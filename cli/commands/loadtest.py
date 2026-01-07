"""
Load Test Command - HTTP load/stress testing.
"""

import asyncio
from datetime import datetime
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

from utils.validator import validate_url, normalize_url
from utils.logger import print_header, print_success, print_error
from utils.config import config

app = typer.Typer(help="Run load/stress testing")
console = Console()


@app.callback(invoke_without_command=True)
def loadtest(
    ctx: typer.Context,
    url: str = typer.Option(..., "--url", "-u", help="Target URL to test"),
    requests: int = typer.Option(None, "--requests", "-n", help="Total number of requests"),
    concurrent: int = typer.Option(None, "--concurrent", "-c", help="Number of concurrent users"),
    duration: int = typer.Option(None, "--duration", "-d", help="Test duration in seconds (overrides --requests)"),
    timeout: int = typer.Option(None, "--timeout", "-t", help="Request timeout in seconds"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method: GET, POST, etc."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run HTTP load/stress testing.
    
    Measures response times, throughput, and error rates.
    Default values are loaded from config/settings.yaml
    """
    
    # Use config defaults if not specified
    requests = requests or config.get_loadtest_requests()
    concurrent = concurrent or config.get_loadtest_concurrent()
    timeout = timeout or config.get_loadtest_timeout()
    
    # Validate URL
    is_valid, error = validate_url(url)
    if not is_valid:
        print_error(f"Invalid URL: {error}")
        raise typer.Exit(1)
    
    url = normalize_url(url)
    
    print_header("Load Testing", f"Target: {url}")
    
    console.print(f"[dim]Requests: {requests} | Concurrent: {concurrent} | Timeout: {timeout}s[/dim]")
    console.print()
    
    # Run load test
    asyncio.run(_run_loadtest(url, requests, concurrent, duration, timeout, method, verbose))


async def _run_loadtest(
    url: str, 
    total_requests: int, 
    concurrent: int, 
    duration: int,
    timeout: int,
    method: str,
    verbose: bool
):
    """Run the load test."""
    
    from tools.loadtest import LoadTestTool
    
    start_time = datetime.now()
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Running load test...", total=total_requests)
        
        def update_progress(completed: int):
            progress.update(task, completed=completed)
        
        try:
            tool = LoadTestTool()
            result = await tool.run(
                url,
                requests=total_requests,
                concurrent=concurrent,
                timeout=timeout,
                method=method,
                progress_callback=update_progress
            )
            
        except Exception as e:
            print_error(f"Load test failed: {e}")
            return
    
    # Calculate duration
    test_duration = (datetime.now() - start_time).total_seconds()
    
    console.print()
    
    # Display results
    _display_results(result, test_duration)
    
    # Save results
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    import json
    report_file = output_dir / f"loadtest_{session_id}.json"
    result["test_duration"] = test_duration
    report_file.write_text(json.dumps(result, indent=2, default=str))
    
    print_success(f"Report saved to: {report_file}")


def _display_results(result: dict, duration: float):
    """Display load test results."""
    
    # Summary table
    table = Table(title="Load Test Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    # Response times
    avg_rt = result.get("avg_response_time", 0)
    min_rt = result.get("min_response_time", 0)
    max_rt = result.get("max_response_time", 0)
    p95_rt = result.get("p95_response_time", 0)
    p99_rt = result.get("p99_response_time", 0)
    
    # Color code based on response time
    def format_time(ms: float) -> str:
        if ms < 200:
            return f"[green]{ms:.2f}ms[/green]"
        elif ms < 1000:
            return f"[yellow]{ms:.2f}ms[/yellow]"
        else:
            return f"[red]{ms:.2f}ms[/red]"
    
    table.add_row("Total Requests", str(result.get("total_requests", 0)))
    table.add_row("Successful", f"[green]{result.get('successful', 0)}[/green]")
    table.add_row("Failed", f"[red]{result.get('failed', 0)}[/red]")
    table.add_row("Success Rate", f"{result.get('success_rate', 0):.1f}%")
    table.add_row("─" * 20, "─" * 15)
    table.add_row("Avg Response Time", format_time(avg_rt))
    table.add_row("Min Response Time", format_time(min_rt))
    table.add_row("Max Response Time", format_time(max_rt))
    table.add_row("P95 Response Time", format_time(p95_rt))
    table.add_row("P99 Response Time", format_time(p99_rt))
    table.add_row("─" * 20, "─" * 15)
    table.add_row("Requests/sec", f"[bold]{result.get('rps', 0):.2f}[/bold]")
    table.add_row("Test Duration", f"{duration:.2f}s")
    
    console.print(table)
    console.print()
    
    # Status code distribution
    if "status_codes" in result and result["status_codes"]:
        console.print("[bold]Status Code Distribution[/bold]")
        for code, count in sorted(result["status_codes"].items()):
            color = "green" if str(code).startswith("2") else "yellow" if str(code).startswith("3") else "red"
            bar_len = min(count, 50)
            bar = "█" * bar_len
            console.print(f"  [{color}]{code}[/{color}] {bar} {count}")
        console.print()
    
    # Performance rating
    if avg_rt < 200:
        rating = "[green]Excellent[/green] 🚀"
    elif avg_rt < 500:
        rating = "[green]Good[/green] ✓"
    elif avg_rt < 1000:
        rating = "[yellow]Fair[/yellow] ⚠"
    else:
        rating = "[red]Poor[/red] ✗"
    
    console.print(f"[bold]Performance Rating:[/bold] {rating}")
    console.print()
