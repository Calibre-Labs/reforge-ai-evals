"""
Scorer: metric_scope_judge
Type: LLM judge
Are metrics scoped to the relevant product/division, not the parent company?
Catches the pattern where e.g. Microsoft's $245B total revenue is cited for a Teams query.
"""
from typing import Any
from openai import OpenAI
import json
import re


PROMPT = """\
You are evaluating whether a market research response uses appropriately scoped metrics for each company it ranks.

## Criterion
**Metric Scope**: When a ranked company's relevant product is a division or product line (not the whole company), do the cited metrics reflect that division — not the parent company's total revenue or valuation? If exact division revenue is unavailable, an estimate or analyst figure is expected. Stating that standalone revenue "isn't publicly disclosed" without providing an estimate is not sufficient.

## Scoring
- **PASS**: Metrics are scoped to the relevant product or division, OR the company's entire business is the product (no scoping needed).
- **FAIL**: Metrics cited are the parent company's total figures when only one product line is relevant, OR the response acknowledges a division figure is unavailable but makes no attempt to estimate it.

## Examples

### Example 1 — PASS
Input: "enterprise video conferencing software"
Output excerpt: "1. Zoom — $4.7B FY2025 revenue · 300M daily participants. 2. Microsoft Teams — ~$10B est. annual revenue (analyst estimate, part of Microsoft 365). 3. Google Meet — ~$2B est. (bundled with Workspace; Google does not disclose standalone figures)."
Result: {"reason": "Zoom is a pure-play product — total revenue is correct. Teams and Google Meet are divisions, but the response provides analyst estimates scoped to those products rather than citing Microsoft's $245B or Alphabet's $350B totals.", "score": "PASS"}

### Example 2 — FAIL
Input: "enterprise video conferencing software"
Output excerpt: "1. Microsoft Teams — Microsoft total revenue $245B FY2024. 2. Zoom — $4.7B FY2025 revenue. 3. Google Meet — Alphabet total revenue $350B FY2024."
Result: {"reason": "Microsoft Teams and Google Meet are single product lines within much larger companies. Citing Microsoft's $245B and Alphabet's $350B total revenues as metrics for their video conferencing products is misleading — these figures include cloud, search, hardware, and dozens of other businesses.", "score": "FAIL"}

### Example 3 — FAIL
Input: "project management software"
Output excerpt: "1. Asana — $723M FY2024 revenue. 2. Monday.com — $966M FY2024 revenue. 3. Atlassian — $4.4B total revenue (Jira is one of several products; standalone Jira revenue not publicly disclosed)."
Result: {"reason": "Atlassian correctly notes Jira is one of several products, but then cites total company revenue and offers no estimate of Jira's standalone contribution. An analyst estimate or breakdown was available and expected.", "score": "FAIL"}

---

Input: {input}
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
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        max_tokens=512,
        messages=[{"role": "user", "content": PROMPT.format(input=input, output=output)}]
    )
    text = response.choices[0].message.content.strip()
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
