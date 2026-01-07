"""
Report Command - Generate and manage reports.
"""

import json
from datetime import datetime
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from utils.logger import print_header, print_success, print_error

app = typer.Typer(help="Generate and manage reports")
console = Console()


@app.command("list")
def list_reports(
    directory: str = typer.Option("reports", "--dir", "-d", help="Reports directory"),
):
    """List all available reports."""
    
    reports_dir = Path(directory)
    
    if not reports_dir.exists():
        print_error(f"Reports directory not found: {reports_dir}")
        raise typer.Exit(1)
    
    # Find all report files
    reports = list(reports_dir.glob("*.json")) + list(reports_dir.glob("*.html"))
    
    if not reports:
        console.print("[dim]No reports found.[/dim]")
        return
    
    table = Table(title="Available Reports", show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan")
    table.add_column("Type")
    table.add_column("Size", justify="right")
    table.add_column("Modified")
    
    for report in sorted(reports, key=lambda x: x.stat().st_mtime, reverse=True):
        stat = report.stat()
        size = f"{stat.st_size / 1024:.1f} KB"
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        
        # Determine type from filename
        if "audit" in report.name:
            report_type = "Full Audit"
        elif "lighthouse" in report.name:
            report_type = "Lighthouse"
        elif "loadtest" in report.name:
            report_type = "Load Test"
        elif "seo" in report.name:
            report_type = "SEO"
        else:
            report_type = "Unknown"
        
        table.add_row(report.name, report_type, size, modified)
    
    console.print()
    console.print(table)
    console.print()


@app.command("show")
def show_report(
    filename: str = typer.Argument(..., help="Report filename"),
    directory: str = typer.Option("reports", "--dir", "-d", help="Reports directory"),
):
    """Display a report in the console."""
    
    report_path = Path(directory) / filename
    
    if not report_path.exists():
        print_error(f"Report not found: {report_path}")
        raise typer.Exit(1)
    
    if report_path.suffix == ".json":
        with open(report_path) as f:
            data = json.load(f)
        
        console.print()
        console.print_json(data=data)
        console.print()
    
    elif report_path.suffix == ".html":
        console.print(f"[dim]HTML report saved at: {report_path.absolute()}[/dim]")
        console.print("[dim]Open in browser to view.[/dim]")
    
    else:
        console.print(report_path.read_text())


@app.command("export")
def export_report(
    source: str = typer.Argument(..., help="Source report filename (JSON)"),
    format: str = typer.Option("html", "--format", "-f", help="Export format: html, md"),
    directory: str = typer.Option("reports", "--dir", "-d", help="Reports directory"),
):
    """Export a JSON report to another format."""
    
    source_path = Path(directory) / source
    
    if not source_path.exists():
        print_error(f"Source report not found: {source_path}")
        raise typer.Exit(1)
    
    if source_path.suffix != ".json":
        print_error("Source must be a JSON file")
        raise typer.Exit(1)
    
    with open(source_path) as f:
        data = json.load(f)
    
    # Generate output filename
    output_name = source_path.stem + f".{format}"
    output_path = Path(directory) / output_name
    
    if format == "html":
        html = _generate_html(data)
        output_path.write_text(html)
    elif format == "md":
        md = _generate_markdown(data)
        output_path.write_text(md)
    else:
        print_error(f"Unsupported format: {format}")
        raise typer.Exit(1)
    
    print_success(f"Exported to: {output_path}")


@app.command("clean")
def clean_reports(
    directory: str = typer.Option("reports", "--dir", "-d", help="Reports directory"),
    days: int = typer.Option(7, "--days", help="Delete reports older than N days"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Clean up old reports."""
    
    from rich.prompt import Confirm
    
    reports_dir = Path(directory)
    
    if not reports_dir.exists():
        print_error(f"Reports directory not found: {reports_dir}")
        raise typer.Exit(1)
    
    # Find old reports
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    old_reports = []
    
    for report in reports_dir.glob("*"):
        if report.is_file() and report.stat().st_mtime < cutoff:
            old_reports.append(report)
    
    if not old_reports:
        console.print("[dim]No old reports found.[/dim]")
        return
    
    console.print(f"[yellow]Found {len(old_reports)} reports older than {days} days[/yellow]")
    
    if not force:
        if not Confirm.ask("Delete these reports?"):
            console.print("[dim]Cancelled.[/dim]")
            return
    
    for report in old_reports:
        report.unlink()
    
    print_success(f"Deleted {len(old_reports)} reports")


def _generate_html(data: dict) -> str:
    """Generate HTML from report data."""
    url = data.get("url", "Unknown")
    session = data.get("session_id", "Unknown")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perfwatch Report</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #1a1a2e; color: #eee; padding: 2rem; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; }}
        pre {{ background: #16213e; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Perfwatch Report</h1>
        <p>URL: {url} | Session: {session}</p>
        <pre>{json.dumps(data, indent=2)}</pre>
    </div>
</body>
</html>"""


def _generate_markdown(data: dict) -> str:
    """Generate Markdown from report data."""
    url = data.get("url", "Unknown")
    session = data.get("session_id", "Unknown")
    
    return f"""# Perfwatch Report

**URL:** {url}  
**Session:** {session}

## Results

```json
{json.dumps(data, indent=2)}
```
"""
