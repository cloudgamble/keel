"""Conversation handling for Keel."""

from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from keel.config import CONVERSATIONS_DIR
from keel.context import build_context, save_conversation
from keel.llm import chat
from keel.prompts import SYSTEM_PROMPT

console = Console()


def get_today_file() -> Path:
    """Get path to today's conversation file."""
    today = datetime.now().strftime("%Y-%m-%d")
    return CONVERSATIONS_DIR / f"{today}.md"


def conversation_loop(config: dict[str, Any]) -> None:
    """Run interactive conversation loop."""
    console.print()
    console.print("[dim]keel[/dim] [bold blue]What's on your mind?[/bold blue]")
    console.print("[dim]Type 'q' to exit[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold blue]>[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Talk later.[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("q", "quit", "exit"):
            console.print("[dim]Talk later.[/dim]")
            break

        response = process_message(user_input, config)
        console.print()

        # Save to today's file
        save_conversation(user_input, response)


def one_shot(message: str, config: dict[str, Any]) -> None:
    """Process a single message and exit."""
    console.print()
    response = process_message(message, config)
    console.print()

    # Save to today's file
    save_conversation(message, response)


def process_message(user_input: str, config: dict[str, Any]) -> str:
    """Process a user message and return the response."""
    # Build context with history
    context = build_context(config)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
        {"role": "user", "content": user_input},
    ]

    # Stream response
    full_response = ""

    try:
        with Live(console=console, refresh_per_second=10) as live:
            for chunk in chat(messages, config, stream=True):
                full_response += chunk
                live.update(Markdown(full_response))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return ""

    return full_response
