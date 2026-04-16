"""
Scorer: ranking_quality_judge
Type: LLM judge
Are the top 3 companies the right ones, in the right order?
Most useful on well-scoped queries where ground truth is knowable.
"""
from typing import Any
import anthropic
import json
import re


PROMPT = """\
You are evaluating whether an AI market research assistant correctly identified and ranked the top 3 players in a market.

## Evaluation Criterion
**Ranking Quality**: Are the 3 companies the most defensible choices for this market, ranked in the correct order based on: revenue > valuation > customer count > ratings/reviews?

## Scoring
- **PASS**: The top 3 companies are plausible, well-known leaders in the market. The ranking order is consistent with the metrics cited (revenue-first priority). Minor debatable placements are acceptable if the metrics support them.
- **FAIL**: A significant/obvious market leader is missing from the top 3, OR the ranking order directly contradicts the metrics cited (e.g., company ranked #1 has lower revenue than company ranked #2), OR the companies listed are mid-market players when dominant leaders exist.

## Few-Shot Examples

### Example 1 — PASS
Input: "CRM software"
Output excerpt: "**Category**: CRM Software | Rank | Company | Revenue | Customers | | 1 | Salesforce | $34.9B FY2024 | 150,000+ | | 2 | Microsoft Dynamics | ~$5B est. FY2024 | 40,000+ | | 3 | HubSpot | $2.17B FY2024 | 200,000+ |"
Result: {"reason": "Top 3 are the correct players. Salesforce's dominance is well-established. The Microsoft vs HubSpot order is correctly based on revenue despite HubSpot having more customers, consistent with the ranking criteria.", "score": "PASS"}

### Example 2 — FAIL
Input: "video conferencing software"
Output excerpt: "| 1 | Google Meet | 3B+ total meeting participants (Google Workspace) | | 2 | Microsoft Teams | 320M MAU | | 3 | Zoom | $4.7B FY2025 revenue · 300M daily meeting participants |"
Result: {"reason": "Zoom is ranked #3 despite having $4.7B in standalone revenue — the highest among pure-play video conferencing companies. Google Meet has no disclosed standalone revenue and is bundled with Workspace. By the revenue-first criterion, Zoom should be #1, not #3.", "score": "FAIL"}

### Example 3 — FAIL
Input: "business intelligence tools"
Output excerpt: "| 1 | Domo | $340M ARR · 30,000+ customers | | 2 | Sisense | ~$100M est. revenue | | 3 | Qlik | ~$800M est. revenue |"
Result: {"reason": "All three dominant BI players — Microsoft Power BI (100M+ users, ~$3B+ est.), Tableau ($1.4B standalone revenue), and Looker (Google Cloud) — are absent from the output. Domo, Sisense, and Qlik are mid-market vendors. This output reflects a long tail of the market, not the leaders.", "score": "FAIL"}

---

Now evaluate:

Input: {input}
Output: {output}

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
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": PROMPT.format(input=input, output=output)}]
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
