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

## Three Modes

Keel has three modes that share the same context:

| Mode | What it does | Prompt |
|------|--------------|--------|
| **keel** | Reflects, stops, no agenda | Blue `>` |
| **engage** | Collaborates - brainstorms, drafts, strategizes | Green `engage>` |
| **push** | Directs - tells you exactly what to do, step by step | Red `push>` |

Switch modes inline:
```
> feeling stuck on promoting my app
[reflects, bullets, stops]

> /engage
Engage mode. Let's work on something.

engage> help me come up with a visibility strategy
[brainstorms, asks questions, explores options]

engage> /push
Push mode. Tell me what to do. I'll break it down.

push> I need to post about keel
Here's what you're doing:
1. Open X
2. Type: "built a CLI for people who are great at work and terrible at their own life"
3. Add the github link in a reply
4. Post it

That's it. Go. Stuck on a step? Ask.
```

- **keel** is the mirror
- **engage** is the collaborator
- **push** is the drill sergeant

Same context, different contract.

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
