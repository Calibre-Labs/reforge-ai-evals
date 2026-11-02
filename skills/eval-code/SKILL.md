---
name: eval-code
description: >
  Write deterministic, code-based evaluator functions for an AI product. Use this skill whenever
  you need to write evaluators that check structural properties of AI outputs (format, count,
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

### Step 1 — Find the project's scorer contract

Before writing anything, look for where the project already keeps its evaluators: a `scorers/` or
`evals/` folder, a types or contract file, existing scorers, a README that says how they run. If
there is one, write in that language and follow it exactly: the function signature, the return
shape, how the file is named, and where it goes. A new check should look like its neighbors.

For example, Mapper's course scorers live in `scorers/course/`, one TypeScript file per scorer.
`scorers/course/types.ts` defines the contract: each file default-exports a function that takes a
recorded session and returns `{ name, score: 0 | 1, metadata: { reason } }`, and the file name is
the scorer's id.

Use the Python signature and templates below only when the project has no contract of its own.

### Step 2 — Identify the property to check

Start from the product's output requirements, not from what seems easy to check. Ask:
*"What must always be true in a valid output, regardless of the input?"*

When the check comes from a rubric line and a trace code, read both. The rubric line defines what
passes; the trace code names the failure you saw in traces. They can differ in scope. For
example, Mapper's trace code 10 is "writes an essay instead of a map", but rubric line X1 also
counts an analysis card as an output and limits the commentary around it to two sentences. When
they differ, the rubric line wins. Put the rubric line and the trace code numbers in the
scorer's header comment, so anyone reading results can trace a score back to what was found.

For each property, write one sentence: **"A valid output must [verb] [object]."**

Examples:
- A valid output must contain exactly N ranked results.
- A valid output must include at least 3 source citations.
- A valid output must include a summary section before the detailed breakdown.
- A valid output must be parseable as valid JSON matching the schema.

If the sentence requires words like "correctly" or "appropriate" or "relevant", stop —
that property needs an LLM judge, not a code check.

### Step 3 — Decide what happens when the check doesn't apply

Some rows have nothing to check: a request the agent should decline has no map to inspect, and a
session with no table has no columns to count. Decide up front what those rows score, and put it
in the reason. Usually that's a pass whose reason says why ("Row should be declined; no research
answer to check"). If the project's contract supports skipping a row (a null score), use that
instead. Never let a not-applicable row pass silently: the reason is how a reader tells "passed
the check" from "had nothing to check".

### Step 4 — Write the function signature

Use the project's contract from Step 1. Without one, this signature works across most eval
platforms (Braintrust, LangSmith, custom runners):

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

### Step 5 — Write the check, then find its failure modes

After writing the initial check, systematically ask:
1. **False positive**: what valid output would this check incorrectly score 1.0?
   (e.g., a regex for "1." also matches "10." or "1.5B")
2. **False negative**: what invalid output would this check incorrectly score 0.0?
   (e.g., a check for "**Category**:" misses "## Market Category" as a heading)
3. **Malicious input**: could a model learn to game this check trivially?
   (e.g., always appending "Sources: [1] [2] [3]" with no real links)

Fix the top 1–2 failure modes. Don't over-engineer — accept that code-based checks
have limits, and cover the rest with LLM judges.

### Step 6 — Add partial credit where it makes sense

Binary (0/1) scoring is fine when the property is binary (either you have 3 companies or you don't).
Add partial credit when:
- There's a natural scale (0, 1, 2, 3 citations → 0.0, 0.33, 0.66, 1.0)
- You want to distinguish "completely missing" from "partially present"

Don't add partial credit just because it feels nicer — it complicates threshold-setting.
If the project's contract is binary (a score of 0 or 1, like Mapper's), stay binary and put the
detail in the reason.

### Step 7 — Test on known examples, then on recorded runs

Run the evaluator on at least:
- 1 clearly valid output (should score 1.0)
- 1 clearly invalid output (should score 0.0)
- 1 edge case that you're not sure about

If the evaluator scores an obviously valid output below 0.8, the check is too strict.
If it scores an obviously invalid output above 0.2, the check is too loose.

Then run it on the recorded runs you'll report, and read every failing row's reason against the
output. A check you haven't read failures for is a check you don't know.

If it never fails on any run, say so when you report it. A check that passes everything isn't
measuring a current problem; it's a regression guard that will catch the problem if a later
change brings it back. That's useful, but it's a different claim from "this is fixed".

---

## Output Format

Write each evaluator in the project's own format (Step 1): its language, its folder, one file per
scorer if that's the convention. Without a project format, write a Python file with one function
per evaluator. Either way, each function:
- Has a clear docstring stating what it checks and what counts as pass/fail, plus the rubric line
  and trace code numbers it comes from
- Returns a float or dict (not print statements)
- Is independently testable (no global state, no side effects)

```python
def result_count(output: str, input: str, expected: str = None) -> dict:
    """
    Checks that exactly N items appear in the output.

    Pass: output contains exactly N numbered/ranked entries
    Fail: output contains 0 to N-1 or N+ entries
    Partial (0.5): output contains N-1 entries (close but not compliant)

    Does NOT check whether the items are correct — use an LLM judge for content correctness.
    """
    ...
```

---

## Common Patterns

### Count with partial credit
```python
import re

def result_count(output, input, expected=None):
    """
    Checks that exactly N ranked/numbered items appear in the output.
    Adapt the regex and expected count to your product's output format.
    """
    matches = re.findall(r'(?:^|\n)\s*\d+[\.\)]\s+\S', output, re.MULTILINE)
    expected_n = 3  # set to whatever your product should return
    if len(matches) == expected_n:
        return 1.0
    if len(matches) == expected_n - 1:
        return {"score": 0.5, "metadata": {"found": len(matches), "expected": expected_n}}
    return {"score": 0.0, "metadata": {"found": len(matches), "expected": expected_n}}
```

### Presence check with multiple fallback patterns
```python
def has_disclaimer(output, input, expected=None):
    """
    Checks that a required disclaimer or section header is present.
    Use multiple patterns to handle different formatting styles the model may produce.
    """
    patterns = [
        r'\*{0,2}disclaimer\*{0,2}\s*:',          # "**Disclaimer**:"
        r'^#{1,3}\s+.*disclaimer',                  # "## Disclaimer"
        r'(?:this is not|should not be construed)', # prose disclaimer
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

# Replace with the schema your product's output should conform to
SCHEMA = {
    "type": "object",
    "required": ["summary", "items", "sources"],
    "properties": {
        "items": {"type": "array", "minItems": 1},
        "sources": {"type": "array", "minItems": 1}
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
