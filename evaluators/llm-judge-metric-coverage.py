"""
Scorer: metric_coverage_judge
Type: LLM judge
Do at least 2 of the 3 ranked companies have at least 2 quantitative metrics each?
Complements the deterministic has_metrics check with semantic understanding of what counts as a metric.
"""
from typing import Any
from openai import OpenAI
import json
import re


PROMPT = """\
You are evaluating whether an AI market research assistant provided sufficient quantitative evidence for the companies it ranked.

## Evaluation Criterion
**Metric Coverage**: Do at least 2 of the 3 ranked companies have at least 2 distinct quantitative data points each? Qualifying metrics include: revenue, ARR, valuation, funding, market share percentage, user/customer count, employee count, growth rate, NPS score, or any other named numeric figure. Qualitative descriptions ("market leader", "widely used") do not count as metrics.

## Scoring
- **PASS**: At least 2 of the 3 companies have 2 or more distinct quantitative metrics cited.
- **FAIL**: Fewer than 2 companies have 2 or more distinct quantitative metrics. This includes outputs where companies are described only qualitatively, or where only 1 metric is given per company across the board.

## Few-Shot Examples

### Example 1 — PASS
Input: "project management software"
Output excerpt: "**Category**: Project Management Software | 1 | Asana | $723M FY2024 revenue · 150,000+ paying customers | 2 | Monday.com | $966M FY2024 revenue · 245,000+ customers · 70% YoY growth (2022) | 3 | Jira/Atlassian | $4.4B FY2024 total revenue |"
Result: {"reason": "Asana has 2 metrics (revenue + customers), Monday.com has 3 metrics (revenue + customers + growth rate). That's 2 of 3 companies meeting the threshold. Atlassian has only 1 metric but that does not prevent a PASS since 2 of 3 companies qualify.", "score": "PASS"}

### Example 2 — FAIL
Input: "email marketing tools"
Output excerpt: "**Category**: Email Marketing Platforms | 1 | Mailchimp (Intuit) — the market leader, trusted by small businesses | 2 | Constant Contact — reliable platform for SMBs with strong customer support | 3 | Klaviyo — the top choice for e-commerce brands |"
Result: {"reason": "None of the three companies have any quantitative data points. All descriptions are qualitative labels. Zero of three companies meet the 2-metric threshold.", "score": "FAIL"}

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
