"""
Scorer: edge_case_handling_judge
Type: LLM judge
For vague/out-of-scope/speculative queries, did the agent handle ambiguity gracefully?
Auto-passes for clear, well-scoped queries.
"""
from typing import Any
from openai import OpenAI
import json
import re


PROMPT = """\
You are evaluating whether an AI market research assistant handled a vague, ambiguous, or out-of-scope query appropriately.

## Evaluation Criterion
**Edge Case Handling**: For queries where a definitive ranking is impossible or requires major assumptions (vague category, abstract concept, non-business domain, speculative future), does the agent: (a) state the interpretation/assumption explicitly, (b) acknowledge uncertainty or data limitations, or (c) decline gracefully with a clear explanation?

This evaluator is ONLY relevant for edge-case or ambiguous queries. For clear, well-scoped market queries, return PASS automatically.

## Scoring
- **PASS**: Agent explicitly flags ambiguity, states its interpretation, caveats data limitations, or declines gracefully. The user is not misled about the basis for the ranking.
- **FAIL**: Agent produces confident rankings with no acknowledgment that the query was ambiguous, the category is unclear, the data is speculative, or that a significant assumption was made. Includes cases where the agent adds only generic hedging ("results may vary") without addressing the specific challenge this query poses.

## Few-Shot Examples

### Example 1 — PASS
Input: "important companies"
Output excerpt: "This query doesn't specify an industry, size, or definition of 'important.' I'll interpret it as largest companies by market capitalization globally as of 2025. If you meant important by revenue, employees, or societal impact, please clarify. **Category**: Largest Companies by Market Cap (Global, 2025) | 1 | Apple | $3.7T market cap | | 2 | Nvidia | $3.4T market cap | | 3 | Microsoft | $3.1T market cap |"
Result: {"reason": "Agent correctly flags that 'important' is undefined, states its interpretation explicitly (market cap), and invites correction before ranking. User is not misled about what metric is being used.", "score": "PASS"}

### Example 2 — FAIL
Input: "ocean"
Output excerpt: "**Category**: Ocean shipping & logistics | 1 | Maersk | $81B revenue FY2023 | | 2 | MSC Mediterranean Shipping | ~$50B est. | | 3 | CMA CGM | $72B FY2023 |"
Result: {"reason": "The agent silently chose 'ocean shipping' without acknowledging that 'ocean' is not a market category and could mean offshore drilling, desalination, marine data, oceanographic research, or aquaculture. Confident rankings were produced with no ambiguity flag.", "score": "FAIL"}

### Example 3 — FAIL
Input: "electric vehicle companies in 2027"
Output excerpt: "Note: 2027 figures are projections based on current growth rates. **Category**: Electric Vehicle Manufacturers (2027 projected) | 1 | Tesla | $120B projected revenue | | 2 | BYD | $150B projected | | 3 | Volkswagen EV | $40B projected |"
Result: {"reason": "The generic projection note does not address why EV forecasts are particularly uncertain (policy risk, adoption curve volatility, competitive dynamics). More critically, BYD is ranked #2 despite the output citing a higher projected revenue than Tesla — a ranking contradiction that goes unacknowledged. The agent did not adequately flag the speculative nature of the query.", "score": "FAIL"}

---

Now evaluate:

Input: {input}
Output: {output}

First: Is this query an edge case? (vague, out-of-scope, or impossible to rank confidently with public data?)
- If NO (clear, well-scoped query): return {{"reason": "Clear market query — edge case handling evaluator not applicable.", "score": "PASS"}}
- If YES: evaluate against the criterion above.

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
        model="gpt-4.1",
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
