"""
Scorer: has_category
Type: code-based
Checks that the output identifies a market category before ranking companies.
Looks for a "Category:" label, a markdown heading, or an opening sentence naming the market.
Returns 1.0 if found, 0.0 otherwise.
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
    # Explicit category label
    if re.search(r'\*{0,2}(?:market\s+)?category\*{0,2}\s*:', output, re.IGNORECASE):
        return 1.0

    # Markdown heading mentioning category/market
    if re.search(r'^#{1,3}\s+.*(?:market|category|industry|sector)', output, re.IGNORECASE | re.MULTILINE):
        return 1.0

    # First 400 chars reference the market being analyzed
    opening = output[:400].lower()
    if any(kw in opening for kw in ['market category', 'this market', 'identifying', 'the market for', 'in the ', 'category:']):
        return 1.0

    return 0.0
