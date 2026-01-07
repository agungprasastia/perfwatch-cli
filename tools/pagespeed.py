"""
PageSpeed Tool - Google PageSpeed Insights API integration.
"""

import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class PageSpeedTool:
    """Google PageSpeed Insights API wrapper."""
    
    API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    def __init__(self, api_key: Optional[str] = None):
        # Only use PAGESPEED_API_KEY, not GOOGLE_API_KEY (Gemini key doesn't work for PageSpeed)
        self.api_key = api_key or os.getenv("PAGESPEED_API_KEY")
    
    async def analyze(
        self, 
        url: str, 
        strategy: str = "mobile",
        categories: Optional[list] = None
    ) -> dict:
        """
        Analyze a URL using PageSpeed Insights API.
        
        Args:
            url: The URL to analyze
            strategy: 'mobile' or 'desktop'
            categories: List of categories to analyze
                       (performance, accessibility, best-practices, seo, pwa)
        
        Returns:
            Dict with scores, web vitals, and opportunities
        """
        if categories is None:
            categories = ["performance", "accessibility", "best-practices", "seo"]
        
        # Build URL with multiple category params
        category_params = "&".join([f"category={cat}" for cat in categories])
        request_url = f"{self.API_URL}?url={url}&strategy={strategy}&{category_params}"
        
        # Only add API key if specifically set for PageSpeed
        if self.api_key:
            request_url += f"&key={self.api_key}"
        
        # Make request
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(request_url)
            response.raise_for_status()
            data = response.json()
        
        # Parse response
        return self._parse_response(data)
    
    def _parse_response(self, data: dict) -> dict:
        """Parse PageSpeed API response."""
        
        result = {
            "url": data.get("id", ""),
            "fetch_time": data.get("analysisUTCTimestamp", ""),
        }
        
        # Extract scores
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        
        result["scores"] = {}
        for cat_id, cat_data in categories.items():
            # Convert to display name
            display_name = cat_id.replace("-", " ").title()
            score = (cat_data.get("score", 0) or 0) * 100
            result["scores"][display_name] = score
        
        # Extract Core Web Vitals
        audits = lighthouse.get("audits", {})
        result["web_vitals"] = {}
        
        vitals_map = {
            "largest-contentful-paint": "LCP",
            "first-input-delay": "FID",
            "cumulative-layout-shift": "CLS",
            "first-contentful-paint": "FCP",
            "speed-index": "Speed Index",
            "total-blocking-time": "TBT",
            "interactive": "Time to Interactive",
        }
        
        for audit_id, display_name in vitals_map.items():
            if audit_id in audits:
                audit = audits[audit_id]
                result["web_vitals"][display_name] = {
                    "score": audit.get("score", 0),
                    "displayValue": audit.get("displayValue", "N/A"),
                    "numericValue": audit.get("numericValue", 0),
                }
        
        # Extract opportunities
        result["opportunities"] = []
        
        opportunity_audits = [
            "render-blocking-resources",
            "unused-css-rules",
            "unused-javascript",
            "modern-image-formats",
            "uses-optimized-images",
            "uses-responsive-images",
            "efficient-animated-content",
            "uses-text-compression",
            "uses-rel-preconnect",
            "server-response-time",
            "redirects",
            "uses-rel-preload",
            "offscreen-images",
        ]
        
        for audit_id in opportunity_audits:
            if audit_id in audits:
                audit = audits[audit_id]
                if audit.get("score", 1) < 1:  # Not perfect score
                    opportunity = {
                        "id": audit_id,
                        "title": audit.get("title", audit_id),
                        "description": audit.get("description", ""),
                    }
                    
                    # Get potential savings
                    details = audit.get("details", {})
                    if "overallSavingsMs" in details:
                        opportunity["savings"] = f"{details['overallSavingsMs']:.0f}ms"
                    elif "overallSavingsBytes" in details:
                        kb = details["overallSavingsBytes"] / 1024
                        opportunity["savings"] = f"{kb:.1f} KB"
                    
                    result["opportunities"].append(opportunity)
        
        # Sort opportunities by potential savings
        result["opportunities"].sort(
            key=lambda x: float(x.get("savings", "0").replace("ms", "").replace(" KB", "").replace(",", "") or 0),
            reverse=True
        )
        
        return result
