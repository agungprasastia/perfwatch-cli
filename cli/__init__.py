"""
Perfwatch CLI - Main entry point.
AI-Powered Website Performance Testing Tool.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional

from cli.commands import audit, lighthouse, loadtest, seo, init as init_cmd, report

# Create the main Typer app
app = typer.Typer(
    name="perfwatch",
    help="🚀 AI-Powered Website Performance Testing CLI Tool",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()

# Register sub-commands
app.add_typer(audit.app, name="audit", help="Run full website performance audit")
app.add_typer(lighthouse.app, name="lighthouse", help="Run Lighthouse performance analysis")
app.add_typer(loadtest.app, name="loadtest", help="Run load/stress testing")
app.add_typer(seo.app, name="seo", help="Run SEO analysis")
app.add_typer(init_cmd.app, name="init", help="Initialize Perfwatch configuration")
app.add_typer(report.app, name="report", help="Generate reports from sessions")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """
    🚀 Perfwatch - AI-Powered Website Performance Testing CLI
    
    Use 'perfwatch <command> --help' for more information about a command.
    """
    if version:
        console.print(Panel.fit(
            "[bold green]Perfwatch[/bold green] v1.0.0\n"
            "[dim]AI-Powered Website Performance Testing CLI[/dim]",
            border_style="green"
        ))
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        # Show welcome message if no command provided
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🚀 Perfwatch[/bold cyan]\n\n"
            "[white]AI-Powered Website Performance Testing CLI[/white]\n\n"
            "[dim]Commands:[/dim]\n"
            "  [green]audit[/green]      - Full website performance audit\n"
            "  [green]lighthouse[/green] - Lighthouse performance analysis\n"
            "  [green]loadtest[/green]   - Load/stress testing\n"
            "  [green]seo[/green]        - SEO analysis\n"
            "  [green]init[/green]       - Initialize configuration\n"
            "  [green]report[/green]     - Generate reports\n\n"
            "[dim]Use 'perfwatch <command> --help' for more info[/dim]",
            border_style="cyan",
            title="Welcome",
            title_align="left"
        ))
        console.print()


if __name__ == "__main__":
    app()
