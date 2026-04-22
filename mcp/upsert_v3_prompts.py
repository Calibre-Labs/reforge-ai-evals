#!/usr/bin/env python3
"""
One-shot script: push the v3a / v3b / v3c market-map prompts to Braintrust.

Usage:
  export BRAINTRUST_API_KEY=...
  uv run --with 'braintrust-api' python mcp/upsert_v3_prompts.py
"""
import os
import re
from pathlib import Path

from braintrust_api import Braintrust

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ID = "e8f83657-dacc-4437-a8ad-09501bb77646"  # Market_Map project
MODEL = "gpt-5.2-2025-12-11"  # mirror live v1 prompt
PARAMS = {
    "temperature": 0.0,
    "verbosity": "low",
    "reasoning_effort": "medium",
    "use_cache": True,
}

VARIANTS = [
    {
        "name": "Market Map v2",
        "slug": "market-map-v2",
        "alias": "market_map_v2",
        "file": "prompts/market-map-prompt-v2.md",
        "description": "v2: v1 system text + 2 new examples (historical query, ambiguous query).",
    },
    {
        "name": "Market Map v3a (example only)",
        "slug": "market-map-v3a-example-only",
        "alias": "market_map_v3a",
        "file": "prompts/market-map-prompt-v3a-example-only.md",
        "description": "v3a: v2 + new Example 4 (division scoping). No rule changes.",
    },
    {
        "name": "Market Map v3b (rule only)",
        "slug": "market-map-v3b-rule-only",
        "alias": "market_map_v3b",
        "file": "prompts/market-map-prompt-v3b-rule-only.md",
        "description": "v3b: v2 + explicit metric-scoping rule bullet. No new example.",
    },
    {
        "name": "Market Map v3c (both)",
        "slug": "market-map-v3c-both",
        "alias": "market_map_v3c",
        "file": "prompts/market-map-prompt-v3c-both.md",
        "description": "v3c: v2 + both metric-scoping rule and new Example 4.",
    },
]


def extract_system_prompt(md_text: str) -> str:
    idx = md_text.find("## System Prompt")
    if idx == -1:
        raise ValueError("No '## System Prompt' section found in file")
    body = md_text[idx + len("## System Prompt"):].lstrip()
    body = re.sub(r"^---\s*", "", body)
    return body.strip()


def main() -> None:
    if not os.environ.get("BRAINTRUST_API_KEY"):
        raise SystemExit("BRAINTRUST_API_KEY is not set. Export it and re-run.")

    client = Braintrust()
    slug_lines = []

    for v in VARIANTS:
        path = REPO_ROOT / v["file"]
        system_prompt = extract_system_prompt(path.read_text())

        result = client.prompts.replace(
            name=v["name"],
            slug=v["slug"],
            project_id=PROJECT_ID,
            description=v["description"],
            prompt_data={
                "prompt": {
                    "type": "chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "{{input}}"},
                    ],
                },
                "options": {"model": MODEL, "params": PARAMS},
            },
        )
        print(f"  ✓ {v['name']}  →  slug={result.slug}  id={result.id}  ({len(system_prompt)} chars)")
        slug_lines.append(f'    "{v["alias"]}": "{result.slug}",')

    print("\nAdd these lines under names.json → prompts:")
    print("\n".join(slug_lines))


if __name__ == "__main__":
    main()
