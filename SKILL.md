---
name: model-lookup
description: >
  Verify and resolve LLM model IDs to their latest, valid versions.
  Use when writing code that calls LLM APIs (Gemini, OpenAI, Anthropic, DeepSeek, etc.),
  when you encounter a model ID in code, or when you need to know the current model ID
  for any LLM provider.
allowed-tools: Bash(python3 *)
---

# Model Lookup

When writing or editing code that references LLM model IDs, **always verify the model ID is current** by running the lookup script. Model IDs change frequently — models get deprecated, renamed, or replaced without warning.

## How to Use

The lookup script is at `scripts/lookup.py` inside this skill's directory. Find it and run:

```bash
# If installed in the project repo:
python3 .claude/skills/model-lookup/scripts/lookup.py <search terms>

# If installed globally:
python3 ~/.claude/skills/model-lookup/scripts/lookup.py <search terms>
```

Examples:
```bash
python3 <path-to-skill>/scripts/lookup.py gemini flash
python3 <path-to-skill>/scripts/lookup.py claude sonnet
python3 <path-to-skill>/scripts/lookup.py gpt-4o
python3 <path-to-skill>/scripts/lookup.py deepseek chat
python3 <path-to-skill>/scripts/lookup.py --list google
python3 <path-to-skill>/scripts/lookup.py --list anthropic
```

The script queries OpenRouter's live model catalog (free, no API key needed) and returns matches with:
- **Native ID**: The correct model ID for the provider's own API (use this in code)
- **OpenRouter ID**: The OpenRouter-formatted ID (use only if routing through OpenRouter)
- Context window, pricing, capabilities

## Rules

1. **Always verify before using a model ID.** Never trust a model ID from your training data — it may be deprecated. Run the lookup.
2. **Use the Native ID** in code unless the project explicitly uses OpenRouter as a proxy.
3. **Pick the top result** unless the code specifically references an older version for a reason.
4. If a model ID in existing code doesn't appear in the results, it's likely deprecated. Look up the replacement and flag it.

## Provider ID Formats

The script handles translation automatically. For reference:

| Provider | OpenRouter Format | Native API Format |
|---|---|---|
| Google | `google/gemini-2.5-flash` | `gemini-2.5-flash` |
| OpenAI | `openai/gpt-4o` | `gpt-4o` |
| Anthropic | `anthropic/claude-sonnet-4.6` | `claude-sonnet-4-6` |
| DeepSeek | `deepseek/deepseek-chat` | `deepseek-chat` |

Note: Anthropic uses dashes where OpenRouter uses dots (4.6 vs 4-6).
