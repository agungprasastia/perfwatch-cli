"""
SEO Command - SEO analysis.
"""

import asyncio
from datetime import datetime
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils.validator import validate_url, normalize_url
from utils.logger import print_header, print_success, print_error, print_warning

app = typer.Typer(help="Run SEO analysis")
console = Console()


@app.callback(invoke_without_command=True)
def seo(
    ctx: typer.Context,
    url: str = typer.Option(..., "--url", "-u", help="Target URL to analyze"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run SEO analysis on a webpage.
    
    Checks: meta tags, headings, images, links, robots.txt, sitemap
    """
    
    # Validate URL
    is_valid, error = validate_url(url)
    if not is_valid:
        print_error(f"Invalid URL: {error}")
        raise typer.Exit(1)
    
    url = normalize_url(url)
    
    print_header("SEO Analysis", f"Target: {url}")
    
    # Run analysis
    asyncio.run(_run_seo(url, verbose))


async def _run_seo(url: str, verbose: bool):
    """Run SEO analysis."""
    
    from tools.seo import SEOTool
    
    console.print("[dim]Analyzing webpage...[/dim]")
    console.print()
    
    try:
        tool = SEOTool()
        result = await tool.analyze(url)
    except Exception as e:
        print_error(f"SEO analysis failed: {e}")
        return
    
    # Display results
    _display_results(result, verbose)
    
    # Calculate and display score
    score = _calculate_seo_score(result)
    _display_score(score)
    
    # Save results
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    import json
    report_file = output_dir / f"seo_{session_id}.json"
    result["score"] = score
    report_file.write_text(json.dumps(result, indent=2, default=str))
    
    print_success(f"Report saved to: {report_file}")


def _display_results(result: dict, verbose: bool):
    """Display SEO analysis results."""
    
    # Meta Information
    console.print("[bold cyan]📝 Meta Information[/bold cyan]")
    console.print()
    
    # Title
    title = result.get("title", "")
    title_len = len(title)
    if title:
        if 30 <= title_len <= 60:
            console.print(f"  [green]✓[/green] Title: {title}")
            console.print(f"    [dim]Length: {title_len} chars (optimal: 30-60)[/dim]")
        else:
            console.print(f"  [yellow]⚠[/yellow] Title: {title}")
            console.print(f"    [yellow]Length: {title_len} chars (optimal: 30-60)[/yellow]")
    else:
        console.print("  [red]✗[/red] Title: [red]Missing![/red]")
    
    # Meta Description
    desc = result.get("meta_description", "")
    desc_len = len(desc)
    if desc:
        if 120 <= desc_len <= 160:
            console.print(f"  [green]✓[/green] Meta Description: {desc[:80]}...")
            console.print(f"    [dim]Length: {desc_len} chars (optimal: 120-160)[/dim]")
        else:
            console.print(f"  [yellow]⚠[/yellow] Meta Description: {desc[:80]}...")
            console.print(f"    [yellow]Length: {desc_len} chars (optimal: 120-160)[/yellow]")
    else:
        console.print("  [red]✗[/red] Meta Description: [red]Missing![/red]")
    
    # Canonical
    canonical = result.get("canonical", "")
    if canonical:
        console.print(f"  [green]✓[/green] Canonical URL: {canonical}")
    else:
        console.print("  [yellow]⚠[/yellow] Canonical URL: Not set")
    
    console.print()
    
    # Headings
    console.print("[bold cyan]📑 Heading Structure[/bold cyan]")
    console.print()
    
    headings = result.get("headings", {})
    h1_count = len(headings.get("h1", []))
    
    if h1_count == 1:
        console.print(f"  [green]✓[/green] H1: {headings['h1'][0][:60]}...")
    elif h1_count == 0:
        console.print("  [red]✗[/red] H1: [red]Missing![/red]")
    else:
        console.print(f"  [yellow]⚠[/yellow] H1: {h1_count} found (should be 1)")
    
    for level in ["h2", "h3", "h4"]:
        count = len(headings.get(level, []))
        if count > 0:
            console.print(f"  [dim]{level.upper()}: {count} found[/dim]")
    
    console.print()
    
    # Images
    console.print("[bold cyan]🖼️ Images[/bold cyan]")
    console.print()
    
    images = result.get("images", {})
    total_images = images.get("total", 0)
    missing_alt = images.get("missing_alt", 0)
    
    console.print(f"  Total images: {total_images}")
    if missing_alt == 0:
        console.print(f"  [green]✓[/green] All images have alt text")
    else:
        console.print(f"  [red]✗[/red] Missing alt text: {missing_alt} images")
    
    console.print()
    
    # Links
    console.print("[bold cyan]🔗 Links[/bold cyan]")
    console.print()
    
    links = result.get("links", {})
    console.print(f"  Internal links: {links.get('internal', 0)}")
    console.print(f"  External links: {links.get('external', 0)}")
    
    console.print()
    
    # Technical
    console.print("[bold cyan]⚙️ Technical SEO[/bold cyan]")
    console.print()
    
    if result.get("robots_txt"):
        console.print("  [green]✓[/green] robots.txt found")
    else:
        console.print("  [yellow]⚠[/yellow] robots.txt not found")
    
    if result.get("sitemap"):
        console.print("  [green]✓[/green] Sitemap found")
    else:
        console.print("  [yellow]⚠[/yellow] Sitemap not found")
    
    if result.get("https"):
        console.print("  [green]✓[/green] HTTPS enabled")
    else:
        console.print("  [red]✗[/red] HTTPS not enabled")
    
    console.print()


def _calculate_seo_score(result: dict) -> int:
    """Calculate SEO score based on results."""
    score = 0
    max_score = 100
    
    # Title (15 points)
    title = result.get("title", "")
    if title:
        score += 10
        if 30 <= len(title) <= 60:
            score += 5
    
    # Meta description (15 points)
    desc = result.get("meta_description", "")
    if desc:
        score += 10
        if 120 <= len(desc) <= 160:
            score += 5
    
    # Canonical (5 points)
    if result.get("canonical"):
        score += 5
    
    # H1 (15 points)
    h1s = result.get("headings", {}).get("h1", [])
    if len(h1s) == 1:
        score += 15
    elif len(h1s) > 1:
        score += 5
    
    # Images with alt (10 points)
    images = result.get("images", {})
    if images.get("total", 0) > 0:
        if images.get("missing_alt", 0) == 0:
            score += 10
        else:
            alt_ratio = 1 - (images["missing_alt"] / images["total"])
            score += int(10 * alt_ratio)
    else:
        score += 10  # No images is not a penalty
    
    # Robots.txt (10 points)
    if result.get("robots_txt"):
        score += 10
    
    # Sitemap (10 points)
    if result.get("sitemap"):
        score += 10
    
    # HTTPS (20 points)
    if result.get("https"):
        score += 20
    
    return min(score, max_score)


def _display_score(score: int):
    """Display SEO score with visual representation."""
    
    if score >= 90:
        color = "green"
        rating = "Excellent"
        emoji = "🏆"
    elif score >= 70:
        color = "green"
        rating = "Good"
        emoji = "✓"
    elif score >= 50:
        color = "yellow"
        rating = "Needs Improvement"
        emoji = "⚠"
    else:
        color = "red"
        rating = "Poor"
        emoji = "✗"
    
    console.print(Panel.fit(
        f"[bold {color}]{score}/100[/bold {color}] {emoji}\n"
        f"[{color}]{rating}[/{color}]",
        title="[bold]SEO Score[/bold]",
        border_style=color
    ))
    console.print()
