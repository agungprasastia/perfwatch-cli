"""
Reporter Agent - Generates reports.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from core.agent import BaseAgent


class ReporterAgent(BaseAgent):
    """Agent that generates performance reports."""
    
    def __init__(self):
        super().__init__("Reporter")
    
    async def execute(self, context: dict) -> dict:
        """
        Generate performance report.
        
        Args:
            context: Dict containing:
                - results: Test results
                - analysis: Analysis from AnalyzerAgent
                - format: Report format (html, json, md)
                - output_dir: Output directory
        
        Returns:
            Dict with report path
        """
        self.start("Generating report")
        
        try:
            results = context.get("results", {})
            analysis = context.get("analysis", {})
            format = context.get("format", "html")
            output_dir = Path(context.get("output_dir", "reports"))
            url = context.get("url", "")
            session_id = context.get("session_id", datetime.now().strftime("%Y%m%d_%H%M%S"))
            
            output_dir.mkdir(exist_ok=True)
            
            report_path = self._generate_report(
                results=results,
                analysis=analysis,
                url=url,
                session_id=session_id,
                format=format,
                output_dir=output_dir,
            )
            
            self.complete({"report_path": str(report_path)})
            return {"report_path": str(report_path)}
            
        except Exception as e:
            self.fail(str(e))
            return {"error": str(e)}
    
    def _generate_report(
        self,
        results: dict,
        analysis: dict,
        url: str,
        session_id: str,
        format: str,
        output_dir: Path,
    ) -> Path:
        """Generate report in specified format."""
        
        report_data = {
            "url": url,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "analysis": analysis,
        }
        
        if format == "json":
            filepath = output_dir / f"report_{session_id}.json"
            filepath.write_text(json.dumps(report_data, indent=2, default=str))
        
        elif format == "html":
            filepath = output_dir / f"report_{session_id}.html"
            html = self._generate_html_report(report_data)
            filepath.write_text(html)
        
        elif format == "md":
            filepath = output_dir / f"report_{session_id}.md"
            md = self._generate_markdown_report(report_data)
            filepath.write_text(md)
        
        else:
            filepath = output_dir / f"report_{session_id}.json"
            filepath.write_text(json.dumps(report_data, indent=2, default=str))
        
        return filepath
    
    def _generate_html_report(self, data: dict) -> str:
        """Generate HTML report."""
        
        # Build scores section
        scores_html = ""
        if "pagespeed" in data["results"] and "scores" in data["results"]["pagespeed"]:
            for metric, score in data["results"]["pagespeed"]["scores"].items():
                color = "#22c55e" if score >= 90 else "#eab308" if score >= 50 else "#ef4444"
                scores_html += f"""
                <div class="score-card">
                    <div class="score-value" style="color: {color}">{score:.0f}</div>
                    <div class="score-label">{metric}</div>
                </div>"""
        
        # Build issues section
        issues_html = ""
        analysis = data.get("analysis", {})
        for issue in analysis.get("issues", []):
            severity_color = "#ef4444" if issue.get("severity") == "high" else "#eab308"
            issues_html += f"""
            <div class="issue-item">
                <span class="severity" style="background: {severity_color}">{issue.get('severity', 'unknown').upper()}</span>
                <span>{issue.get('message', '')}</span>
            </div>"""
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perfwatch Report - {data['url']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #22d3ee, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        .meta {{ color: #64748b; font-size: 0.9rem; }}
        .scores-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .score-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .score-value {{
            font-size: 3rem;
            font-weight: bold;
        }}
        .score-label {{
            color: #94a3b8;
            margin-top: 0.5rem;
        }}
        .section {{
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        .section h2 {{
            color: #22d3ee;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }}
        .issue-item {{
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .severity {{
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
        }}
        footer {{
            text-align: center;
            margin-top: 3rem;
            color: #64748b;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Perfwatch Report</h1>
            <p class="meta">{data['url']}</p>
            <p class="meta">Generated: {data['timestamp']}</p>
        </header>
        
        <div class="scores-grid">
            {scores_html if scores_html else '<div class="score-card"><div class="score-value">-</div><div class="score-label">No scores</div></div>'}
        </div>
        
        <div class="section">
            <h2>🔴 Issues Found</h2>
            {issues_html if issues_html else '<p style="color: #22c55e">No critical issues found!</p>'}
        </div>
        
        <footer>
            <p>Generated by Perfwatch CLI v1.0.0</p>
        </footer>
    </div>
</body>
</html>"""
    
    def _generate_markdown_report(self, data: dict) -> str:
        """Generate Markdown report."""
        
        md = f"""# 🚀 Perfwatch Report

**URL:** {data['url']}  
**Session:** {data['session_id']}  
**Date:** {data['timestamp']}

## Performance Scores

"""
        
        if "pagespeed" in data["results"] and "scores" in data["results"]["pagespeed"]:
            for metric, score in data["results"]["pagespeed"]["scores"].items():
                rating = "🟢" if score >= 90 else "🟡" if score >= 50 else "🔴"
                md += f"- **{metric}**: {score:.0f}/100 {rating}\n"
        
        md += "\n## Issues\n\n"
        
        analysis = data.get("analysis", {})
        issues = analysis.get("issues", [])
        
        if issues:
            for issue in issues:
                severity_icon = "🔴" if issue.get("severity") == "high" else "🟡"
                md += f"- {severity_icon} {issue.get('message', '')}\n"
        else:
            md += "✅ No critical issues found!\n"
        
        md += "\n---\n*Generated by Perfwatch CLI v1.0.0*\n"
        
        return md
