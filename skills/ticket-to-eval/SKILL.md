---
name: ticket-to-eval
description: >
  Strip PII from a customer support ticket or eval trace and convert it into eval dataset rows.
  Produces two outputs: a regression dataset row (close to the original input, tagged with
  failure_mode) and a generalized dataset row (abstracted for broader coverage). Works with
  local CSV files or any eval platform. Use this skill whenever someone shares a support ticket,
  user complaint, or raw trace and wants to turn it into eval data. Trigger on: "add this ticket
  to the dataset", "convert this trace to an eval", "strip PII from this complaint", "turn this
  into a test case".
---

# Ticket → Eval Conversion

You are converting a customer support ticket or eval trace into two eval dataset rows: a
regression row (exact input, tagged with failure_mode) and a generalized row (abstracted for
broader coverage). Work through the phases below.

---

## Phase 0: Dataset Discovery

Ask the user where their eval datasets live:
- **Local CSV** — glob for CSV files whose first line contains `input,metadata`
- **Eval platform** (Braintrust, LangSmith, etc.) — ask for the project name and list available datasets
- If unclear, ask: "Should I look for datasets in a local CSV or an eval platform?"

Identify two targets:
- **Regression target** — the dataset tracking real failures (look for "regression" in the name)
- **Coverage target** — the dataset for generalized coverage rows (the broader dev/test set)

Ask the user to confirm both before proceeding.

Store: `regression_target` and `coverage_target` as either `{type: "local", path: "<path>"}` or
`{type: "platform", name: "<dataset name>", project: "<project>"}`.

---

## Phase 1: Extract & Identify

Parse the input — it may be a CSV row, free-form complaint text, or trace JSON.

Extract:
- **original_input**: the exact text or structured input the user sent to the AI
- **complaint_summary**: what went wrong (1 sentence)
- **failure_mode**: classify using the taxonomy below

### Failure Mode Taxonomy

These are common AI failure modes. The list below uses a Market Map agent as a concrete example
of each — adapt the labels to your product's failure patterns:

| Failure mode | What it means | Market Map example |
|---|---|---|
| `intent_misparse` | Agent misread or ignored a key term in the input | Jargon term (PLG, bootstrapped) treated as freeform text |
| `stale_data` | Agent used outdated information | Ranked a company that is bankrupt or acquired |
| `temporal_override` | Historical/future input answered with current data | "Market in 2008" answered with today's data |
| `scope_ignored` | A constraint in the input was ignored | Geographic or segment constraint silently dropped |
| `unit_mismatch` | Metrics returned in wrong units or mixed without disclosure | Revenue in EUR mixed with USD with no conversion note |
| `hallucinated_citation` | Source does not exist or doesn't support the claim | URL 404s or publication doesn't mention the claim |
| `implausible_metric` | A numeric figure is off by >5x from any credible estimate | ARR figure that's 10x the company's actual size |
| `refused_valid_input` | Agent declined to handle something it should be able to | Refused a well-formed request within its stated scope |
| `latency` | Response time complaint (not a content failure; flag separately) | — |
| `format_violation` | Wrong count, broken structure, incomplete output | Wrong number of results, broken table |
| `other` | Describe in a note field | — |

---

## Phase 2: Strip PII

Scan the original input AND any surrounding context for PII. Replace in-place with typed
placeholders. Do NOT alter words that are not PII.

| PII type | Placeholder |
|---|---|
| Person name | `[USER_NAME]` |
| Email address | `[USER_EMAIL]` |
| Company / employer | `[USER_COMPANY]` |
| Session / trace ID | `[SESSION_ID]` |
| Internal dollar figure | `[INTERNAL_FIGURE]` |

**Rule**: domain-specific content (product names, market terms, company names the user is
*asking about*) is rarely PII — preserve it exactly unless it contains the user's own name
or employer submitted in a private context.

Show the cleaned input and ask the user to confirm before proceeding.

---

## Phase 3: Map to Dimensions

Tag the cleaned input using the UIG dimensions from the project's eval dataset. If none are
defined, fall back to these generic fields:

```json
{
  "input_type": "<action_instruction | information_request | aggregation | multi_step | clarification | edge_out_of_scope>",
  "domain": "<adapt to your product's domain dimension>",
  "style": "<well_specified | under_specified | multi_constraint | jargon_heavy | edge_out_of_scope>",
  "temporal": "<current | historical | future>",
  "edge_case": true | false
}
```

Regression-specific additions (Row A only):
```json
{
  "failure_mode": "<from Phase 1>",
  "source_ticket": "<ticket ID if known, else null>",
  "regression": true
}
```

---

## Phase 4: Generate Both Rows

### Row A — Regression Row

- **input**: PII-stripped input (exact)
- **metadata**: full dimension tags + regression fields
- **expected**: blank unless user provides a reference response
- **tags**: `["regression"]`
- **id**: generate with `python3 -c "import uuid; print(uuid.uuid4())"`
- **target**: `regression_target` from Phase 0

### Row B — Generalized Row

Rewrite the input to remove specifics that make it a regression test, keeping the
failure-relevant pattern. Goal: organic-looking coverage diversity.

Generalisation examples:
- `"UPI payment apps in India"` (scope_ignored) → different geography + category not already in the dataset
- `"PLG-first B2B devtools under $500M ARR"` (intent_misparse) → same jargon pattern, different market
- `"social networking in 2008"` (temporal_override) → only add if the domain isn't already covered

Before finalising Row B, check what's already in the coverage target. If a similar row already
exists, pick a different generalisation.

- **metadata**: dimension tags only (no `failure_mode`, `regression`, `source_ticket`)
- **tags**: `[]`
- **id**: generate a new UUID
- **target**: `coverage_target` from Phase 0

---

## Phase 5: Output & Append

Present both rows clearly labeled with their target:

```
ROW A → <regression target name>:
<formatted row>

ROW B → <coverage target name>:
<formatted row>
```

Ask: "Should I append both, just one, or neither?"

### Appending to local CSV

Use the Edit tool to append the new line after the last row. Do not rewrite the file.

### Appending to an eval platform

Use the platform's SDK or MCP tool to insert the row. Generic pattern:

```python
# Adapt to your platform's SDK
dataset.insert(
    input="<cleaned input>",
    expected=None,
    metadata={"input_type": "...", "failure_mode": "...", ...},
    tags=["regression"]
)
```

---

## Handling Latency Tickets

Latency complaints can't be tested with a content eval:

1. Still generate Row A for the regression dataset (useful for load testing).
2. For Row B, skip the content dataset. Instead check if `perf-test-queries.txt` exists
   in the datasets directory; if not, create it. Append the PII-stripped input.
3. Tell the user: "This failure mode needs a latency monitor, not an LLM judge."

---

## Batch Mode

If the user passes multiple tickets, process all through Phases 1–4 first, then present all
rows grouped by target file before asking for a single confirmation.
