"""
Scorer: company_match_judge
Type: LLM judge
Do the top 3 companies in the output match the reference in the same order?
Simpler than reference_judge — only checks company identity and rank, not metrics or category.
Requires the dataset to have an 'expected' field populated.
"""
from typing import Any
import anthropic
import json
import re


PROMPT = """\
You are checking whether a market research response names the same top 3 companies as a reference answer, in the same rank order.

## Criterion
**Company Match**: Do the top 3 companies in the output match the top 3 companies in the reference, in the same order (#1 = #1, #2 = #2, #3 = #3)?

Minor name variations are fine (e.g., "Microsoft Dynamics 365" vs "Microsoft Dynamics"). What matters is that the same three companies appear at the same rank positions.

## Scoring
- **PASS**: All 3 companies are present and in the same rank order as the reference.
- **FAIL**: Any company differs, or the order is different (e.g., reference #1 appears as output #2).

## Examples

### Example 1 — PASS
Reference: "#1 Salesforce, #2 Microsoft Dynamics, #3 HubSpot"
Output: "1. Salesforce ($34.9B revenue) 2. Microsoft Dynamics 365 (~$5B est.) 3. HubSpot ($2.17B)"
Result: {"reason": "All three companies match in the correct order. 'Microsoft Dynamics 365' is the same company as 'Microsoft Dynamics'.", "score": "PASS"}

### Example 2 — FAIL
Reference: "#1 Zoom, #2 Microsoft Teams, #3 Google Meet"
Output: "1. Microsoft Teams (320M MAU) 2. Zoom ($4.7B revenue) 3. Google Meet"
Result: {"reason": "Zoom and Microsoft Teams are swapped — Zoom is #1 in the reference but appears as #2 in the output.", "score": "FAIL"}

---

Reference: {expected}
Output: {output}

Respond with JSON only:
{{"reason": "<1-2 sentence explanation>", "score": "PASS" | "FAIL"}}
"""


async def handler(
    input: Any,
    output: Any,
    expected: Any,
    metadata: dict[str, Any],
    trace: Any,
) -> float | dict[str, Any] | None:
    if not expected:
        return None

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": PROMPT.format(expected=expected, output=output)}]
    )
    text = response.content[0].text.strip()
    text = re.sub(r'^```(?:json)?\n?', '', text)
    text = re.sub(r'\n?```$', '', text)

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return {"score": 0.0, "metadata": {"reason": "Failed to parse judge response", "raw": text}}

    return {
        "score": 1.0 if result.get("score") == "PASS" else 0.0,
        "metadata": {"reason": result.get("reason", ""), "label": result.get("score", "FAIL")}
    }
