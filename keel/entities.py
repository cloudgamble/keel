"""Entity extraction and tracking for Keel."""

import json
from datetime import datetime
from typing import Any

from keel.config import CONTEXT_DIR
from keel.llm import chat
from keel.prompts import ENTITY_EXTRACTION_PROMPT

ENTITIES_FILE = CONTEXT_DIR / "entities.json"


def extract_entities(conversation: str, config: dict[str, Any]) -> dict:
    """Extract entities from a conversation using LLM."""
    messages = [
        {"role": "system", "content": ENTITY_EXTRACTION_PROMPT},
        {"role": "user", "content": conversation},
    ]

    try:
        response = chat(messages, config, stream=False)

        # Parse JSON from response
        # Handle potential markdown code blocks
        text = response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])

        return json.loads(text)
    except (json.JSONDecodeError, Exception):
        return {"people": [], "things": [], "patterns": []}


def load_entities() -> dict:
    """Load existing entities from file."""
    if not ENTITIES_FILE.exists():
        return {"people": [], "things": [], "patterns": []}

    try:
        with open(ENTITIES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"people": [], "things": [], "patterns": []}


def save_entities(entities: dict) -> None:
    """Save entities to file."""
    with open(ENTITIES_FILE, "w") as f:
        json.dump(entities, f, indent=2)


def merge_entities(new_entities: dict) -> None:
    """Merge new entities with existing ones."""
    existing = load_entities()
    timestamp = datetime.now().isoformat()

    # Merge people
    existing_people_names = {p["name"].lower() for p in existing.get("people", [])}
    for person in new_entities.get("people", []):
        if person["name"].lower() not in existing_people_names:
            person["first_seen"] = timestamp
            person["last_seen"] = timestamp
            person["mentions"] = 1
            existing.setdefault("people", []).append(person)
        else:
            # Update existing
            for p in existing["people"]:
                if p["name"].lower() == person["name"].lower():
                    p["last_seen"] = timestamp
                    p["mentions"] = p.get("mentions", 1) + 1
                    if person.get("context"):
                        p["context"] = person["context"]
                    break

    # Merge things
    existing_thing_names = {t["name"].lower() for t in existing.get("things", [])}
    for thing in new_entities.get("things", []):
        if thing["name"].lower() not in existing_thing_names:
            thing["first_seen"] = timestamp
            thing["last_seen"] = timestamp
            thing["mentions"] = 1
            existing.setdefault("things", []).append(thing)
        else:
            # Update existing
            for t in existing["things"]:
                if t["name"].lower() == thing["name"].lower():
                    t["last_seen"] = timestamp
                    t["mentions"] = t.get("mentions", 1) + 1
                    if thing.get("context"):
                        t["context"] = thing["context"]
                    break

    # Add new patterns (don't dedupe, they're observations)
    for pattern in new_entities.get("patterns", []):
        pattern["observed"] = timestamp
        existing.setdefault("patterns", []).append(pattern)

    # Keep patterns list manageable (last 20)
    existing["patterns"] = existing.get("patterns", [])[-20:]

    save_entities(existing)


def update_after_conversation(user_input: str, response: str, config: dict[str, Any]) -> None:
    """Extract and merge entities after a conversation."""
    conversation = f"User: {user_input}\n\nAssistant: {response}"

    new_entities = extract_entities(conversation, config)
    merge_entities(new_entities)
