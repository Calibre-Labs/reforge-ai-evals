---
name: eval-llm-judge
description: >
  Write LLM-as-judge evaluator prompts for AI products. Use this skill whenever Sandhya needs
  to evaluate semantic properties of AI outputs that cannot be checked programmatically —
  ranking quality, tone, factual accuracy, edge case handling, reference alignment. Also use
  when auditing existing judge prompts for bias, vagueness, or compound criteria. Output is a
  judge prompt string and a Python runner function, saved to the project's evaluators file.
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
- **Ranking correctness**: are the top 3 companies the right ones in the right order?
- **Edge case handling**: did the agent appropriately flag ambiguity or decline gracefully?
- **Reference alignment**: does the output agree with a gold-standard expected response?
- **Tone and framing**: is the hedging appropriate for a speculative claim?
- **Faithfulness**: does the output stay within what the cited sources actually say?

Do NOT write an LLM judge for:
- Properties a code check can handle (count, format, presence) — these are cheaper and faster
- Compound criteria — write one judge per criterion, not one judge that checks everything

---

## Workflow

### Step 1 — Define exactly ONE criterion

The most common failure in judge design is compound criteria: "Is the output accurate, well-formatted,
and appropriately hedged?" This produces judges that are hard to calibrate and whose scores are
uninterpretable — a 0 could mean any of three things.

Write the criterion as one sentence that completes: *"A good output [verb phrase]."*

Good: "A good output ranks the top 3 companies in defensible order based on the stated metrics."
Good: "A good output explicitly states its interpretation when the query is ambiguous."
Bad: "A good output is accurate, well-cited, and appropriately hedged." (three criteria)

If you're tempted to write a compound criterion, split it into two judges.

### Step 2 — Write binary or ternary pass/fail definitions

**Binary (PASS/FAIL)** is the default. It forces the judge to commit and produces clean metrics.

**Ternary (PASS/BORDERLINE/FAIL)** is useful when there is a genuinely meaningful middle ground —
not "I'm not sure", but "the output is partially correct in a specific way." Use BORDERLINE when:
- The criterion has a legitimate gray zone (e.g., ranking order is debatable because two companies
  have comparable metrics)
- You want to distinguish "clearly wrong" from "wrong but understandable"

Do not use a 1–5 Likert scale. It collapses to 3s and 4s and tells you nothing.

Write definitions for each level that are:
- **Specific**: reference the criterion, not generic quality
- **Mutually exclusive**: a judge should not reasonably assign two levels to the same output
- **Grounded**: name what counts as evidence, not just "good" vs "bad"

### Step 3 — Write 3 few-shot examples

The examples are the most important part of the prompt. They calibrate the judge's interpretation
of the criterion and tell it what evidence to look for.

Required: **one clear PASS, one clear FAIL, one BORDERLINE**.

Rules for good examples:
1. **The borderline example is the most valuable.** It shows the judge what the gray zone looks like
   and prevents it from defaulting to binary extremes. Spend the most time on this one.
2. **Use real-looking outputs**, not toy ones. The output in the example should look like what your
   model actually produces — same formatting, similar length, same hedging patterns.
3. **Write the critique before the score.** The critique teaches the judge *why* to assign a score,
   not just *what* score to assign. The judge should be able to derive the score from the critique.
4. **Don't use inputs from your eval dataset.** Example inputs and outputs should be entirely
   distinct from the queries in your test set, to avoid contaminating judge behavior.
5. **Match the domain.** If you're evaluating a market map agent, use market map examples.
   Don't use generic QA examples — the judge will pattern-match to the wrong signals.

### Step 4 — Require structured output

The judge's output should be a JSON object, with the critique *before* the score:

```json
{"critique": "2-3 sentence explanation of why this output passes/fails", "score": "PASS"}
```

Critique-first ordering matters: it forces the judge to reason before committing to a score,
which produces more reliable results than score-first or score-only formats.

### Step 5 — Validate the judge against human labels

Before using a judge in production evals, validate it:

1. Label 20–40 outputs by hand (10–20 PASS, 10–20 FAIL)
2. Run the judge on the same outputs
3. Calculate **TPR** (when human says PASS, judge also says PASS) and **TNR** (when human says FAIL,
   judge also says FAIL)
4. Target: TPR > 90% and TNR > 90%. Minimum viable: both > 80%
5. If failing, read the mismatches — they reveal criterion ambiguity or missing example coverage

If a judge consistently fails on a specific sub-type of output, add a few-shot example covering
that sub-type. If the criterion itself is ambiguous, rewrite it before adding more examples.

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
- **BORDERLINE**: [Specific description of the gray zone, if applicable. Remove if binary.]

## Few-Shot Examples

### Example 1 — PASS
Input: "[example input]"
Output excerpt: "[example output]"
Result: {{"critique": "[why this passes]", "score": "PASS"}}

### Example 2 — FAIL
Input: "[example input]"
Output excerpt: "[example output]"
Result: {{"critique": "[why this fails]", "score": "FAIL"}}

### Example 3 — BORDERLINE
Input: "[example input]"
Output excerpt: "[example output]"
Result: {{"critique": "[why this is on the line]", "score": "BORDERLINE"}}

---

Now evaluate:

Input: {input}
Output: {output}

Respond with JSON only:
{{"critique": "<2-3 sentence explanation>", "score": "PASS" | "FAIL" | "BORDERLINE"}}
"""
```

---

## Runner Function Template

```python
def my_judge(output: str, input: str, expected: str = None) -> dict:
    """
    LLM judge for [criterion name].
    Returns: {"score": 0.0|0.5|1.0, "metadata": {"critique": str, "label": str}}
    """
    import anthropic, json, re

    client = anthropic.Anthropic()
    prompt = JUDGE_PROMPT.format(input=input, output=output)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()

    # Strip markdown fences if present
    text = re.sub(r'^```(?:json)?\n?', '', text)
    text = re.sub(r'\n?```$', '', text)

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return {"score": 0.0, "metadata": {"critique": "Failed to parse response", "raw": text}}

    score_map = {"PASS": 1.0, "BORDERLINE": 0.5, "FAIL": 0.0}
    return {
        "score": score_map.get(result.get("score", "FAIL"), 0.0),
        "metadata": {
            "critique": result.get("critique", ""),
            "label": result.get("score", "FAIL")
        }
    }
```

---

## Working Notes

- **One criterion per judge, always.** This is the rule most often violated. A judge that checks
  two things at once cannot be improved — you don't know which criterion is failing. Split compound
  criteria before anything else.

- **The borderline example is more valuable than the pass example.** Most judges default to PASS
  on ambiguous cases unless trained otherwise. The borderline example shows what "trying but not
  quite" looks like, which is often the most common failure mode in production.

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
  A weaker judge model introduces noise that looks like model variation. For market map evals,
  claude-sonnet-4-6 is the minimum; claude-opus-4-6 is preferable for nuanced ranking quality
  judgments.

- **Re-validate judges when the prompt changes.** If you update the system prompt (e.g., adding
  few-shot examples), re-run your human-labeled validation set. Prompt changes shift output
  distributions, which can invalidate a previously calibrated judge.

- **For reference judges specifically**: the gold-standard expected answer should be written by
  a domain expert, not generated by the same model you're evaluating. Using model-generated
  expected outputs as the reference creates circular evaluation — the judge will reward outputs
  that sound like the model, not outputs that are correct.
