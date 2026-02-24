# Model Lookup

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that verifies and resolves LLM model IDs to their latest, valid versions.

Coding agents have knowledge cutoffs. Model IDs change constantly — Gemini models get deprecated, new ones launch, IDs get renamed. This skill queries [OpenRouter's free model API](https://openrouter.ai/docs/api/api-reference/models/get-models) at runtime so your agent always uses the right model ID.

## Install

Clone the repo and symlink it into your Claude Code skills directory:

```bash
git clone https://github.com/JoeyWangTW/model-lookup.git
ln -s "$(pwd)/model-lookup" ~/.claude/skills/model-lookup
```

That's it. No API keys, no config, no dependencies beyond Python 3.

## How It Works

Once installed, Claude Code auto-activates this skill whenever it detects LLM API work in your code. It instructs the agent to **always verify model IDs** before using them by running the lookup script.

The script queries OpenRouter's `/api/v1/models` endpoint (free, no auth required) and returns:

- **Native ID** — the correct model ID for the provider's own API
- Context window, pricing, and capabilities
- Results cached for 1 hour

## Manual Usage

You can also run the lookup script directly:

```bash
# Search by model family
python3 ~/.claude/skills/model-lookup/scripts/lookup.py gemini flash
python3 ~/.claude/skills/model-lookup/scripts/lookup.py claude sonnet
python3 ~/.claude/skills/model-lookup/scripts/lookup.py gpt-4o
python3 ~/.claude/skills/model-lookup/scripts/lookup.py deepseek chat

# List all models from a provider
python3 ~/.claude/skills/model-lookup/scripts/lookup.py --list google
python3 ~/.claude/skills/model-lookup/scripts/lookup.py --list anthropic
python3 ~/.claude/skills/model-lookup/scripts/lookup.py --list openai
```

Example output:

```
Top matches for 'gemini flash':

[1]   Name:       Google: Gemini 3 Flash Preview
  Native ID:  gemini-3-flash-preview
  OpenRouter: google/gemini-3-flash-preview
  Context:    1,048,576
  Pricing:    $0.0000005/token in, $0.000003/token out
  Inputs:     text, image, file, audio, video
  Features:   tool_use, structured_output, reasoning
```

## Provider ID Translation

The script automatically translates OpenRouter IDs to native provider formats:

| Provider | OpenRouter Format | Native API Format |
|---|---|---|
| Google | `google/gemini-2.5-flash` | `gemini-2.5-flash` |
| OpenAI | `openai/gpt-4o` | `gpt-4o` |
| Anthropic | `anthropic/claude-sonnet-4.6` | `claude-sonnet-4-6` |
| DeepSeek | `deepseek/deepseek-chat` | `deepseek-chat` |

Note: Anthropic uses dashes where OpenRouter uses dots (`4.6` → `4-6`).

## Requirements

- Python 3 (pre-installed on macOS and most Linux)
- Internet connection (to query OpenRouter)
