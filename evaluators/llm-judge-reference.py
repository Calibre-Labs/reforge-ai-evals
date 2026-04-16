"""
Scorer: reference_judge
Type: LLM judge
Compares output to a gold-standard reference answer.
Checks: same top 3 companies, same market category, comparable metrics.
Requires the dataset to have an 'expected' field populated.
"""
from typing import Any
import anthropic
import json
import re


PROMPT = """\
You are evaluating an AI market research assistant's response by comparing it to a gold-standard reference answer.

## Evaluation Criterion
**Reference Alignment**: Does the output cover the same key companies, metrics, and market category as the reference answer? The output does NOT need to be identical — different phrasing, ordering of sections, or additional context is fine. What matters is: (a) the same top 3 companies, (b) the same market category identified, and (c) comparable supporting metrics (same order of magnitude, same companies ranked in the same order).

## Scoring
- **PASS**: Same top 3 companies in the same rank order, same market category, metrics are in the same order of magnitude.
- **FAIL**: Different companies in the top 3, wrong market category identified, rank order differs from the reference, or metrics differ by more than 50% without explanation.

## Few-Shot Examples

### Example 1 — PASS
Reference: "Category: CRM Software. #1 Salesforce ($34.9B), #2 Microsoft Dynamics (~$5B), #3 HubSpot ($2.17B)"
Output: "Market: Customer Relationship Management. Top players: 1. Salesforce — $35B revenue FY2024, 150K customers. 2. Microsoft Dynamics 365 — ~$5B est. 3. HubSpot — $2.2B FY2024, 200K+ customers."
Result: {"reason": "Same top 3 companies, same rank order, metrics agree within rounding. Minor phrasing differences don't affect accuracy.", "score": "PASS"}

### Example 2 — FAIL
Reference: "Category: Video Conferencing Software. #1 Zoom ($4.7B FY2025 revenue, 300M daily participants), #2 Microsoft Teams (320M MAU), #3 Google Meet (Workspace bundle)"
Output: "Category: Video Conferencing. #1 Google Meet (largest meeting participants across Workspace) · #2 Microsoft Teams (320M MAU) · #3 Zoom ($4.7B revenue)"
Result: {"reason": "Google Meet is not the reference #1 — Zoom is. The output ranks Zoom last despite citing its $4.7B standalone revenue, which is the highest in the category. The rank order is inverted from the reference on the most important criterion.", "score": "FAIL"}

### Example 3 — FAIL
Reference: "Category: Business Intelligence Tools. #1 Microsoft Power BI (100M+ users, ~$3B est. revenue via M365), #2 Tableau ($1.4B est. standalone revenue), #3 Looker/Google (~$500M est.)"
Output: "Category: BI and Analytics. #1 Tableau ($1.4B revenue, 42,000+ customers) · #2 Microsoft Power BI (100M+ users, bundled with Microsoft 365) · #3 Looker ($500M est.)"
Result: {"reason": "All three companies are present but Tableau and Power BI are swapped — the reference ranks Power BI #1, the output ranks Tableau #1. Rank order is part of the evaluation criterion; a #1/#2 swap is a meaningful disagreement with the reference, not a rounding difference.", "score": "FAIL"}

---

Now evaluate:

Input: {input}
Reference answer: {expected}
Model output: {output}

Respond with JSON only:
{{"reason": "<2-3 sentence explanation>", "score": "PASS" | "FAIL"}}
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
        messages=[{"role": "user", "content": PROMPT.format(input=input, expected=expected, output=output)}]
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
