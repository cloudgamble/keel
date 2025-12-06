"""LLM integration via LiteLLM."""

from typing import Any, Generator

import litellm
from rich.console import Console

from keel.config import get_api_key

console = Console()

# Suppress LiteLLM's verbose logging
litellm.suppress_debug_info = True


def get_model_string(config: dict[str, Any]) -> str:
    """Get the full model string for LiteLLM based on provider."""
    provider = config.get("provider", "anthropic")
    model = config.get("model", "claude-sonnet-4-5-20250929")

    # LiteLLM expects specific prefixes for some providers
    prefixes = {
        "anthropic": "",  # No prefix needed
        "openai": "",
        "google": "gemini/",
        "vertex": "vertex_ai/",
        "bedrock": "bedrock/",
    }

    prefix = prefixes.get(provider, "")

    # If model already has a prefix, don't add another
    if "/" in model:
        return model

    return f"{prefix}{model}" if prefix else model


def chat(
    messages: list[dict[str, str]],
    config: dict[str, Any],
    stream: bool = True,
) -> str | Generator[str, None, None]:
    """Send messages to the LLM and get a response."""
    api_key = get_api_key(config)
    if not api_key:
        raise ValueError(
            f"No API key found. Set {config['provider'].upper()}_API_KEY "
            "environment variable or add api_key to ~/.keel/config.yaml"
        )

    model = get_model_string(config)

    try:
        if stream:
            return _stream_response(messages, model, api_key)
        else:
            response = litellm.completion(
                model=model,
                messages=messages,
                api_key=api_key,
            )
            return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"LLM error: {e}") from e


def _stream_response(
    messages: list[dict[str, str]],
    model: str,
    api_key: str,
) -> Generator[str, None, None]:
    """Stream response from LLM."""
    response = litellm.completion(
        model=model,
        messages=messages,
        api_key=api_key,
        stream=True,
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def count_tokens(text: str, model: str = "claude-sonnet-4-5-20250929") -> int:
    """Count tokens in text using tiktoken."""
    try:
        import tiktoken

        # Use cl100k_base as a reasonable approximation for most models
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Fallback: rough estimate of 4 chars per token
        return len(text) // 4
