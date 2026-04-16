"""
Scorer: has_category
Type: code-based
Checks that the output contains **Market Category** or **Category**.
Returns 1.0 if found, 0.0 otherwise.
"""
from typing import Any


async def handler(
    input: Any,
    output: Any,
    expected: Any,
    metadata: dict[str, Any],
    trace: Any,
) -> float | dict[str, Any] | None:
    text = "" if output is None else str(output)
    if "**Market Category**" in text or "**Category**" in text:
        return 1.0
    return 0.0
