"""
Planner Agent - Plans performance testing strategy.
"""

from typing import Optional
from core.agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Agent that plans the performance testing strategy."""
    
    def __init__(self):
        super().__init__("Planner")
    
    async def execute(self, context: dict) -> dict:
        """
        Plan the performance testing strategy based on context.
        
        Args:
            context: Dict containing:
                - url: Target URL
                - test_type: Type of test (audit, lighthouse, loadtest, seo)
                - options: Additional options
        
        Returns:
            Dict with execution plan
        """
        self.start("Planning performance test strategy")
        
        try:
            url = context.get("url", "")
            test_type = context.get("test_type", "audit")
            options = context.get("options", {})
            
            # Create execution plan
            plan = self._create_plan(url, test_type, options)
            
            self.complete(plan)
            return plan
            
        except Exception as e:
            self.fail(str(e))
            return {"error": str(e)}
    
    def _create_plan(self, url: str, test_type: str, options: dict) -> dict:
        """Create execution plan based on test type."""
        
        base_plan = {
            "url": url,
            "test_type": test_type,
            "steps": [],
        }
        
        if test_type == "audit":
            base_plan["steps"] = [
                {"tool": "pagespeed", "priority": 1, "description": "Run PageSpeed analysis"},
                {"tool": "seo", "priority": 2, "description": "Run SEO analysis"},
                {"tool": "loadtest", "priority": 3, "description": "Run quick load test"},
                {"tool": "ai_analysis", "priority": 4, "description": "Generate AI recommendations"},
            ]
        
        elif test_type == "lighthouse":
            base_plan["steps"] = [
                {"tool": "pagespeed", "priority": 1, "description": "Run Lighthouse via PageSpeed API"},
            ]
            base_plan["options"] = {
                "categories": options.get("categories", ["performance", "accessibility", "best-practices", "seo"]),
                "device": options.get("device", "mobile"),
            }
        
        elif test_type == "loadtest":
            base_plan["steps"] = [
                {"tool": "loadtest", "priority": 1, "description": "Run load test"},
            ]
            base_plan["options"] = {
                "requests": options.get("requests", 100),
                "concurrent": options.get("concurrent", 10),
                "timeout": options.get("timeout", 30),
            }
        
        elif test_type == "seo":
            base_plan["steps"] = [
                {"tool": "seo", "priority": 1, "description": "Run SEO analysis"},
            ]
        
        return base_plan
