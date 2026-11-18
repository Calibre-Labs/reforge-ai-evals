# Ch 5: Code-based Evaluation

In this lesson, you will learn how to write deterministic, code-based evaluations that run automatically on every prompt change and serve as the non-negotiable foundation of your eval suite.

As we learnt in the previous lesson, **The default path for automated evaluation should always be code-based because it's faster, cheaper, and 100% reproducible (deterministic).**

### Common Categories for Code-based Evals

> *Diagram idea: diagram - examples of trace codes that are a good fit for code-based evals*

Certain kinds of trace codes show up across products and are strong candidates for deterministic checks.

  - **Structure and format** **issues** appear whenever outputs are consumed by other systems. Missing fields, malformed JSON, or invalid schemas are easy to detect and expensive to ignore.
  - **Presence and coverage** **gaps** show up when outputs omit required elements. A pitch that never mentions market size. A summary that doesn’t cite sources. A recommendation that lacks a next step.
  - **Tool call failures** become visible in multi-step systems. Agents call tools that don’t exist, omit required parameters, or invoke steps out of order. These failures are mechanical, not conceptual.
  - **Search quality problems** surface in RAG and GREP based systems. If the right documents weren’t retrieved, the generation step never had a chance. Measuring retrieval accuracy directly is often easier than judging the final answer.

### What exactly is a code-based eval?

**A code-based evaluator is a Python function**. It takes a trace as input - or more precisely, the output string, tool call log, or structured response from your AI system - and returns a pass or fail. No LLM call. No probability distribution. One deterministic result, every time. That determinism is the point.

**Code-based evals are the bedrock of a reliable eval suite. They run on every prompt change, every model upgrade, every release candidate.** They tell you immediately when something that was working has broken. When you have them, you can move fast. When you don't, you're relying on vibe checks to catch regressions.

**The economics matter too. Code evals are fast and cheap — deterministic checks cost nothing per-run compared to LLM inference.** They can run in the critical path of your production pipeline to catch failures in real time, not just in offline testing. And they're 100% reproducible: the same input produces the same result every time, which means your eval results are comparable across versions.

This chapter covers what code-based evals look like, which trace codes they handle best, how to apply them to the Support Triage Agent, and how to build the infrastructure to run them across a dataset.

### What Code-Based Evals Look Like

> *Diagram idea: diagram - code-based eval taxonomy*

Every code-based eval has the same three-part anatomy.

**Inputs:** **the full trace.** Usually the complete response from your AI system — an output string, a JSON response, the sequence of tool calls, or some combination. Some evals also take the original user input to check context-dependent properties (did the output reference the correct ticket ID?).

**The check: the logic.** A condition, a pattern match, a schema validation, a count, a threshold comparison. Whatever you're measuring, it can be expressed precisely in code without requiring language understanding.

**The output: pass or fail, plus a reason string.** The reason string is not optional. When an eval fails on trace \#38 of 50, you need to know why without reading the full trace. "Output contains no valid category label" is useful. "False" is not.

#### **Example 1: Category checking for Support Triage**

The Support Triage Agent is supposed to classify each ticket into exactly one of three categories:

  - Technical
  - Billing, or
  - Feature Request.

This code-based eval checks that every response includes the correct label — not a paraphrase, not "billing issue," not a free-form description, but the exact string.

> *Diagram idea: diagram - show the code-based eval check\_category\_present below nicely formatted on a slide*

|  |
| :-: |
| \*def check\\\_category\\\_present(agent\\\_output: str) -\\\> tuple\\\[bool, str\\\]:\*    \*VALID\\\_CATEGORIES = {"Technical", "Billing", "Feature Request"}\*    \*found = \\\[c for c in VALID\\\_CATEGORIES if c in agent\\\_output\\\]\*    \*if len(found) == 0:\*        \*return False, f"No valid category label found in output"\*    \*if len(found) \\\> 1:\*        \*return False, f"Multiple category labels found: {found}"\*    \*return True, f"Single valid category found: {found\\\[0\\\]}"\* |

This is a code-based eval. It is eight lines long. It runs in microseconds. It gives an unambiguous result on every ticket in your dataset.

**The practical threshold: if you can write the success condition as a Python function in under ten lines, it belongs in code.** Every hour you spend writing an LLM judge for something code could check is an hour you didn't spend on the genuinely hard problems.

## Writing and Scaling Code-based Evals

Four trace property types are ideal for code-based evaluation: structure/format, presence and coverage, tool call success, and threshold checks.

### Structure and format

AI outputs are often required to conform to a schema: JSON with specific fields, a response that includes required sections, a character count under a UI limit. Code evals are the right tool here. Schema validation libraries exist for this. **These checks are especially important when your AI system feeds downstream pipelines — a malformed output that passes a vibe check can silently break production.**

**For the Support Triage Agent:** does the JSON response include both a category label and a priority level? Are all required fields present? Is the summary under 500 characters?

Below you can see an example of this kind of response schema check

> *Diagram idea: diagram - show the code-based eval check\_response\_schema below nicely formatted on a slide*

|  |
| :-: |
| REQUIRED\\\_FIELDS = {"category", "priority", "summary"} def check\\\_response\\\_schema(agent\\\_output: str) -\\\> tuple\\\[bool, str\\\]:    try:        data = json.loads(agent\\\_output)        missing = REQUIRED\\\_FIELDS - set(data.keys())        if missing:            return False, f"Missing required fields: {missing}"        return True, "Schema valid"    except json.JSONDecodeError:        return False, "Output is not valid JSON" |

### Presence and coverage

Does the output contain specific keywords, phrases, or identifiers? Does it reference the correct product name, the right ticket ID, the required policy language? **These are string-matching and regex problems. They're cheap to run and straightforward to debug.**

A concrete example: evaluating whether a conversational agent asks open-ended follow-up questions. The check is a keyword scan against a target set. If any open-ended question marker appears, the eval passes.

> *Diagram idea: diagram - show the code-based eval check\_open\_question\_present below nicely formatted on a slide*

|  |
| :-: |
| OPEN\\\_QUESTION\\\_MARKERS = {    "what", "how", "why", "who", "where", "when", "which",    "tell me about", "describe", "walk me through",    "help me understand", "could you share more about",    "what else", "say more", "how so"} def check\\\_open\\\_question\\\_present(llm\\\_response: str) -\\\> tuple\\\[bool, str\\\]:    lower = llm\\\_response.lower()    for marker in OPEN\\\_QUESTION\\\_MARKERS:        if marker in lower:            return True, f"Found open question marker: '{marker}'"    return False, "No open question markers found in response" |

**Similarly, for the Support Triage Agent:** we could have code check whether the response references only ticket IDs that appeared in the original input? Does it avoid inventing IDs that weren't there?

### Tool call sequencing

**If your agent uses tools — retrieval, database lookups, API calls — you can check whether it called the right tools, in the right order, with the right parameters.**

This is one of the most underused categories of code-based eval and one of the most valuable. Tool call logs are structured data. They're easy to check programmatically.

**For the Support Triage Agent:** did the agent call Subscription\_Check before Resolution\_Step? Did it pass the correct user\_id? Did it avoid triggering Escalation for tickets below the severity threshold?

> *Diagram idea: diagram - show the code-based eval check\_tool\_call\_order below nicely formatted on a slide*

|  |
| :-: |
| def check\\\_tool\\\_call\\\_order(tool\\\_calls: list\\\[dict\\\]) -\\\> tuple\\\[bool, str\\\]:    names = \\\[call\\\["name"\\\] for call in tool\\\_calls\\\]    if "Subscription\\\_Check" not in names:        return False, "Subscription\\\_Check was never called"    if "Resolution\\\_Step" not in names:        return False, "Resolution\\\_Step was never called"    if names.index("Subscription\\\_Check") \\\> names.index("Resolution\\\_Step"):        return False, "Resolution\\\_Step called before Subscription\\\_Check"    return True, "Tool call order correct" |

### Threshold checks

**Latency, cost, token count, confidence scores — any numeric property can be checked against a threshold.** These are simple comparisons, but they catch important regressions. A new prompt version that passes every quality check but doubles response latency is still a problem.

**For the Support Triage Agent:** is end-to-end latency under 2 seconds? Is the response within the character limit? Is cost-per-ticket within budget?

> *Diagram idea: diagram - show the code-based eval check\_sla\_latency below nicely formatted on a slide*

|  |
| :-: |
| def check\\\_sla\\\_latency(trace\\\_metadata: dict, threshold\\\_ms: int = 2000) -\\\> tuple\\\[bool, str\\\]:    latency = trace\\\_metadata.get("latency\\\_ms")    if latency is None:        return False, "Latency not recorded in trace metadata"    if latency \\\> threshold\\\_ms:        return False, f"SLA breach: {latency}ms (limit: {threshold\\\_ms}ms)"    return True, f"Within SLA: {latency}ms" |

### Case Study: 3 Code Evals for the Support Triage Agent

Our earlier trace analysis revealed a set of error patterns. Three of them have clear, deterministic success conditions. They become the first three code evals in the eval suite.

#### **Eval 1: Category label format check**

The prompt specifies that every response must include exactly one of: Technical, Billing, or Feature Request. The generalization gap: some responses describe the category rather than using the canonical label. "This is a billing-related question" passes a vibe check but breaks the downstream routing system that parses the exact label.

> *Diagram idea: diagram - show the code-based eval check\_single\_valid\_category below nicely formatted on a slide*

|  |
| :-: |
| VALID\\\_CATEGORIES = {"Technical", "Billing", "Feature Request"} def check\\\_single\\\_valid\\\_category(agent\\\_output: str) -\\\> tuple\\\[bool, str\\\]:    found = \\\[c for c in VALID\\\_CATEGORIES if c in agent\\\_output\\\]    if len(found) == 0:        return False, "No valid category label found in output"    if len(found) \\\> 1:        return False, f"Multiple category labels found: {found}"    return True, f"Single valid category: {found\\\[0\\\]}"  |

**Passing case:** "Category: Billing — Customer is disputing their March invoice." → True, "Single valid category: Billing"

**Failing case:** "This appears to be a billing-related issue." → False, "No valid category label found in output"

**Diagnostic value: When this eval fails at scale, it tells you which prompt version introduced the paraphrasing behavior.** It also shows whether specific input types — short tickets, ambiguous tickets, non-English inputs — are disproportionately likely to produce unlabeled outputs.

#### **Eval 2: Hallucination guard — no invented ticket IDs**

The trace analysis found a specific failure mode: when summarizing a ticket, the agent occasionally references a ticket ID that wasn't in the input. This is hallucination. It can't be detected by reading the output alone — you have to check the output against the input.

> *Diagram idea: diagram - show the code-based eval check\_no\_invented\_ticket\_ids below nicely formatted on a slide*

|  |
| :-: |
| def check\\\_no\\\_invented\\\_ticket\\\_ids(user\\\_input: str, agent\\\_output: str) -\\\> tuple\\\[bool, str\\\]:    output\\\_ids = set(re.findall(r'TKT-\\\\d{5}', agent\\\_output))    if not output\\\_ids:        return True, "No ticket IDs referenced in output"    input\\\_ids = set(re.findall(r'TKT-\\\\d{5}', user\\\_input))    invented = output\\\_ids - input\\\_ids    if invented:        return False, f"Invented ticket IDs in output: {invented}"    return True, f"All referenced IDs {output\\\_ids} present in input" |

**Passing case:** Input mentions TKT-00421. Output references TKT-00421. → True

**Failing case:** Input mentions TKT-00421. Output references TKT-00422. → False, "Invented ticket IDs in output: {'TKT-00422'}"

**Diagnostic value: Hallucination of ticket IDs tends to cluster around specific agent behaviors** — usually when the model is asked to generate a summary that references prior context it doesn't actually have. The eval identifies exactly which inputs trigger this.

#### **Eval 3: Response latency SLA**

The product requirement is a sub-2-second classification. After a prompt update that added additional reasoning context, latency on the 50-ticket dataset increased from an average of 1.1 seconds to 2.4 seconds. The code eval caught this before release.

> *Diagram idea: diagram - show the code-based eval check\_sla\_latency below nicely formatted on a slide*

|  |
| :-: |
| def check\\\_sla\\\_latency(trace\\\_metadata: dict) -\\\> tuple\\\[bool, str\\\]:    latency\\\_ms = trace\\\_metadata.get("latency\\\_ms")    if latency\\\_ms is None:        return False, "Latency not recorded in trace metadata"    if latency\\\_ms \\\> 2000:        return False, f"SLA breach: {latency\\\_ms}ms (limit: 2000ms)"    return True, f"Within SLA: {latency\\\_ms}ms" |

These three evals cover format correctness, hallucination risk, and performance. They run on every prompt change. **When all three pass on the full dataset, the change is a candidate for release. When one fails, the failure message tells you exactly what to investigate.**

**Pitfall to avoid:** Don't confuse a green eval suite with a good agent. These three evals check specific properties you chose to measure. **They don't check whether the agent is helpful, coherent, or appropriately empathetic. Code evals are the floor, not the ceiling.** The full eval strategy — LLM judge, human review, user feedback — addresses what code can't reach.

### Running Code Evals Across a Dataset

PMs should lead on prioritizing and framing evals. You then work with your engineering team to **run them systematically across your reference dataset and read the results.** The mechanics are simple.

1.  You have a dataset (eg: the 50-ticket golden set from module 3).
2.  You run each eval function against each row.
3.  You record pass/fail and the reason string for every combination.
4.  Then you look at the aggregate.

> *Diagram idea: diagram describing the aggregate result metrics below of a code-based eval*

**Pass rate: the percentage of rows that pass the eval.** **
**Your baseline pass rate on the current production version is the reference point. A new prompt version that drops pass rate from 92% to 78% on the category label eval failed — even if every individual output looks fine in spot checks.

**Failure distribution: are failures concentrated on specific input types?****
**If 80% of hallucination eval failures come from tickets under 20 characters, the eval has given you a precise diagnostic. Short, underspecified inputs are the failure mode.

**Cross-eval correlation:** when the category label eval and the hallucination eval both fail on the same row, that's a signal about input complexity, not two independent problems. Look at the rows where multiple evals fail simultaneously.

**When the pass rate is unexpectedly low, check the eval logic first:**

  - A pass rate of 0% almost always means a bug in the eval function, not a fundamentally broken agent.
  - Read five failure reasons. If they're all "No valid category label found" on outputs that clearly contain category labels, your string matching has a case sensitivity issue.
  - Fix the eval before you investigate the agent.
  - Once the eval logic is verified, the low pass rate is a diagnostic signal. It tells you where to focus.

### Code Evals in Your Release Workflow

The goal is to run code evals automatically on every prompt change or model upgrade before anything ships.

> *Diagram idea: diagram describing how code-based evals fit into release workflows*

**The setup:** you need a reference dataset, a pass rate baseline for each eval on your current production version, and an explicit threshold for each eval.

**When you make a change, you run the eval suite, compare the results to the baseline, and check against the thresholds.**

  - Set thresholds before you start iterating, not after. The decision of whether 82% is good enough should not be made after you've already seen the number and want to ship.
  - Decide in advance: the category label eval must be above 90% for a prompt change to move forward. Write it down. Treat it as a hard gate.
  - The threshold varies by what you're shipping. A major architectural change — new retrieval method, new model family — warrants a higher bar and a larger reference dataset. A small prompt tweak can use a narrower margin.

The principle is consistent: the eval suite is a release gate, not a post-mortem tool.

**Quick rule of thumb** — If you can write the success condition as a Python function in under ten lines, it belongs in code. If expressing the success condition requires understanding intent, evaluating tone, or reasoning about quality, that's an LLM judge. We’ll dive into this in our next section.

## Recap and Further Learning

### Key takeaways and definitions

  - **Default Evaluation Path:** The default for automated evaluation should always be code-based because it is faster, cheaper, and 100% reproducible (deterministic).
  - **Anatomy of an eval:** Every code-based eval requires three parts: Inputs (the full trace), The check (the logic, such as a pattern match or schema validation), and The output (a pass/fail result plus a non-optional reason string for debugging).
  - **Release Gate:** Code evals are the bedrock of a reliable eval suite; they should run on every prompt or model change and act as a hard release gate by comparing results to a baseline pass rate and explicit thresholds.
  - **Limitations of deterministic checks:** Code evals are the "floor, not the ceiling". They only check specific, measurable properties and cannot evaluate subjective qualities like helpfulness, intent, or empathy, which require LLM judges or human review

**Code-based Eval****
**A code-based evaluator is a simple Python function that takes the AI system's output (a "trace") and returns a deterministic pass or fail result, without using an LLM call.

**Reason string**
The non-optional string output of a code-based eval that explains why an eval failed, necessary for debugging.

**Tool Call failures**
Mechanical, not conceptual, failures in multi-step systems where agents call tools that don’t exist, omit required parameters, or invoke steps out of order.

**Release Gate (General IT)****
**A milestone or health indicator of a software release at a specific point in time, where each Gate defines criteria that must be met to mark a phase as completed, ensuring a smooth journey into production.

**RAG (Retrieval-Augmented Generation)****
**An AI framework that enhances large language models (LLMs) by first retrieving relevant information from external knowledge bases and then using that information to generate more accurate and contextually relevant responses.

**GREP (Global Regular Expression Print)****
**A command-line utility for searching text or data sets for lines that match a regular expression or pattern. It is mentioned as part of search-based systems where "Search quality problems surface" if the correct documents are not retrieved.

In the next module, we will learn how to build LLM-as-Judge evaluators for the quality dimensions that code can’t reach — tone, actionability, and factual grounding.
