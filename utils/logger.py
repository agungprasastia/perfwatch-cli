"""
Perfwatch Logger - Rich-based logging utilities.
"""

import logging
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table


console = Console()


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging with Rich handler."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    
    return logging.getLogger("perfwatch")


def print_header(title: str, subtitle: Optional[str] = None):
    """Print a styled header."""
    content = f"[bold cyan]{title}[/bold cyan]"
    if subtitle:
        content += f"\n[dim]{subtitle}[/dim]"
    
    console.print()
    console.print(Panel.fit(content, border_style="cyan"))
    console.print()


def print_success(message: str):
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print an error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_step(step: int, total: int, message: str):
    """Print a step indicator."""
    console.print(f"[dim][{step}/{total}][/dim] {message}")


def create_progress() -> Progress:
    """Create a Rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )


def print_score_table(scores: dict[str, float], title: str = "Performance Scores"):
    """Print a table of scores with color coding."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Rating", justify="center")
    
    for metric, score in scores.items():
        # Color code based on score
        if score >= 90:
            color = "green"
            rating = "🟢 Good"
        elif score >= 50:
            color = "yellow"
            rating = "🟡 Needs Improvement"
        else:
            color = "red"
            rating = "🔴 Poor"
        
        table.add_row(
            metric,
            f"[{color}]{score:.0f}[/{color}]",
            rating
        )
    
    console.print()
    console.print(table)
    console.print()


def print_metrics_table(metrics: dict[str, str], title: str = "Metrics"):
    """Print a table of metrics."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    for metric, value in metrics.items():
        table.add_row(metric, str(value))
    
    console.print()
    console.print(table)
    console.print()


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime for display."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
