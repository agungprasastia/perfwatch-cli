"""
Audit Command - Full website performance audit.
"""

import asyncio
from datetime import datetime
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.validator import validate_url, normalize_url
from utils.logger import print_header, print_success, print_error, print_score_table, format_duration

app = typer.Typer(help="Run full website performance audit")
console = Console()


@app.callback(invoke_without_command=True)
def audit(
    ctx: typer.Context,
    url: str = typer.Option(..., "--url", "-u", help="Target URL to audit"),
    output: str = typer.Option("reports", "--output", "-o", help="Output directory for reports"),
    format: str = typer.Option("html", "--format", "-f", help="Report format: html, json, md"),
    ai: bool = typer.Option(True, "--ai/--no-ai", help="Enable AI-powered recommendations"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run a comprehensive website performance audit.
    
    This command runs all available performance tests:
    - Core Web Vitals (LCP, FID, CLS)
    - Lighthouse Performance Score
    - SEO Analysis
    - Accessibility Check
    - Load Testing
    """
    
    # Validate URL
    is_valid, error = validate_url(url)
    if not is_valid:
        print_error(f"Invalid URL: {error}")
        raise typer.Exit(1)
    
    url = normalize_url(url)
    
    print_header("Perfwatch Full Audit", f"Target: {url}")
    
    # Create session ID
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True)
    
    console.print(f"[dim]Session ID: {session_id}[/dim]")
    console.print()
    
    # Run the audit
    asyncio.run(_run_audit(url, session_id, output_dir, format, ai, verbose))


async def _run_audit(url: str, session_id: str, output_dir: Path, format: str, ai: bool, verbose: bool):
    """Run the full audit asynchronously."""
    
    from tools.pagespeed import PageSpeedTool
    from tools.seo import SEOTool
    from tools.loadtest import LoadTestTool
    
    results = {}
    start_time = datetime.now()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # 1. PageSpeed Analysis
        task1 = progress.add_task("[cyan]Running PageSpeed analysis...", total=None)
        try:
            pagespeed = PageSpeedTool()
            pagespeed_result = await pagespeed.analyze(url)
            results["pagespeed"] = pagespeed_result
            progress.update(task1, description="[green]✓ PageSpeed analysis complete")
        except Exception as e:
            progress.update(task1, description=f"[red]✗ PageSpeed failed: {e}")
            results["pagespeed"] = {"error": str(e)}
        
        # 2. SEO Analysis
        task2 = progress.add_task("[cyan]Running SEO analysis...", total=None)
        try:
            seo = SEOTool()
            seo_result = await seo.analyze(url)
            results["seo"] = seo_result
            progress.update(task2, description="[green]✓ SEO analysis complete")
        except Exception as e:
            progress.update(task2, description=f"[red]✗ SEO failed: {e}")
            results["seo"] = {"error": str(e)}
        
        # 3. Load Test (quick)
        task3 = progress.add_task("[cyan]Running quick load test...", total=None)
        try:
            loadtest = LoadTestTool()
            loadtest_result = await loadtest.run(url, requests=10, concurrent=5)
            results["loadtest"] = loadtest_result
            progress.update(task3, description="[green]✓ Load test complete")
        except Exception as e:
            progress.update(task3, description=f"[red]✗ Load test failed: {e}")
            results["loadtest"] = {"error": str(e)}
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    console.print()
    console.print(f"[dim]Audit completed in {format_duration(duration)}[/dim]")
    console.print()
    
    # Display results
    _display_results(results)
    
    # AI Recommendations
    if ai:
        await _get_ai_recommendations(results, url)
    
    # Save report
    report_file = output_dir / f"audit_{session_id}.{format}"
    _save_report(results, report_file, format, url, session_id)
    
    console.print()
    print_success(f"Report saved to: {report_file}")


def _display_results(results: dict):
    """Display audit results in a formatted table."""
    
    # Performance Scores
    if "pagespeed" in results and "error" not in results["pagespeed"]:
        ps = results["pagespeed"]
        if "scores" in ps:
            print_score_table(ps["scores"], "Performance Scores")
    
    # SEO Summary
    if "seo" in results and "error" not in results["seo"]:
        seo = results["seo"]
        console.print("[bold]SEO Summary[/bold]")
        if "title" in seo:
            console.print(f"  Title: [cyan]{seo.get('title', 'N/A')}[/cyan]")
        if "meta_description" in seo:
            desc = seo.get("meta_description", "N/A")
            if len(desc) > 60:
                desc = desc[:60] + "..."
            console.print(f"  Description: [dim]{desc}[/dim]")
        console.print()
    
    # Load Test Summary
    if "loadtest" in results and "error" not in results["loadtest"]:
        lt = results["loadtest"]
        table = Table(title="Load Test Results", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Avg Response Time", f"{lt.get('avg_response_time', 0):.2f}ms")
        table.add_row("Min Response Time", f"{lt.get('min_response_time', 0):.2f}ms")
        table.add_row("Max Response Time", f"{lt.get('max_response_time', 0):.2f}ms")
        table.add_row("Success Rate", f"{lt.get('success_rate', 0):.1f}%")
        table.add_row("Requests/sec", f"{lt.get('rps', 0):.2f}")
        
        console.print(table)
        console.print()


async def _get_ai_recommendations(results: dict, url: str):
    """Get AI-powered recommendations based on results."""
    
    try:
        from ai.gemini import GeminiClient
        
        console.print("[bold]🤖 AI Recommendations[/bold]")
        console.print("[dim]Analyzing results...[/dim]")
        console.print()
        
        client = GeminiClient()
        recommendations = await client.get_performance_recommendations(results, url)
        
        if recommendations:
            console.print(Panel(
                recommendations,
                title="[bold cyan]Performance Recommendations[/bold cyan]",
                border_style="cyan"
            ))
        else:
            console.print("[yellow]⚠[/yellow] Could not generate AI recommendations")
            
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] AI recommendations unavailable: {e}")


def _save_report(results: dict, filepath: Path, format: str, url: str, session_id: str):
    """Save the audit report to file."""
    import json
    
    report_data = {
        "session_id": session_id,
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    if format == "json":
        filepath.write_text(json.dumps(report_data, indent=2, default=str), encoding="utf-8")
    
    elif format == "html":
        html = _generate_html_report(report_data)
        filepath.write_text(html, encoding="utf-8")
    
    elif format == "md":
        md = _generate_markdown_report(report_data)
        filepath.write_text(md, encoding="utf-8")


def _generate_html_report(data: dict) -> str:
    """Generate HTML report."""
    
    scores_html = ""
    if "pagespeed" in data["results"] and "scores" in data["results"]["pagespeed"]:
        for metric, score in data["results"]["pagespeed"]["scores"].items():
            color = "#22c55e" if score >= 90 else "#eab308" if score >= 50 else "#ef4444"
            scores_html += f'<div class="score-item"><span class="metric">{metric}</span><span class="score" style="color:{color}">{score:.0f}</span></div>'
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perfwatch Report - {data['url']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #22d3ee; margin-bottom: 0.5rem; }}
        .meta {{ color: #64748b; margin-bottom: 2rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
        .card h2 {{ color: #22d3ee; margin-bottom: 1rem; font-size: 1.2rem; }}
        .score-item {{ display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #334155; }}
        .score {{ font-weight: bold; font-size: 1.2rem; }}
        .metric {{ color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Perfwatch Report</h1>
        <p class="meta">URL: {data['url']} | Session: {data['session_id']}</p>
        
        <div class="card">
            <h2>Performance Scores</h2>
            {scores_html if scores_html else '<p>No scores available</p>'}
        </div>
    </div>
</body>
</html>"""


def _generate_markdown_report(data: dict) -> str:
    """Generate Markdown report."""
    
    md = f"""# Perfwatch Report

**URL:** {data['url']}  
**Session:** {data['session_id']}  
**Date:** {data['timestamp']}

## Performance Scores

"""
    
    if "pagespeed" in data["results"] and "scores" in data["results"]["pagespeed"]:
        for metric, score in data["results"]["pagespeed"]["scores"].items():
            rating = "🟢" if score >= 90 else "🟡" if score >= 50 else "🔴"
            md += f"- **{metric}**: {score:.0f} {rating}\n"
    
    return md
