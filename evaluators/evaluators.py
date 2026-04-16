"""
Market Map Agent — Evaluators for Braintrust
Day 2: Code-based evaluators + LLM judges

Usage in Braintrust:
    from evaluators import company_count, has_sources, has_metrics, has_category
    from evaluators import ranking_quality_judge, edge_case_handling_judge, reference_judge

Each function signature: fn(output, input, expected=None) -> float | dict
Braintrust expects a score between 0.0 and 1.0, or a dict with {"score": float, "metadata": dict}
"""

import re
import json


# ─────────────────────────────────────────────
# CODE-BASED EVALUATORS (deterministic, fast)
# ─────────────────────────────────────────────

def company_count(output, input, expected=None):
    """
    Checks that exactly 3 ranked companies appear in the output.
    Looks for numbered list items (1., 2., 3.) or markdown table rows with rank numbers.
    Returns 1.0 if exactly 3 found, 0.5 if 2 found, 0.0 otherwise.
    """
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


def has_sources(output, input, expected=None):
    """
    Checks that the output includes 3–4 source citations.
    Accepts URLs, numbered references [1], or a Sources/References section.
    Returns 1.0 if ≥3 citations found, 0.5 if 1–2, 0.0 if none.
    """
    # Count URLs
    urls = re.findall(r'https?://\S+', output)

    # Count numbered references [1], [2], etc.
    bracketed_refs = re.findall(r'\[\d+\]', output)

    # Count lines in a Sources section (markdown heading + list items)
    sources_section = re.search(
        r'(?:#{1,3}\s*sources?|#{1,3}\s*references?|#{1,3}\s*citations?)(.*?)(?=\n#{1,3}|\Z)',
        output, re.IGNORECASE | re.DOTALL
    )
    section_items = []
    if sources_section:
        section_items = re.findall(r'^\s*[-\d*]+[\.\)]\s+\S', sources_section.group(1), re.MULTILINE)

    total = max(len(urls), len(set(bracketed_refs)), len(section_items))

    if total >= 3:
        return 1.0
    if total >= 1:
        return 0.5
    return 0.0


def has_metrics(output, input, expected=None):
    """
    Checks that companies are backed by at least 2 data points each (≥6 total).
    Looks for: $ figures, B/M/K suffixes, percentages, customer/user counts, year references.
    Returns 1.0 if ≥6 metrics, 0.5 if 3–5, 0.0 if <3.
    """
    # Dollar figures: $34.9B, $2.1M, $500K
    dollar_figures = re.findall(r'\$[\d,\.]+\s*[BMKbmk]?\b', output)

    # Standalone number + B/M/K (revenue shorthand): 34.9B, 150M
    shorthand = re.findall(r'\b\d+(?:\.\d+)?\s*[BMKbmk]\b', output)

    # Percentages
    percentages = re.findall(r'\b\d+(?:\.\d+)?%', output)

    # Customer/user/employee counts
    counts = re.findall(r'\b\d[\d,]+\s*(?:customers?|users?|employees?|clients?|subscribers?)\b', output, re.IGNORECASE)

    total = len(dollar_figures) + len(shorthand) + len(percentages) + len(counts)
    # Deduplicate loosely by capping contribution of each type
    total = len(set(dollar_figures)) + len(set(shorthand)) + len(set(percentages)) + len(set(counts))

    if total >= 6:
        return 1.0
    if total >= 3:
        return 0.5
    return 0.0


def has_category(output, input, expected=None):
    """
    Checks that the output identifies a market category before ranking companies.
    Looks for a "Category:" label, a markdown heading like "## Market Category", or
    an opening sentence that names the market being analyzed.
    Returns 1.0 if found, 0.0 otherwise.
    """
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


# ─────────────────────────────────────────────
# LLM JUDGE PROMPTS
# ─────────────────────────────────────────────

RANKING_QUALITY_PROMPT = """\
You are evaluating whether an AI market research assistant correctly identified and ranked the top 3 players in a market.

## Evaluation Criterion
**Ranking Quality**: Are the 3 companies the most defensible choices for this market, ranked in the correct order based on: revenue > valuation > customer count > ratings/reviews?

## Scoring
- **PASS**: The top 3 companies are plausible, well-known leaders in the market. The ranking order is consistent with the metrics cited (revenue-first priority). Minor debatable placements are acceptable if the metrics support them.
- **FAIL**: A significant/obvious market leader is missing from the top 3, OR the ranking order directly contradicts the metrics cited (e.g., company ranked #1 has lower revenue than company ranked #2).
- **BORDERLINE**: Companies are correct but ranking order is legitimately debatable (two companies have comparable metrics and either could be #1).

## Few-Shot Examples

### Example 1 — PASS
Input: "CRM software"
Output excerpt: "**Category**: CRM Software | Rank | Company | Revenue | Customers | | 1 | Salesforce | $34.9B FY2024 | 150,000+ | | 2 | Microsoft Dynamics | ~$5B est. FY2024 | 40,000+ | | 3 | HubSpot | $2.17B FY2024 | 200,000+ |"
Result: {{"critique": "Top 3 are the correct players. Salesforce's dominance is well-established. The Microsoft vs HubSpot order is correctly based on revenue despite HubSpot having more customers, consistent with the ranking criteria.", "score": "PASS"}}

### Example 2 — FAIL
Input: "video conferencing software"
Output excerpt: "| 1 | Google Meet | 3B+ total meeting participants (Google Workspace) | | 2 | Microsoft Teams | 320M MAU | | 3 | Zoom | $4.7B FY2025 revenue · 300M daily meeting participants |"
Result: {{"critique": "Zoom is ranked #3 despite having $4.7B in standalone revenue — the highest among pure-play video conferencing companies. Google Meet has no disclosed standalone revenue and is bundled with Workspace. By the revenue-first criterion, Zoom should be #1, not #3.", "score": "FAIL"}}

### Example 3 — BORDERLINE
Input: "business intelligence tools"
Output excerpt: "| 1 | Tableau | $1.4B est. revenue · 42,000+ customers | | 2 | Microsoft Power BI | 100M+ users · bundled with Microsoft 365 | | 3 | Looker | ~$500M est. · part of Google Cloud |"
Result: {{"critique": "All three companies are the correct players. Tableau vs Power BI rank order is legitimately debatable — Tableau has higher reported standalone revenue ($1.4B) while Power BI likely has higher total revenue as part of Microsoft 365 licensing. Either at #1 is defensible given the bundling ambiguity.", "score": "BORDERLINE"}}

---

Now evaluate:

Input: {input}
Output: {output}

Respond with JSON only:
{{"critique": "<2-3 sentence explanation>", "score": "PASS" | "FAIL" | "BORDERLINE"}}
"""


EDGE_CASE_HANDLING_PROMPT = """\
You are evaluating whether an AI market research assistant handled a vague, ambiguous, or out-of-scope query appropriately.

## Evaluation Criterion
**Edge Case Handling**: For queries where a definitive ranking is impossible or requires major assumptions (vague category, abstract concept, non-business domain, speculative future), does the agent: (a) state the interpretation/assumption explicitly, (b) acknowledge uncertainty or data limitations, or (c) decline gracefully with a clear explanation?

This evaluator is ONLY relevant for edge-case or ambiguous queries. For clear, well-scoped market queries, return PASS automatically.

## Scoring
- **PASS**: Agent explicitly flags ambiguity, states its interpretation, caveats data limitations, or declines gracefully. User is not misled.
- **FAIL**: Agent produces confident rankings with no acknowledgment that the query was ambiguous, the category is unclear, or the data is speculative. User could be misled.
- **BORDERLINE**: Agent produces rankings with generic hedging ("results may vary", "data is approximate") but doesn't specifically address why this query is challenging.

## Few-Shot Examples

### Example 1 — PASS
Input: "important companies"
Output excerpt: "This query doesn't specify an industry, size, or definition of 'important.' I'll interpret it as largest companies by market capitalization globally as of 2025. If you meant important by revenue, employees, or societal impact, please clarify. **Category**: Largest Companies by Market Cap (Global, 2025) | 1 | Apple | $3.7T market cap | | 2 | Nvidia | $3.4T market cap | | 3 | Microsoft | $3.1T market cap |"
Result: {{"critique": "Agent correctly flags that 'important' is undefined, states its interpretation explicitly (market cap), and invites correction before ranking. User is not misled about what metric is being used.", "score": "PASS"}}

### Example 2 — FAIL
Input: "ocean"
Output excerpt: "**Category**: Ocean shipping & logistics | 1 | Maersk | $81B revenue FY2023 | | 2 | MSC Mediterranean Shipping | ~$50B est. | | 3 | CMA CGM | $72B FY2023 |"
Result: {{"critique": "The agent silently chose 'ocean shipping' without acknowledging that 'ocean' is not a market category and could mean offshore drilling, desalination, marine data, oceanographic research, or aquaculture. Confident rankings were produced with no ambiguity flag.", "score": "FAIL"}}

### Example 3 — BORDERLINE
Input: "electric vehicle companies in 2027"
Output excerpt: "Note: 2027 figures are projections based on current growth rates. **Category**: Electric Vehicle Manufacturers (2027 projected) | 1 | Tesla | $120B projected revenue | | 2 | BYD | $150B projected | | 3 | Volkswagen EV | $40B projected |"
Result: {{"critique": "The note about projections is present but generic — it doesn't address why EV projections are particularly uncertain (policy risk, adoption curve volatility, BYD vs Tesla competition), and BYD is ranked #2 despite having a higher projected revenue than Tesla in the output itself. Partially addresses the edge case but not specifically enough.", "score": "BORDERLINE"}}

---

Now evaluate:

Input: {input}
Output: {output}

First: Is this query an edge case? (vague, out-of-scope, or impossible to rank confidently with public data?)
- If NO (clear, well-scoped query): return {{"critique": "Clear market query — edge case handling evaluator not applicable.", "score": "PASS"}}
- If YES: evaluate against the criterion above.

Respond with JSON only:
{{"critique": "<2-3 sentence explanation>", "score": "PASS" | "FAIL" | "BORDERLINE"}}
"""


REFERENCE_JUDGE_PROMPT = """\
You are evaluating an AI market research assistant's response by comparing it to a gold-standard reference answer.

## Evaluation Criterion
**Reference Alignment**: Does the output cover the same key companies, metrics, and market category as the reference answer? The output does NOT need to be identical — different phrasing, ordering of sections, or additional context is fine. What matters is: (a) the same top 3 companies, (b) the same market category identified, and (c) comparable supporting metrics (same order of magnitude, same companies ranked in the same order).

## Scoring
- **PASS**: Same top 3 companies in the same rank order, same market category, metrics are in the same order of magnitude.
- **FAIL**: Different companies in the top 3, wrong market category identified, or metrics differ by more than 50% without explanation.
- **BORDERLINE**: 2 of 3 companies match, OR companies match but rank order differs, OR same companies but one key metric is significantly off.

## Few-Shot Examples

### Example 1 — PASS
Reference: "Category: CRM Software. #1 Salesforce ($34.9B), #2 Microsoft Dynamics (~$5B), #3 HubSpot ($2.17B)"
Output: "Market: Customer Relationship Management. Top players: 1. Salesforce — $35B revenue FY2024, 150K customers. 2. Microsoft Dynamics 365 — ~$5B est. 3. HubSpot — $2.2B FY2024, 200K+ customers."
Result: {{"critique": "Same top 3 companies, same rank order, metrics agree within rounding. Minor phrasing differences don't affect accuracy.", "score": "PASS"}}

### Example 2 — FAIL
Reference: "Category: Video Conferencing Software. #1 Zoom ($4.7B FY2025 revenue, 300M daily participants), #2 Microsoft Teams (320M MAU), #3 Google Meet (Workspace bundle)"
Output: "Category: Video Conferencing. #1 Google Meet (largest meeting participants across Workspace) · #2 Microsoft Teams (320M MAU) · #3 Zoom ($4.7B revenue)"
Result: {{"critique": "Google Meet is not in the reference top 3 at #1 — Zoom is. The output ranks Zoom last despite citing its $4.7B standalone revenue, which is the highest in the category. Company order is significantly different from the reference.", "score": "FAIL"}}

### Example 3 — BORDERLINE
Reference: "Category: Business Intelligence Tools. #1 Microsoft Power BI (100M+ users, ~$3B est. revenue via M365), #2 Tableau ($1.4B est. standalone revenue), #3 Looker/Google (~$500M est.)"
Output: "Category: BI and Analytics. #1 Tableau ($1.4B revenue, 42,000+ customers) · #2 Microsoft Power BI (100M+ users, bundled with Microsoft 365) · #3 Looker ($500M est.)"
Result: {{"critique": "All three companies are present and the category matches. Tableau and Power BI are swapped — reference ranks Power BI #1 by estimated total bundled revenue, output ranks Tableau #1 by standalone reported revenue. Both orderings are defensible; the difference reflects an ambiguous ranking criterion when one product is bundled.", "score": "BORDERLINE"}}

---

Now evaluate:

Input: {input}
Reference answer: {expected}
Model output: {output}

Respond with JSON only:
{{"critique": "<2-3 sentence explanation>", "score": "PASS" | "FAIL" | "BORDERLINE"}}
"""


# ─────────────────────────────────────────────
# LLM JUDGE RUNNER
# ─────────────────────────────────────────────

def _run_judge(prompt: str) -> dict:
    """Call Claude with the given judge prompt and parse the JSON response."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\n?', '', text)
        text = re.sub(r'\n?```$', '', text)

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return {"score": 0.0, "metadata": {"critique": "Failed to parse judge response", "raw": text}}

    score_map = {"PASS": 1.0, "BORDERLINE": 0.5, "FAIL": 0.0}
    return {
        "score": score_map.get(result.get("score", "FAIL"), 0.0),
        "metadata": {
            "critique": result.get("critique", ""),
            "label": result.get("score", "FAIL")
        }
    }


def ranking_quality_judge(output, input, expected=None):
    """
    LLM judge: Are the top 3 companies the right ones, in the right order?
    Most useful on well-scoped queries where ground truth is knowable.
    Returns: {"score": 0.0|0.5|1.0, "metadata": {"critique": str, "label": str}}
    """
    prompt = RANKING_QUALITY_PROMPT.format(input=input, output=output)
    return _run_judge(prompt)


def edge_case_handling_judge(output, input, expected=None):
    """
    LLM judge: For vague/out-of-scope queries, did the agent handle ambiguity gracefully?
    Auto-passes for clear, well-scoped queries.
    Returns: {"score": 0.0|0.5|1.0, "metadata": {"critique": str, "label": str}}
    """
    prompt = EDGE_CASE_HANDLING_PROMPT.format(input=input, output=output)
    return _run_judge(prompt)


def reference_judge(output, input, expected=None):
    """
    Reference-based LLM judge: Compare output to a gold-standard answer in the 'expected' column.
    Requires the dataset to have an 'expected' field populated.
    Returns: {"score": 0.0|0.5|1.0, "metadata": {"critique": str, "label": str}}
    """
    if not expected:
        return {
            "score": None,
            "metadata": {"critique": "No reference answer provided — skipping reference judge.", "label": "N/A"}
        }
    prompt = REFERENCE_JUDGE_PROMPT.format(input=input, expected=expected, output=output)
    return _run_judge(prompt)
