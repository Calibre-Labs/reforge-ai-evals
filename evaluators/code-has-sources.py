"""
Scorer: has_sources
Type: code-based
Checks that the output includes 3–4 source citations.
Accepts URLs, numbered references [1], or a Sources/References section.
Returns 1.0 if ≥3 citations found, 0.5 if 1–2, 0.0 if none.
"""
from typing import Any
import re


async def handler(
    input: Any,
    output: Any,
    expected: Any,
    metadata: dict[str, Any],
    trace: Any,
) -> float | dict[str, Any] | None:
    # Count URLs
    urls = re.findall(r'https?://\S+', output)

    # Count numbered references [1], [2], etc.
    bracketed_refs = re.findall(r'\[\d+\]', output)

    # Count lines in a Sources section (markdown heading + list items)
    sources_section = re.search(
        r'(?:#{1,3}\s*sources?|#{1,3}\s*references?|#{1,3}\s*citations?)(.*?)(?=\n#{1,3}|\Z)',
        output, re.IGNORECASE | re.DOTALL
    )
    section_items = []
    if sources_section:
        section_items = re.findall(r'^\s*[-\d*]+[\.\)]\s+\S', sources_section.group(1), re.MULTILINE)

    total = max(len(urls), len(set(bracketed_refs)), len(section_items))

    if total >= 3:
        return 1.0
    if total >= 1:
        return 0.5
    return 0.0
