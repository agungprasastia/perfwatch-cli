"""
Lighthouse Command - Lighthouse performance analysis.
"""

import asyncio
from datetime import datetime
from pathlib import Path
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.validator import validate_url, normalize_url
from utils.logger import print_header, print_success, print_error, print_score_table

app = typer.Typer(help="Run Lighthouse performance analysis")
console = Console()


@app.callback(invoke_without_command=True)
def lighthouse(
    ctx: typer.Context,
    url: str = typer.Option(..., "--url", "-u", help="Target URL to analyze"),
    categories: str = typer.Option(
        "performance,accessibility,best-practices,seo",
        "--categories", "-c",
        help="Comma-separated categories to test"
    ),
    device: str = typer.Option("mobile", "--device", "-d", help="Device type: mobile or desktop"),
    output: str = typer.Option("reports", "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run Lighthouse performance analysis via PageSpeed Insights API.
    
    Categories: performance, accessibility, best-practices, seo, pwa
    """
    
    # Validate URL
    is_valid, error = validate_url(url)
    if not is_valid:
        print_error(f"Invalid URL: {error}")
        raise typer.Exit(1)
    
    url = normalize_url(url)
    category_list = [c.strip() for c in categories.split(",")]
    
    print_header("Lighthouse Analysis", f"Target: {url}")
    console.print(f"[dim]Device: {device} | Categories: {', '.join(category_list)}[/dim]")
    console.print()
    
    asyncio.run(_run_lighthouse(url, category_list, device, output, verbose))


async def _run_lighthouse(url: str, categories: list, device: str, output: str, verbose: bool):
    """Run Lighthouse analysis."""
    
    from tools.pagespeed import PageSpeedTool
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Running Lighthouse via PageSpeed API...", total=None)
        
        try:
            tool = PageSpeedTool()
            result = await tool.analyze(
                url, 
                strategy="mobile" if device == "mobile" else "desktop",
                categories=categories
            )
            
            if "error" in result:
                progress.update(task, description=f"[red]✗ {result['error']}")
                print_error(result['error'])
                return
            
            progress.update(task, description="[green]✓ Analysis complete")
            
        except Exception as e:
            progress.update(task, description=f"[red]✗ Analysis failed: {e}")
            print_error(str(e))
            return
    
    console.print()
    
    # Display scores
    if "scores" in result:
        print_score_table(result["scores"], "Lighthouse Scores")
    
    # Display Core Web Vitals
    if "web_vitals" in result:
        vitals = result["web_vitals"]
        console.print("[bold]Core Web Vitals[/bold]")
        
        for metric, data in vitals.items():
            value = data.get("displayValue", "N/A")
            score = (data.get("score", 0) or 0) * 100
            
            if score >= 90:
                color = "green"
                icon = "🟢"
            elif score >= 50:
                color = "yellow"
                icon = "🟡"
            else:
                color = "red"
                icon = "🔴"
            
            console.print(f"  {icon} [{color}]{metric}[/{color}]: {value}")
        
        console.print()
    
    # Display opportunities
    if "opportunities" in result and result["opportunities"]:
        console.print("[bold]Optimization Opportunities[/bold]")
        for opp in result["opportunities"][:5]:
            savings = opp.get("savings", "")
            console.print(f"  [yellow]→[/yellow] {opp['title']}")
            if savings:
                console.print(f"    [dim]Potential savings: {savings}[/dim]")
        console.print()
    
    # Save results
    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    import json
    report_file = output_dir / f"lighthouse_{session_id}.json"
    report_file.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    
    print_success(f"Report saved to: {report_file}")


