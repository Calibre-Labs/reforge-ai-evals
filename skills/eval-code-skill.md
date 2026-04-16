---
name: eval-code
description: >
  Write deterministic, code-based evaluator functions for an AI product. Use this skill whenever
  Sandhya needs to write evaluators that check structural properties of AI outputs (format, count,
  presence, schema compliance) without calling another LLM. Also use when auditing existing
  code-based evaluators for brittleness, coverage gaps, or false positives.
---

# Code-Based Evaluator Skill

Code-based evaluators are deterministic functions that check AI outputs using regex, string
operations, schema validation, or simple parsing — no LLM call required. They are fast, cheap,
and produce the same result every time, which makes them the foundation of any eval suite.

The tradeoff: they can only check what is mechanically verifiable. They cannot assess whether
the content is *correct*, *relevant*, or *well-reasoned*. Use them for structural properties;
use LLM judges for semantic ones.

## When to use this skill

Write code-based evaluators when the property you want to check can be expressed as:
- **Presence/absence**: does the output contain X? (a section heading, a citation, a table)
- **Count**: does the output contain exactly/at least N of something? (3 companies, 3 sources)
- **Format compliance**: is the output in the expected structure? (JSON schema, markdown table)
- **Value range**: is a number within expected bounds? (confidence score 0–1, year 1900–2030)
- **String match**: does the output contain a required string? (company name, required disclaimer)

Do NOT write a code-based evaluator for:
- Whether the companies ranked are the *right* companies (use an LLM judge)
- Whether the rationale is coherent (use an LLM judge)
- Whether citations are accurate (requires external lookup or LLM judge)

---

## Workflow

### Step 1 — Identify the property to check

Start from the product's output requirements, not from what seems easy to check. Ask:
*"What must always be true in a valid output, regardless of the input?"*

For each property, write one sentence: **"A valid output must [verb] [object]."**

Examples:
- A valid output must contain exactly 3 ranked companies.
- A valid output must include at least 3 source citations.
- A valid output must identify a market category before ranking companies.
- A valid output must be parseable as valid JSON matching the schema.

If the sentence requires words like "correctly" or "appropriate" or "relevant", stop —
that property needs an LLM judge, not a code check.

### Step 2 — Write the function signature

For Braintrust, the signature is:
```python
def evaluator_name(output: str, input: str, expected: str = None) -> float | dict:
    ...
```

Return a `float` between 0.0 and 1.0, or a `dict` with at least a `score` key:
```python
{"score": 0.5, "metadata": {"reason": "found 2 citations, expected 3"}}
```

Return metadata whenever partial credit is possible — it tells you *why* a score is 0.5,
not just *that* it is.

### Step 3 — Write the check, then find its failure modes

After writing the initial check, systematically ask:
1. **False positive**: what valid output would this check incorrectly score 1.0?
   (e.g., a regex for "1." also matches "10." or "1.5B")
2. **False negative**: what invalid output would this check incorrectly score 0.0?
   (e.g., a check for "**Category**:" misses "## Market Category" as a heading)
3. **Malicious input**: could a model learn to game this check trivially?
   (e.g., always appending "Sources: [1] [2] [3]" with no real links)

Fix the top 1–2 failure modes. Don't over-engineer — accept that code-based checks
have limits, and cover the rest with LLM judges.

### Step 4 — Add partial credit where it makes sense

Binary (0/1) scoring is fine when the property is binary (either you have 3 companies or you don't).
Add partial credit when:
- There's a natural scale (0, 1, 2, 3 citations → 0.0, 0.33, 0.66, 1.0)
- You want to distinguish "completely missing" from "partially present"

Don't add partial credit just because it feels nicer — it complicates threshold-setting.

### Step 5 — Test the evaluator on known examples before committing

Run the evaluator on at least:
- 1 clearly valid output (should score 1.0)
- 1 clearly invalid output (should score 0.0)
- 1 edge case that you're not sure about

If the evaluator scores an obviously valid output below 0.8, the check is too strict.
If it scores an obviously invalid output above 0.2, the check is too loose.

---

## Output Format

Write evaluators as a Python file with one function per evaluator. Each function:
- Has a clear docstring stating what it checks and what counts as pass/fail
- Returns a float or dict (not print statements)
- Is independently testable (no global state, no side effects)

```python
def company_count(output: str, input: str, expected: str = None) -> dict:
    """
    Checks that exactly 3 ranked companies appear in the output.
    
    Pass: output contains exactly 3 numbered/ranked company entries
    Fail: output contains 0, 1, 2, or 4+ ranked entries
    Partial (0.5): output contains 2 entries (close but not compliant)
    
    Does NOT check whether the companies are the right ones — use ranking_quality_judge for that.
    """
    ...
```

---

## Common Patterns

### Count with partial credit
```python
import re

def company_count(output, input, expected=None):
    matches = re.findall(r'(?:^|\n)\s*[123][\.\)]\s+\S', output, re.MULTILINE)
    if len(matches) == 3:
        return 1.0
    if len(matches) == 2:
        return {"score": 0.5, "metadata": {"found": len(matches), "expected": 3}}
    return {"score": 0.0, "metadata": {"found": len(matches), "expected": 3}}
```

### Presence check with multiple fallback patterns
```python
def has_category(output, input, expected=None):
    # Try most specific pattern first, fall back to looser ones
    patterns = [
        r'\*{0,2}(?:market\s+)?category\*{0,2}\s*:',          # "**Category**:"
        r'^#{1,3}\s+.*(?:market|category|industry)',             # "## Market Category"
        r'(?:identified as|categorized as|the market for)',      # prose identification
    ]
    for p in patterns:
        if re.search(p, output, re.IGNORECASE | re.MULTILINE):
            return 1.0
    return 0.0
```

### JSON schema validation
```python
import json
from jsonschema import validate, ValidationError

SCHEMA = {
    "type": "object",
    "required": ["category", "companies", "sources"],
    "properties": {
        "companies": {"type": "array", "minItems": 3, "maxItems": 3},
        "sources": {"type": "array", "minItems": 3}
    }
}

def valid_schema(output, input, expected=None):
    try:
        data = json.loads(output)
        validate(data, SCHEMA)
        return 1.0
    except (json.JSONDecodeError, ValidationError) as e:
        return {"score": 0.0, "metadata": {"error": str(e)}}
```

---

## Working Notes

- **Start with 2–3 evaluators, not 10.** Four good code-based checks cover most structural requirements. More than 6 usually means you're checking things an LLM judge should handle.

- **Name evaluators after what they check, not what they penalize.** `has_sources` is better than `no_missing_citations`. The positive framing makes pass/fail interpretation intuitive.

- **Don't hard-code company names or category strings.** The check should be structural ("3 ranked items") not content-specific ("contains 'Salesforce'"). Content correctness is the judge's job.

- **Regex is fragile across output formats.** If the model sometimes produces markdown tables, sometimes numbered lists, and sometimes prose — your regex needs to handle all three or you'll get false negatives. Test on diverse outputs before relying on a single pattern.

- **Score 0.5 sparingly.** Partial credit is useful for training signal but confusing for dashboards. If you're not sure whether to give 0.5, default to binary and document the decision.

- **Track false positive rate manually.** Run the evaluator on a sample of outputs and manually check the ones that score 1.0. If any are obviously invalid, your check is too loose.
