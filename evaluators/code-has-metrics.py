"""
Scorer: has_metrics
Type: code-based
Checks that companies are backed by at least 2 data points each (≥6 total).
Looks for: $ figures, B/M/K suffixes, percentages, customer/user counts.
Returns 1.0 if ≥6 metrics, 0.5 if 3–5, 0.0 if <3.
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
    # Dollar figures: $34.9B, $2.1M, $500K
    dollar_figures = re.findall(r'\$[\d,\.]+\s*[BMKbmk]?\b', output)

    # Standalone number + B/M/K (revenue shorthand): 34.9B, 150M
    shorthand = re.findall(r'\b\d+(?:\.\d+)?\s*[BMKbmk]\b', output)

    # Percentages
    percentages = re.findall(r'\b\d+(?:\.\d+)?%', output)

    # Customer/user/employee counts
    counts = re.findall(r'\b\d[\d,]+\s*(?:customers?|users?|employees?|clients?|subscribers?)\b', output, re.IGNORECASE)

    total = len(set(dollar_figures)) + len(set(shorthand)) + len(set(percentages)) + len(set(counts))

    if total >= 6:
        return 1.0
    if total >= 3:
        return 0.5
    return 0.0
