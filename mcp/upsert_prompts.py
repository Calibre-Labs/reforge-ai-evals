#!/usr/bin/env python3
"""
Push the market-map prompt variants to Braintrust, mirroring v1's
model/params/user-message so changes vs. v1 are isolated to the system prompt.

Usage:
  export BRAINTRUST_API_KEY=...
  uv run --with 'braintrust-api' python mcp/upsert_prompts.py
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

# v1 (slug: marketmapv1-cc46) is the baseline and is NOT re-uploaded by this
# script. It lives as the untouched original in Braintrust.
VARIANTS = [
    {
        "name": "Market Map v2",
        "slug": "market-map-v2",
        "alias": "market_map_v2",
        "file": "prompts/market-map-prompt-v2.md",
        "description": "v2: v1 + metric-scoping rule + 2 new examples (historical, ambiguous).",
    },
    {
        "name": "Market Map v3",
        "slug": "market-map-v3",
        "alias": "market_map_v3",
        "file": "prompts/market-map-prompt-v3.md",
        "description": "v3: v2 + division/product-line ranking example (workplace messaging).",
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

    print("\nnames.json → prompts:")
    print("\n".join(slug_lines))


if __name__ == "__main__":
    main()
