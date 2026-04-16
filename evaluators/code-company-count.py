"""
Scorer: company_count
Type: code-based
Checks that exactly 3 ranked companies appear in the output.
Returns 1.0 if exactly 3 found, 0.5 if 2 found, 0.0 otherwise.
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
    # Match bold/heading ranked entries: "1. **Company**" or "| 1 | Company"
    numbered = re.findall(r'(?:^|\n)\s*[1-3][\.\)]\s+\*{1,2}[A-Z]', output, re.MULTILINE)
    if len(numbered) == 3:
        return 1.0

    # Markdown table rows with a rank column: "| 1 |" or "| #1 |"
    table_ranks = re.findall(r'^\|\s*#?[123]\s*\|', output, re.MULTILINE)
    if len(table_ranks) == 3:
        return 1.0

    # Looser: any "1.", "2.", "3." on their own lines (numbered list)
    list_items = re.findall(r'(?:^|\n)\s*[123]\.\s+\S', output, re.MULTILINE)
    if len(list_items) >= 3:
        return 1.0 if len(list_items) == 3 else 0.5

    return 0.0
