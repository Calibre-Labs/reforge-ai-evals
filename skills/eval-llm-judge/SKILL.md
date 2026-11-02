---
name: eval-llm-judge
description: >
  Write LLM-as-judge evaluator prompts for AI products. Use this skill whenever you need to
  evaluate semantic properties of AI outputs that cannot be checked programmatically —
  output quality, tone, factual accuracy, edge case handling, reference alignment. Also use
  when auditing existing judge prompts for bias, vagueness, or compound criteria. Output is a
  judge prompt and a runner in the project's own scorer format (a Python runner when the project
  has none), saved where the project keeps its evaluators.
---

# LLM Judge Evaluator Skill

An LLM-as-judge evaluator uses a language model to score another model's output against a
defined criterion. It handles semantic properties that code-based checks cannot: is the ranking
defensible? Did the agent handle ambiguity gracefully? Does the output align with the reference?

The tradeoff: judges are slower, more expensive, and non-deterministic. They require calibration
against human labels before you can trust their scores. Use them only after code-based checks have
covered the structural requirements.

## When to use this skill

Write an LLM judge when the property requires reasoning that a human reviewer would apply:
- **Output correctness**: are the results correct and in a defensible order or format?
- **Edge case handling**: did the agent appropriately flag ambiguity or decline gracefully?
- **Reference alignment**: does the output agree with a gold-standard expected response?
- **Tone and framing**: is the hedging appropriate for a speculative or high-stakes claim?
- **Faithfulness**: does the output stay within what the cited sources actually say?

Do NOT write an LLM judge for:
- Properties a code check can handle (count, format, presence) — these are cheaper and faster
- Compound criteria — write one judge per criterion, not one judge that checks everything

---

## Workflow

### Step 1 — Find the project's scorer contract and judge helper

Before drafting, look for where the project already keeps its evaluators: a `scorers/` or `evals/`
folder, a types or contract file, existing judges, a README that says how they run. If there is
one, write the judge in that language and follow the contract exactly: the function signature,
the return shape, the file name and folder. If the project has a helper that calls the judge
model, use it rather than the runner template below, so every judge shares one model, one output
schema and one way of handling errors.

For example, Mapper's course scorers live in `scorers/course/`, one TypeScript file per scorer.
Each judge exports its `PROMPT_TEMPLATE` and default-exports a function that fills the template
and calls `judge(name, prompt)` from `scorers/course/types.ts`. That helper asks Gemini 3.5
Flash-Lite, at temperature 0, for `{critique, score}` and returns
`{ name, score: 0 | 1, metadata: { reason } }`, with the critique as the reason.

If the project's judge model is weaker than the guidance under Working Notes, keep it for
consistency with the other judges, say so, and lean harder on Step 7: a weaker judge needs
alignment more.

In JavaScript or TypeScript, fill the prompt's slots with a replacer function
(`template.replace("{session}", () => text)`). A plain string replacement reads `$&`, `` $` `` and
`$'` in the session text as patterns, and sessions full of dollar figures will hit that.

Use the Python runner template below only when the project has no contract of its own.

### Step 2 — Define exactly ONE criterion

The most common failure in judge design is compound criteria: "Is the output accurate, well-formatted,
and appropriately hedged?" This produces judges that are hard to calibrate and whose scores are
uninterpretable — a 0 could mean any of three things.

Write the criterion as one sentence that completes: *"A good output [verb phrase]."*

Good: "A good output ranks the top 3 companies in defensible order based on the stated metrics."
Good: "A good output explicitly states its interpretation when the query is ambiguous."
Bad: "A good output is accurate, well-cited, and appropriately hedged." (three criteria)

If you're tempted to write a compound criterion, split it into two judges.

### Step 3 — Write binary pass/fail definitions

**Binary (PASS/FAIL)** forces the judge to commit and produces clean metrics.

Do not use a 1–5 Likert scale. It collapses to 3s and 4s and tells you nothing. Do not add a
BORDERLINE tier — it becomes a crutch and makes TPR/TNR harder to interpret.

Write definitions for each level that are:
- **Specific**: reference the criterion, not generic quality
- **Mutually exclusive**: a judge should not reasonably assign two levels to the same output
- **Grounded**: name what counts as evidence, not just "good" vs "bad"

### Step 4 — Write 3 few-shot examples

The examples are the most important part of the prompt. They calibrate the judge's interpretation
of the criterion and tell it what evidence to look for.

Required: **one clear PASS, two clear FAILs** covering different failure modes.

Rules for good examples:
1. **Use two distinct FAIL examples.** Different failure modes teach the judge where the line is better than a single example. Spend more time on these than on the PASS.
2. **Use real-looking outputs**, not toy ones. The output in the example should look like what your
   model actually produces — same formatting, similar length, same hedging patterns.
3. **Write the critique before the score.** The critique teaches the judge *why* to assign a score,
   not just *what* score to assign. The judge should be able to derive the score from the critique.
4. **Don't use inputs from your eval dataset.** Example inputs and outputs should be entirely
   distinct from the queries in your test set, to avoid contaminating judge behavior.
5. **Match the domain.** Use examples from your actual product — same output format, same hedging
   patterns, same vocabulary. Don't use generic QA examples; the judge will pattern-match to the
   wrong signals.

### Step 5 — Require structured output

The judge's output should be a JSON object, with the critique *before* the score:

```json
{"critique": "2-3 sentence explanation of why this output passes/fails", "score": "PASS"}
```

Critique-first ordering matters: it forces the judge to reason before committing to a score,
which produces more reliable results than score-first or score-only formats.

### Step 6 — Gate the judge, and give it the evidence it needs

**Gate first.** If the criterion can't apply to a session, don't call the judge. Check that in
code and return a pass whose reason says why. Mapper's judges do this: "delivers what was
confirmed" skips sessions where nothing was proposed before the first output, "answers for the
year asked" skips sessions that name no other year, and "metric scope" skips sessions with no
table. If the project's contract supports skipping a row (a null score), use that instead. The
gate saves judge calls, and the reason lets a reader tell "passed" from "had nothing to check".

**Then give the judge what it needs to decide.** A judge can only judge what is in its prompt. If
the criterion needs evidence the trace doesn't hold, the scorer has to fetch it. Mapper's "a
source supports each figure" judge downloads each cited page and passes only the passages that
mention the companies or figures shown. When you do this:
- Save what you fetched, so a re-score reads the same text even if the page changes later.
- Mark evidence you couldn't get ("could not be read: 403") instead of dropping it, and decide
  how it counts. Mapper counts a figure backed only by unreadable pages as unsupported.
- Tell the judge to decide only from the evidence given, not from what it knows.

### Step 7 — Validate the judge against human labels

**Read verdicts before you label.** Run the judge on the recorded runs you'll report and read
about ten verdicts, passes and fails, against the outputs. This catches a criterion the judge
misreads before you spend an hour labeling.

Before using a judge in production evals, validate it:

1. Label 20–40 outputs by hand (10–20 PASS, 10–20 FAIL)
2. Run the judge on the same outputs
3. Calculate **TPR** (when human says PASS, judge also says PASS) and **TNR** (when human says FAIL,
   judge also says FAIL)
4. Target: TPR > 90% and TNR > 90%. Minimum viable: both > 80%
5. If failing, read the mismatches — they reveal criterion ambiguity or missing example coverage

If a judge consistently fails on a specific sub-type of output, add a few-shot example covering
that sub-type. If the criterion itself is ambiguous, rewrite it before adding more examples.

**Score borderline cases twice.** Temperature 0 doesn't make a judge deterministic. Mapper's
"answers for the year asked" judge gave the same output a FAIL and then a PASS. Run the judge
twice over the labeled set. A row whose verdict flips is a borderline case: treat it as a
disagreement to read, add a few-shot example near it or tighten the definition, and don't report
a single run of it as the verdict.

---

## Prompt Template

```python
JUDGE_PROMPT = """\
You are evaluating [AI product description].

## Evaluation Criterion
**[Criterion Name]**: [One-sentence definition of what a good output does.]

## Scoring
- **PASS**: [Specific description of what qualifies as a pass, grounded in the criterion.]
- **FAIL**: [Specific description of what qualifies as a fail.]

## Few-Shot Examples

### Example 1 — PASS
Input: "[example input]"
Output excerpt: "[example output]"
Result: {{"critique": "[why this passes]", "score": "PASS"}}

### Example 2 — FAIL
Input: "[example input]"
Output excerpt: "[example output]"
Result: {{"critique": "[why this fails]", "score": "FAIL"}}

### Example 3 — FAIL
Input: "[example input]"
Output excerpt: "[example output showing a different failure mode]"
Result: {{"critique": "[why this fails]", "score": "FAIL"}}

---

Now evaluate:

Input: {input}
Output: {output}
"""
```

---

## Runner Function Template

Use the project's own judge helper if it has one (Step 1). Otherwise, this runner uses structured
outputs, so the response is always schema-valid JSON — no fence-stripping or parse-failure path. `critique` is declared before `score` so it is written first.

```python
from typing import Literal
from pydantic import BaseModel

JUDGE_MODEL = "claude-opus-5"  # one place to upgrade; re-validate TPR/TNR after changing it

class JudgeResult(BaseModel):
    critique: str
    score: Literal["PASS", "FAIL"]

def my_judge(output: str, input: str, expected: str = None) -> dict:
    """
    LLM judge for [criterion name].
    Returns: {"score": 0.0|1.0|None, "metadata": {"critique": str, "label": str}}
    score is None when the judge didn't produce a verdict (refusal / truncation) —
    that row is skipped, not silently counted as FAIL.
    """
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=JUDGE_MODEL,
        max_tokens=16000,  # thinking counts toward max_tokens
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(input=input, output=output)}],
        output_format=JudgeResult,
    )
    result = response.parsed_output
    if result is None:
        return {"score": None, "metadata": {"error": f"no verdict (stop_reason={response.stop_reason})"}}
    return {
        "score": 1.0 if result.score == "PASS" else 0.0,
        "metadata": {"critique": result.critique, "label": result.score},
    }
```

---

## Working Notes

- **Name the rubric line and trace codes.** Put the rubric line and the trace code numbers the judge
  checks in the scorer's header comment and in its name where results are shown, so anyone reading
  a score can trace it back to the failure that motivated it.

- **One criterion per judge, always.** This is the rule most often violated. A judge that checks
  two things at once cannot be improved — you don't know which criterion is failing. Split compound
  criteria before anything else.

- **The FAIL examples are more valuable than the PASS example.** Most judges default to PASS
  on ambiguous cases unless trained otherwise. Use two distinct FAIL examples covering different
  failure modes to teach the judge where the line is.

- **Don't use your eval dataset inputs as judge examples.** This is data leakage — the judge has
  effectively been pre-told the answer for those inputs. Use different examples that illustrate
  the same criterion.

- **Critique before score, always.** Putting the critique first in the JSON output forces the model
  to reason before committing. Putting the score first produces post-hoc rationalization, which
  is less reliable.

- **Validate TPR and TNR separately.** A judge can have 90% overall accuracy but 70% TNR — it's
  too lenient, marking real failures as passes. Track both rates. If TNR is low, make the FAIL
  definition more specific and add a clear FAIL example.

- **Model choice matters for judge quality.** Use the strongest model you can afford for judges.
  A weaker judge model introduces noise that looks like model variation. Use the current
  Opus-tier model for nuanced semantic judgments; current Sonnet-tier is the floor. Changing
  `JUDGE_MODEL` is a judge change — re-run the human-labeled validation set afterwards.

- **Re-validate judges when the prompt changes.** If you update the system prompt (e.g., adding
  few-shot examples), re-run your human-labeled validation set. Prompt changes shift output
  distributions, which can invalidate a previously calibrated judge.

- **For reference judges specifically**: the gold-standard expected answer should be written by
  a domain expert, not generated by the same model you're evaluating. Using model-generated
  expected outputs as the reference creates circular evaluation — the judge will reward outputs
  that sound like the model, not outputs that are correct.
