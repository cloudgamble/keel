# Keel

*The hidden structure that keeps you upright.*

A quiet accountability mirror. Like having a friend with a good memory who listens, reflects back what they hear, and never nags.

## What It Does

- **Listens** - Dump your thoughts, stream of consciousness
- **Reflects** - "What I'm hearing: you mentioned Marcus, bass keeps coming up..."
- **Remembers** - Builds context over time, surfaces patterns naturally
- **Stops** - No suggestions, no coaching, no "would you like me to..."

## Install

```bash
# Clone and install
git clone https://github.com/cloudgamble/keel
cd keel
pip install -e .
```

Coming soon: `pip install keel-cli` and `brew install cloudgamble/tap/keel`

## Setup

Set your API key:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

Or configure directly:

```bash
keel --config
```

## Usage

```bash
# Start a conversation
keel

# Quick thought (one-shot)
keel "been meaning to call marcus, also feeling scattered today"

# Weekly reflection
keel --week

# See available models
keel --models

# Fresh start
keel --forget
```

## How It Works

Keel saves conversations to `~/.keel/conversations/` as daily markdown files. It builds invisible context about people, things, and patterns you mention - but never shows you a list or dashboard.

When you talk to Keel, it:
1. Reflects back what it hears (2-4 bullets)
2. Occasionally surfaces patterns ("Bass keeps coming up...")
3. Ends the conversation. No follow-ups.

## Configuration

Edit `~/.keel/config.yaml`:

```yaml
provider: anthropic
model: claude-sonnet-4-5-20250929
api_key: ${ANTHROPIC_API_KEY}
timezone: America/New_York
context_limit: 4000
```

## Supported Providers

Default is Anthropic (Claude Sonnet 4.5). PRs welcome for others:

- `anthropic` - Claude models
- `openai` - GPT models  
- `google` - Gemini models
- `bedrock` - AWS Bedrock
- `vertex` - Google Vertex AI

## Philosophy

Most productivity tools add to your cognitive load. Another list to manage, another inbox to check, another thing to feel guilty about.

Keel is different:
- **No lists** - It tracks things invisibly
- **No streaks** - Breaking a streak shouldn't feel bad
- **No gamification** - You're not a lab rat
- **No engagement loops** - It respects your exit

You talk when you want. It listens, reflects, and shuts up.

## License

MIT
