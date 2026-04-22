---
name: ticket-to-eval
description: >
  Strip PII from a customer support ticket or Braintrust trace and convert it into
  eval dataset rows. Produces two outputs: a regression dataset row (close to the
  original query, tagged with failure_mode) and a generalized dataset row (abstracted
  for broader coverage). Supports Braintrust MCP for dataset discovery and local CSV
  fallback. Use this skill whenever someone shares a support ticket, user complaint,
  or raw trace and wants to turn it into eval data. Trigger on: "add this ticket to
  the dataset", "convert this trace to an eval", "strip PII from this complaint",
  "turn this into a test case".

  Usage:
    /ticket-to-eval                  — auto-detect datasets (local CSV or Braintrust)
    /ticket-to-eval braintrust       — use Braintrust MCP for dataset discovery
    /ticket-to-eval local            — use local CSV files only
---

# Ticket → Eval Conversion

You are converting a customer support ticket or Braintrust trace into two eval dataset
rows: a regression row (exact query, tagged with failure_mode) and a generalized row
(abstracted for broader coverage). Work through the five phases below.

---

## Phase 0: Dataset Discovery

Check `$ARGUMENTS` for a dataset target hint:
- `braintrust` or a Braintrust project name → use Braintrust MCP (see Braintrust path below)
- `local` or blank → glob for local CSVs (see Local path below)
- If unclear, ask: "Should I look for datasets in Braintrust or local CSV files?"

### Braintrust path

1. Ask the user for the Braintrust project name if not already in `$ARGUMENTS`.
2. List available datasets in that project:
   ```
   list_recent_objects(object_type="dataset", project_name="<project>", limit=20)
   ```
3. Present the dataset list and ask the user to pick:
   - **regression target** (the dataset that tracks real failures — equivalent to `regression-dataset.csv`)
   - **coverage target** (the dataset to add generalized coverage rows to — equivalent to `week2-dataset.csv`)
4. Resolve both to their dataset IDs:
   ```
   resolve_object(object_type="dataset", project_name="<project>", object_name="<name>")
   ```
5. Optionally infer schema of the coverage target to confirm field names match what you'll generate.

Store: `regression_target` and `coverage_target` as either `{type: "braintrust", id: "<id>", name: "<name>", project: "<project>"}` or `{type: "local", path: "<path>"}`.

### Local path

1. Glob for CSV files in the project that look like Braintrust datasets:
   ```
   Glob("**/*.csv") → filter to files whose first line contains "input,metadata"
   ```
2. Identify which file is the regression dataset (look for "regression" in the filename or a `regression` column in the metadata).
3. Present the list and ask the user to confirm regression target and coverage target.

Store as `{type: "local", path: "<relative path>"}`.

---

## Phase 1: Extract & Identify

Parse the input — it may be a CSV row, free-form complaint text, or Braintrust trace JSON.

Extract:
- **original_query**: the exact text the user submitted to the agent
- **complaint_summary**: what went wrong (1 sentence)
- **failure_mode**: classify as one of:
  - `jargon_misparse` — agent ignored or misread a jargon term (PLG, bootstrapped, ai-native, etc.)
  - `stale_entity` — agent ranked a company that is bankrupt, acquired, or defunct
  - `temporal_override` — historical/future query answered with current data
  - `geography_ignored` — geographic constraint ignored; wrong regional market returned
  - `currency_mismatch` — metrics returned in wrong or mixed currency with no disclosure
  - `hallucinated_citation` — source URL 404s or the publication doesn't exist
  - `implausible_metric` — a numeric figure is off by >5x from any credible estimate
  - `refused_valid_query` — agent declined to answer a query it should be able to handle
  - `latency` — response time complaint (not a content failure; flag separately)
  - `format_violation` — wrong number of companies, broken table, incomplete output
  - `other` — describe in a note field

---

## Phase 2: Strip PII

Scan the original query AND any surrounding context for PII. Replace in-place with
typed placeholders. Do NOT alter words that are not PII.

| PII type | Placeholder |
|---|---|
| Person name | `[USER_NAME]` |
| Email address | `[USER_EMAIL]` |
| Company / employer | `[USER_COMPANY]` |
| Session / trace ID | `[SESSION_ID]` |
| Internal dollar figure | `[INTERNAL_FIGURE]` |

**Rule**: market queries are rarely PII — preserve them exactly unless they contain
a person's name or the user's own company name submitted in a private context.

Show the cleaned query and ask the user to confirm before proceeding.

---

## Phase 3: Map to Dimensions

Tag the cleaned query. Use the schema you inferred from the coverage target in Phase 0,
or fall back to these standard UIG fields if none were found:

```json
{
  "query_type": "<direct_category | competitive_comps | acquisition_targets | historical_snapshot | future_speculative | segment_specific | validation | trend_evolution | edge_out_of_scope>",
  "domain": "<tech_saas | healthcare | financial | consumer_brand | industrial_other>",
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

- **input**: PII-stripped query (exact)
- **metadata**: full dimension tags + regression fields
- **expected**: blank unless user provides a reference response
- **tags**: `["regression"]`
- **id**: generate with `python3 -c "import uuid; print(uuid.uuid4())"`
- **target**: `regression_target` from Phase 0

### Row B — Generalized Row

Rewrite the query to remove specifics that make it a regression test, keeping the
failure-relevant pattern. Goal: organic-looking coverage diversity.

Generalisation examples:
- `"UPI payment apps in India"` (geography_ignored) → different geography + category not already in the dataset
- `"PLG-first B2B devtools under $500M ARR"` (jargon_misparse) → same jargon pattern, different market
- `"social networking in 2008"` (temporal_override) → only add if the domain isn't already covered

Before finalising Row B, check what's already in the coverage target:
- **Braintrust**: `sql_query(select="input, metadata", object_type="dataset", object_ids=["<coverage_id>"], limit=100)` then scan for similar queries
- **Local**: read the last 20 rows of the CSV

If a similar row already exists, pick a different generalisation.

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

### Appending to Braintrust

The Braintrust MCP has no write tool. Use the Python SDK:

```python
import braintrust

dataset = braintrust.init_dataset(project="<project>", name="<dataset name>")
dataset.insert({
    "input": "<query>",
    "expected": "",
    "metadata": <metadata dict>,
    "tags": <tags list>
})
dataset.flush()
print("Done")
```

Run via Bash. Requires `BRAINTRUST_API_KEY` in the environment — check with
`echo $BRAINTRUST_API_KEY` first and prompt the user if it's missing.

### Appending to local CSV

Use the Edit tool to append the new line after the last row. Do not rewrite the file.

---

## Handling Latency Tickets

Latency complaints can't be tested with a content eval:

1. Still generate Row A for the regression dataset (useful for load testing).
2. For Row B, skip the content dataset. Instead check if `perf-test-queries.txt` exists
   in the datasets directory; if not, create it. Append the PII-stripped query.
3. Tell the user: "This failure mode needs a latency monitor, not an LLM judge."

---

## Batch Mode

If the user passes multiple tickets, process all through Phases 1–4 first, then
present all rows grouped by target file before asking for a single confirmation.
