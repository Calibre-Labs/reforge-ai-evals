---
name: llm-align
description: >
  Analyze alignment between LLM judge scores and human labels in Braintrust experiments.
  Use this skill whenever someone wants to evaluate how well an LLM judge agrees with human
  reviewers, calculate TPR/TNR, investigate disagreements, or improve a scorer prompt.
  Trigger on phrases like: "calculate TPR/TNR", "judge alignment", "where does the LLM
  disagree with humans", "improve my scorer", "why is the LLM getting these wrong",
  "compare human labels to LLM scores", "evaluate my eval", or any time someone shares
  a Braintrust experiment ID and asks about score quality or judge calibration.
  Also trigger when someone uploads a Braintrust URL and asks anything about score agreement.
---

# LLM Judge Alignment Analysis

You are helping analyze how well an LLM-based judge aligns with human labels in a
Braintrust experiment. Work through the five phases below in order, confirming with the
user at each ambiguous step before proceeding.

---

## Phase 1: Discovery

**Goal**: Figure out what fields exist in the experiment and which are human vs LLM scores.

### Steps

1. Ask the user for the Braintrust experiment ID or URL if not already provided.

2. Query root spans to discover all score fields. Use a large limit to avoid missing fields that only appear on a subset of rows — some judges may only run on certain row types:

```
select: id, span_id, scores
object_type: experiment
object_ids: ["<experiment-id>"]
where: is_root = true
limit: 500
```

3. Also query scorer spans to cross-check — some score fields may not have propagated to root spans if they were added after the experiment ran:

```
select: span_attributes.name, COUNT(*) as count
object_type: experiment
object_ids: ["<experiment-id>"]
where: span_attributes.type = 'score' OR span_attributes.purpose = 'scorer'
group_by: span_attributes.name
limit: 50
```

The union of fields found in root span `scores` objects AND scorer span names is your complete list of judges.

4. From the root span results, extract:
   - All keys present in `scores` objects
   - For each key: min, max, distinct values (to tell binary 0/1 from continuous)
   - Count of rows where each field is null

5. Count rows missing any scores entirely:
```
where: is_root = true AND scores IS NULL
```

6. Present your findings clearly:
   - List all score fields with their value ranges
   - Flag which look like human labels (binary 0/1, often named things like `scope_validator`, `human_*`, `ground_truth`) vs LLM judges (often named after the criterion, may have fractional values)
   - Report how many rows have missing scores

7. **Ask the user to confirm**: "Which field is the human label and which is the LLM judge score? I'll skip rows where either is missing — is that OK?"

### Technical notes

- Field names with hyphens MUST use bracket notation in SQL: `scores["metric-scope"]` not `scores.metric-scope`
- Root spans are where scores roll up — always filter `is_root = true` for this analysis
- The `id` field on a root span ≠ its `span_id`. You'll need `span_id` later for trace queries; always select both

---

## Phase 2: Confusion Matrix + TPR/TNR

**Goal**: Compute the full confusion matrix and key classification metrics.

### Setup

- **Positive (1)** = the human label value the user defines as "pass" (default: 1)
- **Negative (0)** = the other value (default: 0)
- **Threshold**: for continuous LLM scores, default to ≥ 0.5 = predicted positive. Ask if the score looks continuous.

### Query

Use a GROUP BY to get all four cells at once:

```
select: scores.<human_field> as human_label, scores["<llm_field>"] as llm_score, COUNT(*) as count
object_type: experiment
object_ids: ["<experiment-id>"]
where: is_root = true AND scores.<human_field> IS NOT NULL AND scores["<llm_field>"] IS NOT NULL
group_by: scores.<human_field>, llm_score
```

Apply threshold client-side if needed (the SQL engine may not support CASE WHEN on hyphenated fields cleanly).

### Report

Present:

| | LLM: Positive | LLM: Negative |
|---|---|---|
| **Human: Positive** | TP = N | FN = N |
| **Human: Negative** | FP = N | TN = N |

Then:
- **TPR** (sensitivity/recall) = TP / (TP + FN) — how well the LLM catches true positives
- **TNR** (specificity) = TN / (TN + FP) — how well the LLM rejects true negatives
- Total rows used, rows skipped (missing scores)

Interpret the numbers for the user — don't just show the math. E.g.: "TPR of 85% means the judge misses 15% of cases your human reviewers would pass."

---

## Phase 3: Disagreement Investigation

**Goal**: Understand *why* the LLM got each disagreement wrong by reading the scorer's reasoning.

### Step 1: Pull disagreement rows

```
select: id, span_id, input, scores.<human_field> as human_label, scores["<llm_field>"] as llm_score
object_type: experiment
object_ids: ["<experiment-id>"]
where: is_root = true 
  AND scores.<human_field> IS NOT NULL 
  AND scores["<llm_field>"] IS NOT NULL
  AND scores.<human_field> != scores["<llm_field>"]
limit: 50
```

Note: if the LLM score is continuous and you're using a threshold, the `!=` filter won't work directly. In that case pull all rows and filter manually.

### Step 2: Get scorer reasoning for each disagreement

For each disagreement row, fetch the full trace. **Critical**: use the `span_id` (not `id`) of the root span as the trace identifier.

```
select: span_id, span_attributes, input, output
object_type: experiment
object_ids: ["<experiment-id>"]
where: root_span_id = '<span_id_of_root>' AND span_attributes.name = '<llm_judge_field_name>'
shape: traces
limit: 20
```

The scorer span's `output` contains the LLM's reasoning — typically `{"score": 0/1, "metadata": {"choice": "PASS/FAIL", "rationale": "..."}}`.

### Step 3: Summarize

For each disagreement row, show:
- The input query
- Human verdict vs LLM verdict
- The LLM's actual reasoning (verbatim from the `rationale` field)
- Your read on *why* the LLM got it wrong

Group the errors into patterns — don't just list them one by one. Common patterns:
- **Too strict FNs**: LLM fails responses for a technically correct but pedantic reason the human overlooks
- **Too lenient FPs**: LLM passes responses that violate the spirit of the criterion
- **Ambiguous criteria**: the scoring rubric has a gap the LLM fills differently than humans would

---

## Phase 4: Prompt Fix Suggestions

**Goal**: Suggest targeted, surgical edits to the scorer prompt — not a full rewrite.

Based on the disagreement patterns from Phase 3:

1. Quote the specific part of the existing scorer prompt that's causing the issue
2. Propose the minimal change needed — a single sentence addition, a clarification to an example, a new edge case in the rubric
3. Explain how the change addresses the observed failure mode without overcorrecting

**Format for each suggestion:**

> **Issue**: [what's going wrong and in which cases]
> 
> **Current prompt text**: "[relevant excerpt]"
> 
> **Suggested change**: "[replacement or addition]"
> 
> **Why this helps**: [which disagreements it would fix, and why it won't break the passing cases]

Aim for 2-4 suggestions. Don't suggest rewriting the whole prompt — that tends to fix some things and break others.

---

## Phase 5: Few-Shot Example Suggestions

**Goal**: Identify the best 2-3 disagreement rows to add as labeled examples to the scorer prompt.

Good few-shot examples for a scorer have these properties:
- The case is genuinely ambiguous (not obviously right or wrong)
- The human verdict is clearly defensible and can be explained in 1-2 sentences
- The LLM's mistake was predictable (it reveals a systematic blind spot, not a one-off error)
- Adding it as an example would generalize to similar future inputs

### Selection criteria

- **One "too strict" FN**: A case where the LLM failed something the human passed — include the human's reasoning as the correct label
- **One "too lenient" FP**: A case where the LLM passed something the human failed
- **One borderline case** (if it exists): Something that's genuinely hard and shows the nuance you want the judge to have

### Output format

For each suggested example, draft the actual text to add to the scorer prompt:

```
### Example N — [PASS/FAIL]
Input: "[query]"
Output excerpt: "[relevant part of the system output]"
{"reason": "[why this is PASS/FAIL — in the voice of the scorer]", "score": "[PASS/FAIL]"}
```

Explain why you chose each example and what failure mode it targets.

---

## Reminders & Gotchas

- **Hyphenated field names**: Always `scores["field-name"]`, never `scores.field-name`
- **id vs span_id**: Root spans have a separate `id` (event identifier) and `span_id` (trace identifier). For trace queries, use `span_id` as the `root_span_id`. Always `SELECT id, span_id` when you'll need to do trace lookups later.
- **Null scores**: Always filter `IS NOT NULL` on both fields before computing metrics. Report how many rows you skipped.
- **Human review timing**: In some experiments, `scope_validator` or other human labels may be updated by reviewers after the experiment runs. If you see a row appear in a disagreement query but then show agreement when you fetch it individually, note this to the user — the label was likely updated.
- **Scorer span name**: The span for the LLM judge has `span_attributes.name` equal to the score field name (e.g., `"metric-scope"`). If your WHERE clause returns nothing, try querying without the name filter to see what span names actually exist in the trace.
- **shape=traces**: Required when you want to see all spans in a trace — the default `spans` shape may not return child spans in the expected way.
