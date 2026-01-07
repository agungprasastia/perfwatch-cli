"""
SEO Tool - SEO analysis.
"""

import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Optional


class SEOTool:
    """SEO analysis tool."""
    
    def __init__(self):
        pass
    
    async def analyze(self, url: str) -> dict:
        """
        Analyze SEO aspects of a webpage.
        
        Args:
            url: The URL to analyze
        
        Returns:
            Dict with SEO analysis results
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        result = {
            "url": url,
            "https": parsed_url.scheme == "https",
        }
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # Fetch main page
            response = await client.get(url)
            html = response.text
            
            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract meta information
            result.update(self._extract_meta(soup))
            
            # Extract headings
            result["headings"] = self._extract_headings(soup)
            
            # Extract images
            result["images"] = self._extract_images(soup)
            
            # Extract links
            result["links"] = self._extract_links(soup, base_url)
            
            # Check robots.txt
            result["robots_txt"] = await self._check_robots(client, base_url)
            
            # Check sitemap
            result["sitemap"] = await self._check_sitemap(client, base_url)
        
        return result
    
    def _extract_meta(self, soup: BeautifulSoup) -> dict:
        """Extract meta tags."""
        result = {}
        
        # Title
        title_tag = soup.find("title")
        result["title"] = title_tag.get_text().strip() if title_tag else ""
        
        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        result["meta_description"] = meta_desc.get("content", "").strip() if meta_desc else ""
        
        # Canonical
        canonical = soup.find("link", rel="canonical")
        result["canonical"] = canonical.get("href", "") if canonical else ""
        
        # Viewport
        viewport = soup.find("meta", attrs={"name": "viewport"})
        result["has_viewport"] = viewport is not None
        
        # Language
        html_tag = soup.find("html")
        result["language"] = html_tag.get("lang", "") if html_tag else ""
        
        # Open Graph
        og_tags = {}
        for og in soup.find_all("meta", property=lambda x: x and x.startswith("og:")):
            prop = og.get("property", "").replace("og:", "")
            og_tags[prop] = og.get("content", "")
        result["open_graph"] = og_tags
        
        # Twitter Cards
        twitter_tags = {}
        for tw in soup.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")}):
            prop = tw.get("name", "").replace("twitter:", "")
            twitter_tags[prop] = tw.get("content", "")
        result["twitter_cards"] = twitter_tags
        
        return result
    
    def _extract_headings(self, soup: BeautifulSoup) -> dict:
        """Extract heading structure."""
        headings = {}
        
        for level in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            tags = soup.find_all(level)
            headings[level] = [tag.get_text().strip() for tag in tags]
        
        return headings
    
    def _extract_images(self, soup: BeautifulSoup) -> dict:
        """Extract image information."""
        images = soup.find_all("img")
        
        total = len(images)
        missing_alt = 0
        missing_src = 0
        
        for img in images:
            if not img.get("alt"):
                missing_alt += 1
            if not img.get("src"):
                missing_src += 1
        
        return {
            "total": total,
            "missing_alt": missing_alt,
            "missing_src": missing_src,
        }
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> dict:
        """Extract link information."""
        links = soup.find_all("a", href=True)
        
        internal = 0
        external = 0
        nofollow = 0
        
        parsed_base = urlparse(base_url)
        
        for link in links:
            href = link.get("href", "")
            
            # Skip anchors and javascript
            if href.startswith("#") or href.startswith("javascript:"):
                continue
            
            # Make absolute
            absolute_url = urljoin(base_url, href)
            parsed_link = urlparse(absolute_url)
            
            if parsed_link.netloc == parsed_base.netloc:
                internal += 1
            else:
                external += 1
            
            # Check nofollow
            rel = link.get("rel", [])
            if "nofollow" in rel:
                nofollow += 1
        
        return {
            "internal": internal,
            "external": external,
            "nofollow": nofollow,
            "total": internal + external,
        }
    
    async def _check_robots(self, client: httpx.AsyncClient, base_url: str) -> bool:
        """Check if robots.txt exists."""
        try:
            response = await client.get(f"{base_url}/robots.txt")
            return response.status_code == 200 and len(response.text) > 0
        except:
            return False
    
    async def _check_sitemap(self, client: httpx.AsyncClient, base_url: str) -> bool:
        """Check if sitemap exists."""
        sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/sitemap.xml.gz",
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = await client.get(sitemap_url)
                if response.status_code == 200:
                    return True
            except:
                continue
        
        # Also check robots.txt for sitemap directive
        try:
            response = await client.get(f"{base_url}/robots.txt")
            if response.status_code == 200 and "sitemap:" in response.text.lower():
                return True
        except:
            pass
        
        return False
