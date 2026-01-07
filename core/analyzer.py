"""
Analyzer Agent - Analyzes test results.
"""

from typing import Optional
from core.agent import BaseAgent


class AnalyzerAgent(BaseAgent):
    """Agent that analyzes performance test results."""
    
    def __init__(self):
        super().__init__("Analyzer")
    
    async def execute(self, context: dict) -> dict:
        """
        Analyze test results and identify issues.
        
        Args:
            context: Dict containing:
                - results: Test results from various tools
                - url: Target URL
        
        Returns:
            Dict with analysis and identified issues
        """
        self.start("Analyzing test results")
        
        try:
            results = context.get("results", {})
            url = context.get("url", "")
            
            analysis = self._analyze_results(results)
            
            self.complete(analysis)
            return analysis
            
        except Exception as e:
            self.fail(str(e))
            return {"error": str(e)}
    
    def _analyze_results(self, results: dict) -> dict:
        """Analyze results and identify issues."""
        
        analysis = {
            "issues": [],
            "warnings": [],
            "passed": [],
            "overall_score": 0,
        }
        
        scores = []
        
        # Analyze PageSpeed results
        if "pagespeed" in results and "error" not in results["pagespeed"]:
            ps = results["pagespeed"]
            
            if "scores" in ps:
                for metric, score in ps["scores"].items():
                    scores.append(score)
                    
                    if score < 50:
                        analysis["issues"].append({
                            "severity": "high",
                            "category": "performance",
                            "metric": metric,
                            "score": score,
                            "message": f"{metric} score is poor ({score:.0f}/100)",
                        })
                    elif score < 90:
                        analysis["warnings"].append({
                            "severity": "medium",
                            "category": "performance",
                            "metric": metric,
                            "score": score,
                            "message": f"{metric} needs improvement ({score:.0f}/100)",
                        })
                    else:
                        analysis["passed"].append({
                            "category": "performance",
                            "metric": metric,
                            "score": score,
                            "message": f"{metric} is good ({score:.0f}/100)",
                        })
        
        # Analyze SEO results
        if "seo" in results and "error" not in results["seo"]:
            seo = results["seo"]
            
            if not seo.get("title"):
                analysis["issues"].append({
                    "severity": "high",
                    "category": "seo",
                    "message": "Missing page title",
                })
            
            if not seo.get("meta_description"):
                analysis["issues"].append({
                    "severity": "medium",
                    "category": "seo",
                    "message": "Missing meta description",
                })
            
            if not seo.get("https"):
                analysis["issues"].append({
                    "severity": "high",
                    "category": "security",
                    "message": "HTTPS not enabled",
                })
            
            images = seo.get("images", {})
            if images.get("missing_alt", 0) > 0:
                analysis["warnings"].append({
                    "severity": "medium",
                    "category": "accessibility",
                    "message": f"{images['missing_alt']} images missing alt text",
                })
        
        # Analyze load test results
        if "loadtest" in results and "error" not in results["loadtest"]:
            lt = results["loadtest"]
            
            avg_rt = lt.get("avg_response_time", 0)
            success_rate = lt.get("success_rate", 100)
            
            if avg_rt > 1000:
                analysis["issues"].append({
                    "severity": "high",
                    "category": "performance",
                    "message": f"Slow response time: {avg_rt:.0f}ms average",
                })
            elif avg_rt > 500:
                analysis["warnings"].append({
                    "severity": "medium",
                    "category": "performance",
                    "message": f"Response time could be improved: {avg_rt:.0f}ms average",
                })
            
            if success_rate < 99:
                analysis["issues"].append({
                    "severity": "high",
                    "category": "reliability",
                    "message": f"High error rate: {100 - success_rate:.1f}% failures",
                })
        
        # Calculate overall score
        if scores:
            analysis["overall_score"] = sum(scores) / len(scores)
        
        # Sort issues by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        analysis["issues"].sort(key=lambda x: severity_order.get(x.get("severity", "low"), 2))
        analysis["warnings"].sort(key=lambda x: severity_order.get(x.get("severity", "low"), 2))
        
        return analysis
