---
name: llm-align
description: >
  Analyze alignment between LLM judge scores and human labels in an eval dataset.
  Use this skill whenever someone wants to evaluate how well an LLM judge agrees with human
  reviewers, calculate TPR/TNR, investigate disagreements, or improve a scorer prompt.
  Trigger on phrases like: "calculate TPR/TNR", "judge alignment", "where does the LLM
  disagree with humans", "improve my scorer", "why is the LLM getting these wrong",
  "compare human labels to LLM scores", "evaluate my eval", or any time someone shares
  eval results and asks about score quality or judge calibration.
---

# LLM Judge Alignment Analysis

You are helping analyze how well an LLM-based judge aligns with human labels in an eval
dataset. Work through the five phases below in order, confirming with the user at each
ambiguous step before proceeding.

The methodology works regardless of eval platform (Braintrust, LangSmith, custom CSV/JSONL,
or any other format). Phase 1 covers how to get the data you need from different sources.

---

## Phase 1: Discovery

**Goal**: Figure out what score fields exist and which are human labels vs. LLM judge scores.

### Step 1 — Get the eval results

Ask the user how their eval results are stored:

**Option A — Local file (CSV or JSONL)**
Read the file directly. Look for columns or fields that contain numeric or categorical scores.
Common patterns: `human_score`, `llm_score`, `<judge_name>_score`, `label`, `rating`.

**Option B — Eval platform (Braintrust, LangSmith, etc.)**
Ask for the experiment/run ID or URL. Use the platform's API or MCP tools to fetch rows.
You want: each row's input, the human label field, and the LLM judge score field.

Typical Braintrust query (adapt syntax to other platforms):
```
select: id, span_id, scores
object_type: experiment
object_ids: ["<experiment-id>"]
where: is_root = true
limit: 500
```

**Option C — The user pastes results directly**
Accept a JSON array, CSV snippet, or any structured format. Parse it in-context.

### Step 2 — Identify human vs. LLM score fields

From the data, extract all score fields. For each:
- What are the distinct values? (binary 0/1, categorical PASS/FAIL, continuous 0–1)
- How many rows have this field populated?
- Does the name suggest human or LLM origin? (e.g., `human_*`, `ground_truth`, `label` are likely human; criterion-named fields are likely LLM)

Present your findings and **ask the user to confirm**: "Which field is the human label and which
is the LLM judge score? I'll skip rows where either is missing — is that OK?"

### Technical notes (platform-specific)

- **Braintrust**: hyphenated field names need bracket notation: `scores["metric-scope"]` not `scores.metric-scope`. Root spans are where scores aggregate — filter `is_root = true`. The `id` field ≠ `span_id`; select both for later trace lookups.
- **CSV/JSONL**: parse scores as floats; watch for string "PASS"/"FAIL" that need mapping to 1.0/0.0.

---

## Phase 2: Confusion Matrix + TPR/TNR

**Goal**: Compute the full confusion matrix and key classification metrics.

### Setup

- **Positive (1)** = the human label value the user defines as "pass" (default: 1 or "PASS")
- **Negative (0)** = the other value (default: 0 or "FAIL")
- **Threshold**: for continuous LLM scores (0.0–1.0), default to ≥ 0.5 = predicted positive. Ask if the score looks continuous.

### Compute the confusion matrix

Group rows into four cells:
- **TP**: human = positive, LLM = positive
- **FN**: human = positive, LLM = negative (judge misses a real pass)
- **FP**: human = negative, LLM = positive (judge passes something that should fail)
- **TN**: human = negative, LLM = negative

### Report

| | LLM: Positive | LLM: Negative |
|---|---|---|
| **Human: Positive** | TP = N | FN = N |
| **Human: Negative** | FP = N | TN = N |

Then:
- **TPR** (sensitivity/recall) = TP / (TP + FN) — how well the LLM catches true positives
- **TNR** (specificity) = TN / (TN + FP) — how well the LLM rejects true negatives
- Total rows used, rows skipped (missing scores)

Interpret the numbers — don't just show the math. E.g.: "TPR of 85% means the judge misses
15% of cases your human reviewers would pass."

---

## Phase 3: Disagreement Investigation

**Goal**: Understand *why* the LLM got each disagreement wrong by reading the scorer's reasoning.

### Step 1 — Pull disagreement rows

Filter to rows where human label ≠ LLM score (accounting for threshold if continuous).
Show up to 20 disagreements — enough to find patterns without overwhelming.

For each row, gather:
- The input
- The AI output (if available)
- Human verdict vs. LLM verdict
- The LLM's reasoning (from the scorer's trace/metadata if available)

### Step 2 — Retrieve scorer reasoning

If your eval platform stores scorer reasoning (a critique or rationale alongside the score):
- **Braintrust**: fetch the scorer span using `root_span_id = '<span_id>'` and look for `output.metadata.rationale` or similar
- **LangSmith**: check the run's feedback or evaluator output fields
- **Custom**: look for a `critique`, `rationale`, or `reason` field in the eval output

If no reasoning is stored, re-run the judge on the disagreement rows locally and capture the
reasoning output.

### Step 3 — Summarize patterns

Group errors into patterns — don't list them one by one. Common patterns:
- **Too strict FNs**: LLM fails responses for a pedantic reason humans overlook
- **Too lenient FPs**: LLM passes responses that violate the spirit of the criterion
- **Ambiguous criteria**: the rubric has a gap the LLM fills differently than humans would

---

## Phase 4: Prompt Fix Suggestions

**Goal**: Suggest targeted, surgical edits to the scorer prompt — not a full rewrite.

Based on the disagreement patterns from Phase 3:

1. Quote the specific part of the existing scorer prompt that's causing the issue
2. Propose the minimal change — a single sentence addition, a clarification to an example, a new edge case in the rubric
3. Explain how the change addresses the observed failure mode without overcorrecting

**Format for each suggestion:**

> **Issue**: [what's going wrong and in which cases]
>
> **Current prompt text**: "[relevant excerpt]"
>
> **Suggested change**: "[replacement or addition]"
>
> **Why this helps**: [which disagreements it would fix, and why it won't break the passing cases]

Aim for 2–4 suggestions. Don't suggest rewriting the whole prompt.

---

## Phase 5: Few-Shot Example Suggestions

**Goal**: Identify the best 2–3 disagreement rows to add as labeled examples to the scorer prompt.

Good few-shot examples have these properties:
- The case is genuinely ambiguous (not obviously right or wrong)
- The human verdict is clearly defensible and can be explained in 1–2 sentences
- The LLM's mistake was predictable (reveals a systematic blind spot, not a one-off error)
- Adding it would generalize to similar future inputs

### Selection criteria

- **One "too strict" FN**: A case the LLM failed that the human passed — include human reasoning as the correct label
- **One "too lenient" FP**: A case the LLM passed that the human failed
- **A second FAIL case** covering a different failure mode than the first — shows the nuance you want

### Output format

For each suggested example, draft the text to add to the scorer prompt:

```
### Example N — [PASS/FAIL]
Input: "[input]"
Output excerpt: "[relevant part of the AI output]"
{"reason": "[why this is PASS/FAIL — in the voice of the scorer]", "score": "[PASS/FAIL]"}
```

Explain why you chose each example and what failure mode it targets.

---

## Reminders & Gotchas

- **Threshold matters**: A continuous score of 0.49 vs 0.51 may swing a cell. Always clarify the threshold before computing the matrix, and report it alongside the results.
- **Null scores**: Always filter out rows where either score is missing before computing metrics. Report how many rows were skipped.
- **Human review timing**: In some platforms, human labels may be updated after the experiment runs. If a row appears in disagreement queries but shows agreement when fetched individually, note this — the label was likely updated.
- **Braintrust field names with hyphens**: Use `scores["field-name"]`, never `scores.field-name`.
- **Small samples**: With fewer than 30 human-labeled rows, TPR and TNR estimates are noisy. Report this caveat explicitly.
