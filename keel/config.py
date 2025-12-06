"""Configuration management for Keel."""

import os
from pathlib import Path
from typing import Any

import yaml

KEEL_DIR = Path.home() / ".keel"
CONFIG_FILE = KEEL_DIR / "config.yaml"
CONTEXT_DIR = KEEL_DIR / "context"
CONVERSATIONS_DIR = KEEL_DIR / "conversations"

DEFAULT_CONFIG = {
    "provider": "anthropic",
    "model": "claude-sonnet-4-5-20250929",
    "api_key": "",
    "timezone": "America/New_York",
    "context_limit": 4000,
}


def ensure_directories() -> None:
    """Create necessary directories if they don't exist."""
    KEEL_DIR.mkdir(exist_ok=True)
    CONTEXT_DIR.mkdir(exist_ok=True)
    CONVERSATIONS_DIR.mkdir(exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load configuration from file, creating defaults if needed."""
    ensure_directories()

    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f) or {}

    # Merge with defaults for any missing keys
    merged = DEFAULT_CONFIG.copy()
    merged.update(config)

    # Expand environment variables in api_key
    if merged["api_key"].startswith("${") and merged["api_key"].endswith("}"):
        env_var = merged["api_key"][2:-1]
        merged["api_key"] = os.environ.get(env_var, "")

    return merged


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_directories()

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_api_key(config: dict[str, Any]) -> str:
    """Get API key from config or environment."""
    api_key = config.get("api_key", "")

    if api_key:
        return api_key

    # Fall back to environment variables based on provider
    provider = config.get("provider", "anthropic")
    env_vars = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "vertex": "GOOGLE_APPLICATION_CREDENTIALS",
        "bedrock": "AWS_ACCESS_KEY_ID",
    }

    env_var = env_vars.get(provider, "")
    return os.environ.get(env_var, "") if env_var else ""
