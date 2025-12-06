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
from keel.entities import update_after_conversation
from keel.llm import chat
from keel.prompts import SYSTEM_PROMPT, ENGAGE_PROMPT

console = Console()


def get_today_file() -> Path:
    """Get path to today's conversation file."""
    today = datetime.now().strftime("%Y-%m-%d")
    return CONVERSATIONS_DIR / f"{today}.md"


def conversation_loop(config: dict[str, Any]) -> None:
    """Run interactive conversation loop."""
    mode = "keel"  # Start in keel mode
    
    console.print()
    console.print("[dim]keel[/dim] [bold blue]What's on your mind?[/bold blue]")
    console.print("[dim]Type 'q' to exit, '/engage' to switch modes[/dim]\n")

    while True:
        prompt_color = "blue" if mode == "keel" else "green"
        prompt_label = ">" if mode == "keel" else "engage>"
        
        try:
            user_input = Prompt.ask(f"[bold {prompt_color}]{prompt_label}[/bold {prompt_color}]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Talk later.[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("q", "quit", "exit"):
            console.print("[dim]Talk later.[/dim]")
            break

        # Mode switching
        if user_input.lower() in ("/engage", "/e"):
            mode = "engage"
            console.print("[green]Engage mode.[/green] [dim]Let's work on something. /keel to switch back.[/dim]\n")
            continue
        
        if user_input.lower() in ("/keel", "/k"):
            mode = "keel"
            console.print("[blue]Keel mode.[/blue] [dim]Listening. /engage to switch.[/dim]\n")
            continue

        response = process_message(user_input, config, mode=mode)
        console.print()

        # Save to today's file
        save_conversation(user_input, response, mode=mode)

        # Extract entities in background (don't block on this)
        try:
            update_after_conversation(user_input, response, config)
        except Exception:
            pass  # Silent fail - entity extraction is nice-to-have


def one_shot(message: str, config: dict[str, Any]) -> None:
    """Process a single message and exit."""
    console.print()
    response = process_message(message, config)
    console.print()

    # Save to today's file
    save_conversation(message, response)

    # Extract entities
    try:
        update_after_conversation(message, response, config)
    except Exception:
        pass


def process_message(user_input: str, config: dict[str, Any], mode: str = "keel") -> str:
    """Process a user message and return the response."""
    # Build context with history
    context = build_context(config)

    # Select prompt based on mode
    system_prompt = SYSTEM_PROMPT if mode == "keel" else ENGAGE_PROMPT

    messages = [
        {"role": "system", "content": system_prompt + "\n\n" + context},
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
