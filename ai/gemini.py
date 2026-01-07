"""
Gemini Client - Google Gemini AI integration.
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Google Gemini AI client for performance analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.client = None
        
        # Load model from config
        from utils.config import config
        self.model_name = config.get_ai_model()
        
        if self.api_key:
            self._initialize()
    
    def _initialize(self):
        """Initialize the Gemini client."""
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError("google-genai package not installed. Run: pip install google-genai")
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini: {e}")
    
    async def get_performance_recommendations(self, results: dict, url: str) -> str:
        """
        Get AI-powered performance recommendations based on test results.
        
        Args:
            results: Dict containing test results (pagespeed, seo, loadtest)
            url: The analyzed URL
        
        Returns:
            String with recommendations
        """
        if not self.client:
            return "AI recommendations unavailable: No API key configured"
        
        prompt = self._build_recommendation_prompt(results, url)
        
        try:
            response = await self._generate_async(prompt)
            return response
        except Exception as e:
            return f"Failed to generate recommendations: {e}"
    
    async def analyze_issues(self, issues: list, context: str = "") -> str:
        """
        Analyze specific performance issues and provide solutions.
        
        Args:
            issues: List of issues/problems detected
            context: Additional context about the website
        
        Returns:
            String with analysis and solutions
        """
        if not self.model:
            return "AI analysis unavailable: No API key configured"
        
        prompt = f"""As a web performance expert, analyze these issues and provide solutions:

Issues:
{json.dumps(issues, indent=2)}

Context: {context if context else "Web performance audit"}

Provide:
1. Priority ranking (which to fix first)
2. Specific solutions for each issue
3. Expected improvement from each fix
4. Code examples where applicable

Be concise and actionable."""
        
        try:
            response = await self._generate_async(prompt)
            return response
        except Exception as e:
            return f"Failed to analyze issues: {e}"
    
    async def _generate_async(self, prompt: str) -> str:
        """Generate response from Gemini (async wrapper)."""
        import asyncio
        
        # Run in executor since the SDK is synchronous
        loop = asyncio.get_event_loop()
        model_name = self.model_name
        client = self.client
        
        def generate():
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        
        response = await loop.run_in_executor(None, generate)
        return response
    
    def _build_recommendation_prompt(self, results: dict, url: str) -> str:
        """Build prompt for performance recommendations."""
        
        # Extract key metrics
        metrics_summary = []
        
        # PageSpeed scores
        if "pagespeed" in results and "scores" in results["pagespeed"]:
            scores = results["pagespeed"]["scores"]
            metrics_summary.append("Performance Scores:")
            for metric, score in scores.items():
                status = "Good" if score >= 90 else "Needs Improvement" if score >= 50 else "Poor"
                metrics_summary.append(f"  - {metric}: {score:.0f} ({status})")
        
        # Web Vitals
        if "pagespeed" in results and "web_vitals" in results["pagespeed"]:
            metrics_summary.append("\nCore Web Vitals:")
            for metric, data in results["pagespeed"]["web_vitals"].items():
                value = data.get("displayValue", "N/A")
                metrics_summary.append(f"  - {metric}: {value}")
        
        # Load Test
        if "loadtest" in results:
            lt = results["loadtest"]
            metrics_summary.append("\nLoad Test Results:")
            metrics_summary.append(f"  - Avg Response Time: {lt.get('avg_response_time', 0):.2f}ms")
            metrics_summary.append(f"  - Success Rate: {lt.get('success_rate', 0):.1f}%")
            metrics_summary.append(f"  - Requests/sec: {lt.get('rps', 0):.2f}")
        
        # SEO
        if "seo" in results:
            seo = results["seo"]
            metrics_summary.append("\nSEO Analysis:")
            metrics_summary.append(f"  - Title: {'✓' if seo.get('title') else '✗ Missing'}")
            metrics_summary.append(f"  - Meta Description: {'✓' if seo.get('meta_description') else '✗ Missing'}")
            metrics_summary.append(f"  - HTTPS: {'✓' if seo.get('https') else '✗ Not enabled'}")
        
        # Build prompt
        prompt = f"""You are a web performance expert. Analyze these website performance results and provide actionable recommendations.

URL: {url}

{chr(10).join(metrics_summary)}

Provide recommendations in this format:
1. **Critical Issues** (fix immediately)
2. **High Priority** (fix soon)
3. **Medium Priority** (nice to have)

For each recommendation:
- Explain what the issue is
- Why it matters
- How to fix it (be specific)
- Expected improvement

Keep it concise but actionable. Use bullet points.
Do NOT use markdown headers beyond what's specified above.
Limit to top 5-7 recommendations."""
        
        return prompt
