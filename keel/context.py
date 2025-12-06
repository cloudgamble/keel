"""Context management for Keel - summary buffer, compression, history."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from keel.config import CONTEXT_DIR, CONVERSATIONS_DIR
from keel.llm import count_tokens

SUMMARY_FILE = CONTEXT_DIR / "summary.md"
ENTITIES_FILE = CONTEXT_DIR / "entities.json"


def build_context(config: dict[str, Any]) -> str:
    """Build context string from entities, summary, and recent conversations."""
    context_limit = config.get("context_limit", 4000)
    parts = []

    # 1. Load entities (always included, should be small)
    entities = load_entities()
    if entities:
        entities_text = format_entities(entities)
        parts.append(f"CONTEXT ABOUT USER:\n{entities_text}")

    # 2. Load rolling summary
    summary = load_summary()
    if summary:
        parts.append(f"PREVIOUS CONTEXT:\n{summary}")

    # 3. Load recent conversations (last 3 days)
    recent = load_recent_conversations(days=3)
    if recent:
        parts.append(f"RECENT CONVERSATIONS:\n{recent}")

    context = "\n\n".join(parts)

    # Check if we're over limit and need to compress
    token_count = count_tokens(context)
    if token_count > context_limit:
        context = compress_context(parts, context_limit, config)

    return context


def load_entities() -> dict:
    """Load entities from JSON file."""
    if not ENTITIES_FILE.exists():
        return {}

    try:
        with open(ENTITIES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def format_entities(entities: dict) -> str:
    """Format entities for inclusion in prompt."""
    lines = []

    people = entities.get("people", [])
    if people:
        lines.append("People mentioned:")
        for p in people[-10:]:  # Last 10 people
            ctx = f" ({p['context']})" if p.get("context") else ""
            lines.append(f"  - {p['name']}{ctx}")

    things = entities.get("things", [])
    if things:
        lines.append("Things/interests:")
        for t in things[-10:]:
            ctx = f" ({t['context']})" if t.get("context") else ""
            lines.append(f"  - {t['name']}{ctx}")

    patterns = entities.get("patterns", [])
    if patterns:
        lines.append("Patterns observed:")
        for p in patterns[-5:]:  # Last 5 patterns
            lines.append(f"  - {p['note']}")

    return "\n".join(lines)


def load_summary() -> str:
    """Load rolling summary from file."""
    if not SUMMARY_FILE.exists():
        return ""

    try:
        return SUMMARY_FILE.read_text().strip()
    except IOError:
        return ""


def save_summary(summary: str) -> None:
    """Save rolling summary to file."""
    SUMMARY_FILE.write_text(summary)


def load_recent_conversations(days: int = 3) -> str:
    """Load recent conversation files."""
    today = datetime.now()
    conversations = []

    for i in range(days):
        date = today - timedelta(days=i)
        file_path = CONVERSATIONS_DIR / f"{date.strftime('%Y-%m-%d')}.md"

        if file_path.exists():
            try:
                content = file_path.read_text().strip()
                if content:
                    conversations.append(f"--- {date.strftime('%A, %B %d')} ---\n{content}")
            except IOError:
                continue

    return "\n\n".join(reversed(conversations))  # Oldest first


def save_conversation(user_input: str, response: str) -> None:
    """Append conversation to today's file."""
    today_file = CONVERSATIONS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"

    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n## {timestamp}\n\n**You:** {user_input}\n\n**Keel:** {response}\n"

    with open(today_file, "a") as f:
        f.write(entry)


def compress_context(parts: list[str], limit: int, config: dict[str, Any]) -> str:
    """Compress context to fit within token limit."""
    from keel.llm import chat
    from keel.prompts import SUMMARY_PROMPT

    # For now, simple strategy: truncate oldest content
    # TODO: Implement proper summarization using LLM

    combined = "\n\n".join(parts)
    tokens = count_tokens(combined)

    if tokens <= limit:
        return combined

    # Simple truncation from the beginning (oldest content)
    # Keep roughly the right proportion
    ratio = limit / tokens
    char_limit = int(len(combined) * ratio * 0.9)  # 90% to be safe

    return "...[earlier context compressed]...\n\n" + combined[-char_limit:]


def get_weekly_summary(config: dict[str, Any]) -> str:
    """Generate a weekly summary of conversations."""
    from keel.llm import chat
    from keel.prompts import WEEKLY_REFLECTION_PROMPT

    # Load last 7 days
    week_content = load_recent_conversations(days=7)

    if not week_content:
        return ""

    messages = [
        {"role": "system", "content": WEEKLY_REFLECTION_PROMPT},
        {"role": "user", "content": week_content},
    ]

    try:
        response = chat(messages, config, stream=False)
        return response
    except Exception:
        return ""
