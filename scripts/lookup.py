#!/usr/bin/env python3
"""Look up current LLM model IDs from OpenRouter's free API.

Usage:
    python3 lookup.py <query>          # Search for models matching query
    python3 lookup.py --list <provider> # List all models from a provider

Examples:
    python3 lookup.py "gemini flash"
    python3 lookup.py "claude sonnet"
    python3 lookup.py "gpt-4o"
    python3 lookup.py --list google
    python3 lookup.py --list anthropic
"""

import json
import os
import sys
import time
import urllib.request

CACHE_PATH = os.path.join(os.path.dirname(__file__), ".models-cache.json")
CACHE_TTL = 3600  # 1 hour
API_URL = "https://openrouter.ai/api/v1/models"

# Providers where we strip the prefix to get the native ID
# Anthropic needs extra handling: dots → dashes in version numbers
PROVIDER_PREFIXES = {
    "google": "google/",
    "openai": "openai/",
    "anthropic": "anthropic/",
    "deepseek": "deepseek/",
    "meta-llama": "meta-llama/",
    "mistralai": "mistralai/",
    "cohere": "cohere/",
    "qwen": "qwen/",
    "x-ai": "x-ai/",
}


def fetch_models():
    """Fetch model list from OpenRouter, with 1-hour cache."""
    if os.path.exists(CACHE_PATH):
        age = time.time() - os.path.getmtime(CACHE_PATH)
        if age < CACHE_TTL:
            with open(CACHE_PATH) as f:
                return json.load(f)

    req = urllib.request.Request(API_URL, headers={"User-Agent": "model-lookup/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())

    with open(CACHE_PATH, "w") as f:
        json.dump(data["data"], f)

    return data["data"]


def to_native_id(openrouter_id):
    """Convert OpenRouter ID to native provider API format.

    google/gemini-2.5-flash → gemini-2.5-flash
    openai/gpt-4o → gpt-4o
    anthropic/claude-sonnet-4.6 → claude-sonnet-4-6
    """
    provider, _, model_part = openrouter_id.partition("/")

    if provider == "anthropic":
        # Anthropic native API uses dashes not dots in version numbers
        # claude-sonnet-4.6 → claude-sonnet-4-6
        # claude-3.5-sonnet → claude-3-5-sonnet
        import re
        model_part = re.sub(r"(\d+)\.(\d+)", r"\1-\2", model_part)
        # Strip :thinking suffix if present (that's an OpenRouter-only variant)
        model_part = model_part.split(":")[0]

    return model_part


def score_match(query_terms, model):
    """Score how well a model matches the search query."""
    model_id = model["id"].lower()
    model_name = model.get("name", "").lower()
    text = f"{model_id} {model_name}"

    score = 0
    for term in query_terms:
        term = term.lower()
        if term in model_id:
            score += 10
        if term in model_name:
            score += 5

    # Boost newer models (higher created timestamp)
    created = model.get("created", 0)
    if created:
        score += created / 1e12  # Small boost for recency

    # Penalize free-tier duplicates
    if ":free" in model_id:
        score -= 3

    return score


def format_model(model):
    """Format a model for display."""
    oid = model["id"]
    native = to_native_id(oid)
    name = model.get("name", "")
    ctx = model.get("context_length", "?")
    pricing = model.get("pricing", {})
    prompt_price = pricing.get("prompt", "?")
    completion_price = pricing.get("completion", "?")

    lines = []
    lines.append(f"  Name:       {name}")
    lines.append(f"  Native ID:  {native}")
    lines.append(f"  OpenRouter: {oid}")
    lines.append(f"  Context:    {ctx:,}" if isinstance(ctx, int) else f"  Context:    {ctx}")
    lines.append(f"  Pricing:    ${prompt_price}/token in, ${completion_price}/token out")

    # Capabilities
    arch = model.get("architecture", {})
    input_mods = arch.get("input_modalities", [])
    if input_mods:
        lines.append(f"  Inputs:     {', '.join(input_mods)}")

    # Supported features
    params = model.get("supported_parameters", [])
    features = []
    if "tools" in params:
        features.append("tool_use")
    if "response_format" in params or "structured_outputs" in params:
        features.append("structured_output")
    if "include_reasoning" in params or "reasoning" in params:
        features.append("reasoning")
    if features:
        lines.append(f"  Features:   {', '.join(features)}")

    return "\n".join(lines)


def search(query_terms, models):
    """Search models and return top matches."""
    scored = [(score_match(query_terms, m), m) for m in models]
    scored = [(s, m) for s, m in scored if s > 0]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:8]]


def list_provider(provider, models):
    """List all models from a specific provider."""
    prefix = PROVIDER_PREFIXES.get(provider, f"{provider}/")
    return [m for m in models if m["id"].startswith(prefix)]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 lookup.py <query>")
        print("       python3 lookup.py --list <provider>")
        sys.exit(1)

    models = fetch_models()

    if sys.argv[1] == "--list":
        provider = sys.argv[2] if len(sys.argv) > 2 else "google"
        results = list_provider(provider, models)
        if not results:
            print(f"No models found for provider: {provider}")
            sys.exit(1)
        print(f"Models from {provider} ({len(results)} total):\n")
        for m in results:
            native = to_native_id(m["id"])
            print(f"  {native}  ({m.get('name', '')})")
        return

    query_terms = sys.argv[1:]
    results = search(query_terms, models)

    if not results:
        print(f"No models found matching: {' '.join(query_terms)}")
        sys.exit(1)

    print(f"Top matches for '{' '.join(query_terms)}':\n")
    for i, m in enumerate(results):
        print(f"[{i+1}] {format_model(m)}")
        print()


if __name__ == "__main__":
    main()
