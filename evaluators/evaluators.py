"""
Market Map Agent — Evaluators for Braintrust
Day 2: Code-based evaluators + LLM judges

Usage in Braintrust:
    from evaluators import company_count, has_sources, has_metrics, has_category
    from evaluators import ranking_quality_judge, edge_case_handling_judge, reference_judge, metric_coverage_judge

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
- **FAIL**: A significant/obvious market leader is missing from the top 3, OR the ranking order directly contradicts the metrics cited (e.g., company ranked #1 has lower revenue than company ranked #2), OR the companies listed are mid-market players when dominant leaders exist.

## Few-Shot Examples

### Example 1 — PASS
Input: "CRM software"
Output excerpt: "**Category**: CRM Software | Rank | Company | Revenue | Customers | | 1 | Salesforce | $34.9B FY2024 | 150,000+ | | 2 | Microsoft Dynamics | ~$5B est. FY2024 | 40,000+ | | 3 | HubSpot | $2.17B FY2024 | 200,000+ |"
Result: {{"reason": "Top 3 are the correct players. Salesforce's dominance is well-established. The Microsoft vs HubSpot order is correctly based on revenue despite HubSpot having more customers, consistent with the ranking criteria.", "score": "PASS"}}

### Example 2 — FAIL
Input: "video conferencing software"
Output excerpt: "| 1 | Google Meet | 3B+ total meeting participants (Google Workspace) | | 2 | Microsoft Teams | 320M MAU | | 3 | Zoom | $4.7B FY2025 revenue · 300M daily meeting participants |"
Result: {{"reason": "Zoom is ranked #3 despite having $4.7B in standalone revenue — the highest among pure-play video conferencing companies. Google Meet has no disclosed standalone revenue and is bundled with Workspace. By the revenue-first criterion, Zoom should be #1, not #3.", "score": "FAIL"}}

### Example 3 — FAIL
Input: "business intelligence tools"
Output excerpt: "| 1 | Domo | $340M ARR · 30,000+ customers | | 2 | Sisense | ~$100M est. revenue | | 3 | Qlik | ~$800M est. revenue |"
Result: {{"reason": "All three dominant BI players — Microsoft Power BI (100M+ users, ~$3B+ est.), Tableau ($1.4B standalone revenue), and Looker (Google Cloud) — are absent from the output. Domo, Sisense, and Qlik are mid-market vendors. This output reflects a long tail of the market, not the leaders.", "score": "FAIL"}}

---

Now evaluate:

Input: {input}
Output: {output}

Respond with JSON only:
{{"reason": "<2-3 sentence explanation>", "score": "PASS" | "FAIL"}}
"""


EDGE_CASE_HANDLING_PROMPT = """\
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
Result: {{"reason": "Agent correctly flags that 'important' is undefined, states its interpretation explicitly (market cap), and invites correction before ranking. User is not misled about what metric is being used.", "score": "PASS"}}

### Example 2 — FAIL
Input: "ocean"
Output excerpt: "**Category**: Ocean shipping & logistics | 1 | Maersk | $81B revenue FY2023 | | 2 | MSC Mediterranean Shipping | ~$50B est. | | 3 | CMA CGM | $72B FY2023 |"
Result: {{"reason": "The agent silently chose 'ocean shipping' without acknowledging that 'ocean' is not a market category and could mean offshore drilling, desalination, marine data, oceanographic research, or aquaculture. Confident rankings were produced with no ambiguity flag.", "score": "FAIL"}}

### Example 3 — FAIL
Input: "electric vehicle companies in 2027"
Output excerpt: "Note: 2027 figures are projections based on current growth rates. **Category**: Electric Vehicle Manufacturers (2027 projected) | 1 | Tesla | $120B projected revenue | | 2 | BYD | $150B projected | | 3 | Volkswagen EV | $40B projected |"
Result: {{"reason": "The generic projection note does not address why EV forecasts are particularly uncertain (policy risk, adoption curve volatility, competitive dynamics). More critically, BYD is ranked #2 despite the output citing a higher projected revenue than Tesla — a ranking contradiction that goes unacknowledged. The agent did not adequately flag the speculative nature of the query.", "score": "FAIL"}}

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


REFERENCE_JUDGE_PROMPT = """\
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
Result: {{"reason": "Same top 3 companies, same rank order, metrics agree within rounding. Minor phrasing differences don't affect accuracy.", "score": "PASS"}}

### Example 2 — FAIL
Reference: "Category: Video Conferencing Software. #1 Zoom ($4.7B FY2025 revenue, 300M daily participants), #2 Microsoft Teams (320M MAU), #3 Google Meet (Workspace bundle)"
Output: "Category: Video Conferencing. #1 Google Meet (largest meeting participants across Workspace) · #2 Microsoft Teams (320M MAU) · #3 Zoom ($4.7B revenue)"
Result: {{"reason": "Google Meet is not the reference #1 — Zoom is. The output ranks Zoom last despite citing its $4.7B standalone revenue, which is the highest in the category. The rank order is inverted from the reference on the most important criterion.", "score": "FAIL"}}

### Example 3 — FAIL
Reference: "Category: Business Intelligence Tools. #1 Microsoft Power BI (100M+ users, ~$3B est. revenue via M365), #2 Tableau ($1.4B est. standalone revenue), #3 Looker/Google (~$500M est.)"
Output: "Category: BI and Analytics. #1 Tableau ($1.4B revenue, 42,000+ customers) · #2 Microsoft Power BI (100M+ users, bundled with Microsoft 365) · #3 Looker ($500M est.)"
Result: {{"reason": "All three companies are present but Tableau and Power BI are swapped — the reference ranks Power BI #1, the output ranks Tableau #1. Rank order is part of the evaluation criterion; a #1/#2 swap is a meaningful disagreement with the reference, not a rounding difference.", "score": "FAIL"}}

---

Now evaluate:

Input: {input}
Reference answer: {expected}
Model output: {output}

Respond with JSON only:
{{"reason": "<2-3 sentence explanation>", "score": "PASS" | "FAIL"}}
"""


METRIC_COVERAGE_PROMPT = """\
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
Result: {{"reason": "Asana has 2 metrics (revenue + customers), Monday.com has 3 metrics (revenue + customers + growth rate). That's 2 of 3 companies meeting the threshold. Atlassian has only 1 metric but that does not prevent a PASS since 2 of 3 companies qualify.", "score": "PASS"}}

### Example 2 — FAIL
Input: "email marketing tools"
Output excerpt: "**Category**: Email Marketing Platforms | 1 | Mailchimp (Intuit) — the market leader, trusted by small businesses | 2 | Constant Contact — reliable platform for SMBs with strong customer support | 3 | Klaviyo — the top choice for e-commerce brands |"
Result: {{"reason": "None of the three companies have any quantitative data points. All descriptions are qualitative labels. Zero of three companies meet the 2-metric threshold.", "score": "FAIL"}}

---

Now evaluate:

Input: {input}
Output: {output}

Respond with JSON only:
{{"reason": "<2-3 sentence explanation>", "score": "PASS" | "FAIL"}}
"""


COMPANY_MATCH_PROMPT = """\
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
Result: {{"reason": "All three companies match in the correct order. 'Microsoft Dynamics 365' is the same company as 'Microsoft Dynamics'.", "score": "PASS"}}

### Example 2 — FAIL
Reference: "#1 Zoom, #2 Microsoft Teams, #3 Google Meet"
Output: "1. Microsoft Teams (320M MAU) 2. Zoom ($4.7B revenue) 3. Google Meet"
Result: {{"reason": "Zoom and Microsoft Teams are swapped — Zoom is #1 in the reference but appears as #2 in the output.", "score": "FAIL"}}

---

Reference: {expected}
Output: {output}

Respond with JSON only:
{{"reason": "<1-2 sentence explanation>", "score": "PASS" | "FAIL"}}
"""


METRIC_SCOPE_PROMPT = """\
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
Result: {{"reason": "Zoom is a pure-play product — total revenue is correct. Teams and Google Meet are divisions, but the response provides analyst estimates scoped to those products rather than citing Microsoft's $245B or Alphabet's $350B totals.", "score": "PASS"}}

### Example 2 — FAIL
Input: "enterprise video conferencing software"
Output excerpt: "1. Microsoft Teams — Microsoft total revenue $245B FY2024. 2. Zoom — $4.7B FY2025 revenue. 3. Google Meet — Alphabet total revenue $350B FY2024."
Result: {{"reason": "Microsoft Teams and Google Meet are single product lines within much larger companies. Citing Microsoft's $245B and Alphabet's $350B total revenues as metrics for their video conferencing products is misleading — these figures include cloud, search, hardware, and dozens of other businesses.", "score": "FAIL"}}

### Example 3 — FAIL
Input: "project management software"
Output excerpt: "1. Asana — $723M FY2024 revenue. 2. Monday.com — $966M FY2024 revenue. 3. Atlassian — $4.4B total revenue (Jira is one of several products; standalone Jira revenue not publicly disclosed)."
Result: {{"reason": "Atlassian correctly notes Jira is one of several products, but then cites total company revenue and offers no estimate of Jira's standalone contribution. An analyst estimate or breakdown was available and expected.", "score": "FAIL"}}

---

Input: {input}
Output: {output}

Respond with JSON only:
{{"reason": "<1-2 sentence explanation>", "score": "PASS" | "FAIL"}}
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
        return {"score": 0.0, "metadata": {"reason": "Failed to parse judge response", "raw": text}}

    score_map = {"PASS": 1.0, "FAIL": 0.0}
    return {
        "score": score_map.get(result.get("score", "FAIL"), 0.0),
        "metadata": {
            "reason": result.get("reason", ""),
            "label": result.get("score", "FAIL")
        }
    }


def ranking_quality_judge(output, input, expected=None):
    """
    LLM judge: Are the top 3 companies the right ones, in the right order?
    Most useful on well-scoped queries where ground truth is knowable.
    Returns: {"score": 0.0|1.0, "metadata": {"reason": str, "label": str}}
    """
    prompt = RANKING_QUALITY_PROMPT.format(input=input, output=output)
    return _run_judge(prompt)


def edge_case_handling_judge(output, input, expected=None):
    """
    LLM judge: For vague/out-of-scope queries, did the agent handle ambiguity gracefully?
    Auto-passes for clear, well-scoped queries.
    Returns: {"score": 0.0|1.0, "metadata": {"reason": str, "label": str}}
    """
    prompt = EDGE_CASE_HANDLING_PROMPT.format(input=input, output=output)
    return _run_judge(prompt)


def reference_judge(output, input, expected=None):
    """
    Reference-based LLM judge: Compare output to a gold-standard answer in the 'expected' column.
    Requires the dataset to have an 'expected' field populated.
    Returns: {"score": 0.0|1.0, "metadata": {"reason": str, "label": str}}
    """
    if not expected:
        return {
            "score": None,
            "metadata": {"reason": "No reference answer provided — skipping reference judge.", "label": "N/A"}
        }
    prompt = REFERENCE_JUDGE_PROMPT.format(input=input, expected=expected, output=output)
    return _run_judge(prompt)


def metric_coverage_judge(output, input, expected=None):
    """
    LLM judge: Do at least 2 of the 3 ranked companies have at least 2 quantitative metrics each?
    Complements the deterministic has_metrics check with semantic understanding of what counts as a metric.
    Returns: {"score": 0.0|1.0, "metadata": {"reason": str, "label": str}}
    """
    prompt = METRIC_COVERAGE_PROMPT.format(input=input, output=output)
    return _run_judge(prompt)


def company_match_judge(output, input, expected=None):
    """
    Reference-based LLM judge: Do the top 3 companies in the output match the reference in the same order?
    Simpler than reference_judge — only checks company identity and rank, not metrics or category.
    Requires the dataset to have an 'expected' field populated.
    Returns: {"score": 0.0|1.0, "metadata": {"reason": str, "label": str}}
    """
    if not expected:
        return {
            "score": None,
            "metadata": {"reason": "No reference answer provided — skipping company match judge.", "label": "N/A"}
        }
    prompt = COMPANY_MATCH_PROMPT.format(expected=expected, output=output)
    return _run_judge(prompt)


def metric_scope_judge(output, input, expected=None):
    """
    LLM judge: Are metrics scoped to the relevant product/division, not the parent company?
    Catches the pattern where e.g. Microsoft's $245B total revenue is cited for a Teams query.
    Returns: {"score": 0.0|1.0, "metadata": {"reason": str, "label": str}}
    """
    prompt = METRIC_SCOPE_PROMPT.format(input=input, output=output)
    return _run_judge(prompt)
