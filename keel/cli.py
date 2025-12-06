"""Keel CLI - The hidden structure that keeps you upright."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from keel import __version__
from keel.config import CONFIG_FILE, load_config, save_config, DEFAULT_CONFIG
from keel.chat import conversation_loop, one_shot

app = typer.Typer(
    name="keel",
    help="The hidden structure that keeps you upright.",
    no_args_is_help=False,
    add_completion=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    message: Optional[str] = typer.Argument(None, help="Quick thought to process"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """Start a conversation or process a quick thought."""
    if version:
        console.print(f"[dim]keel[/dim] [bold]{__version__}[/bold]")
        raise typer.Exit()

    if ctx.invoked_subcommand is not None:
        return

    config = load_config()

    # Check for API key
    from keel.config import get_api_key
    if not get_api_key(config):
        console.print(
            Panel(
                "[yellow]No API key configured.[/yellow]\n\n"
                f"Set [bold]ANTHROPIC_API_KEY[/bold] environment variable, or run:\n"
                f"  [dim]keel --config[/dim]",
                title="Setup Required",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    if message:
        # One-shot mode: process single thought and exit
        one_shot(message, config)
    else:
        # Interactive conversation mode
        conversation_loop(config)


@app.command()
def week():
    """Show weekly reflection of what came up."""
    from keel.context import get_weekly_summary

    config = load_config()
    summary = get_weekly_summary(config)

    if summary:
        console.print()
        console.print(Panel(Markdown(summary), title="This Week", border_style="blue"))
    else:
        console.print("[dim]No conversations this week yet.[/dim]")


@app.command()
def models():
    """List available models for current provider."""
    config = load_config()
    provider = config.get("provider", "anthropic")
    current_model = config.get("model", "")

    console.print(f"\n[bold]Provider:[/bold] {provider}")
    console.print(f"[bold]Current model:[/bold] {current_model}\n")

    # Show recommended models by provider
    recommendations = {
        "anthropic": [
            ("claude-sonnet-4-5-20250929", "Best balance (recommended)"),
            ("claude-opus-4-5-20251124", "Premium, most capable"),
            ("claude-3-5-haiku-20241022", "Fast and cheap"),
        ],
        "google": [
            ("gemini-3-pro", "Latest, advanced reasoning"),
            ("gemini-2.5-pro", "Solid performer"),
        ],
        "openai": [
            ("gpt-4.5", "Current production"),
            ("gpt-4o", "Fast, multimodal"),
            ("gpt-4o-mini", "Cheap, good enough"),
        ],
    }

    if provider in recommendations:
        console.print("[dim]Recommended models:[/dim]")
        for model, desc in recommendations[provider]:
            marker = "[green]>[/green] " if model == current_model else "  "
            console.print(f"  {marker}[bold]{model}[/bold] - {desc}")
    else:
        console.print(f"[dim]Configure model in ~/.keel/config.yaml[/dim]")

    console.print()


@app.command()
def config():
    """Open configuration in editor."""
    config_data = load_config()

    # Ensure config file exists with current values
    if not CONFIG_FILE.exists():
        save_config(config_data)

    console.print(f"[dim]Opening {CONFIG_FILE}[/dim]\n")

    # Try to open in user's preferred editor
    editor = None
    for ed in ["$EDITOR", "code", "vim", "nano"]:
        if ed == "$EDITOR":
            import os
            editor = os.environ.get("EDITOR")
        else:
            editor = ed

        if editor:
            try:
                subprocess.run([editor, str(CONFIG_FILE)], check=True)
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

    if not editor:
        console.print(f"[yellow]Edit manually:[/yellow] {CONFIG_FILE}")


@app.command()
def forget():
    """Clear context and start fresh."""
    from keel.config import CONTEXT_DIR

    confirm = Prompt.ask(
        "[yellow]This will clear your conversation history and context. Continue?[/yellow]",
        choices=["y", "n"],
        default="n",
    )

    if confirm == "y":
        # Clear context files
        summary_file = CONTEXT_DIR / "summary.md"
        entities_file = CONTEXT_DIR / "entities.json"

        if summary_file.exists():
            summary_file.unlink()
        if entities_file.exists():
            entities_file.unlink()

        console.print("[dim]Context cleared. Fresh start.[/dim]")
    else:
        console.print("[dim]Cancelled.[/dim]")


if __name__ == "__main__":
    app()
