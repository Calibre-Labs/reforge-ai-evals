# Ch 3: Principles of Trace Analysis

In this module, you will develop a repeatable workflow for reading agent traces — sourcing diverse inputs, reviewing outputs free-form, and clustering patterns into structured trace codes.

**Before you can automate evaluation, you need to understand how your system actually behaves.**

> *Diagram idea: summarizing the role of trace analysis in AI development based on this intro*

We start that journey with trace analysis. **Trace analysis is how teams move from abstract quality goals to concrete insight.** It is the AI equivalent of UX research: instead of interviews and session replays, you study real inputs and outputs to understand success and failure.

New features, unexpected behavior, or user complaints all surface first in real traces. You review them manually to understand what actually happened, not what you hoped would happen. **This is where failure modes are named and reference examples are created.**

**Pitfall to avoid:** Most teams try to skip this step. They jump straight to dashboards, benchmarks, or automated scoring. The result is predictable: metrics that look rigorous but don’t reflect what users experience.

This chapter teaches a lightweight, repeatable way to do trace analysis without turning it into an academic exercise.

### What is a Trace

Before you can analyze traces, your team needs a shared vocabulary for LLM instrumentation. These terms define the atomic units of AI requests.

> *Diagram idea: defining an LLM Trace based on below with a JSON snippet example*

|  |
| :-: |
| Trace - A trace is the complete record of everything that happened inside a single AI request. It captures all user inputs, all model outputs (including intermediate steps) and relevant metadata such as timestamps, token counts, and model versions. |

Traces can be single or multi-turn - where every turn represents fresh external input for the LLM. We recommend recording all the AI vs user back and forth in a single session as a single Trace. When you do trace analysis, you are reviewing not just final outputs, but the full sequence of work the system performed.

#### **Example 1: AI Slide Tool**

A user signs up for an AI presentation tool like Gamma and takes these actions:

  - Creates a new presentation from a template
  - Uploads an outline to generate slides
  - Opens individual slides and edits them
  - Asks the AI to rewrite a slide
  - Iterates on that rewrite through multiple back-and-forth instructions

To the user, this feels like a single continuous workflow. Under the hood, it might produce multiple traces based on how the agents are structured.. Essentially, each task performed with a distinct agent is its own trace.

> *Diagram idea: defining an LLM Trace with a JSON snippet example based on below*

Trace 1 - Slide generation workflow: Outline → Slides

  - User uploads an outline
  - AI generates a full slide deck from that outline
  - Output is a structured set of slides

This trace contains:

  - The uploaded outline and prompt used to generate slides
  - The generated content
  - Any intermediate reasoning or formatting steps
  - All the metadata on the interaction including tokens, latency, etc

Trace 2 - Slide rewrite workflow

  - User selects a specific slide
  - Asks AI to rewrite it through multiple iterations
  - Output is a revised slide

This can be a separate group of traces because it represents a collaborative work with a different part of the AI Slide app.

#### **Example 2: Customer Support Agent**

Below is a simplified JSON representation of an LLM Trace which captures a Retrieval-Augmented Generation (RAG) operation from a CSM agent where a user asks about a return policy.

You can see multiple spans within the trace: the user input query asking about the return policy. The retrieval step where the agent returns content relevant to the request. And a final span with token/latency metadata. While simplified, this is the general shape of traces we will analyze in actual observability tools.

{  "trace\_id": "5b8aa5a2d2c872e8321cf37308d69df2",

    "metadata": {

    "user\_id": "user\_123",

    "environment": "production"

  },

  "spans": \[

    { "span\_id": "051581bf3cb55c13","name": "UserQueryInput",

      "inputs": { "text": "What is your return policy?" }

    },

    { "span\_id": "8a3d12f1e4b21c45", "name": "VectorStoreRetrieval",

      "run\_type": "retrieval",

      "metadata": { "top\_k": 2 },

      "outputs": {

        "documents": \[

          { "content": "Items can be returned within 30 days.", "score": 0.92 },

          { "content": "Must include original receipt for full refund.", "score": 0.88 }

        \]

      }

    },

    {"span\_id": "2d9c4e1f5b0a3c21",

        "usage": {

          "prompt\_tokens": 142,

          "completion\_tokens": 18,

          "total\_tokens": 160

        }

      },

      "latency\_ms": 850

    }

  \]

}

## The Trace Analysis Workflow: Generating Codes

Here's the systematic process for moving from raw traces to structured evaluation categories.

> *Diagram idea: of trace analysis 3 step workflow based on image below*

### Step 1: Source inputs

You start by assembling a small but diverse set of inputs to run through the system. These inputs can come from:

  - Early design partners or internal users
  - Support tickets or example use cases
  - Synthetic inputs generated with prompts

At this stage, perfection doesn’t matter. Coverage does. You are trying to see range: different personas, intents, ambiguity levels, and edge cases.

For early products, synthetic inputs are often the fastest way to explore the solution space. The goal is not realism for its own sake, but stress-testing the system across plausible scenarios.

### Step 2: Review Outputs (Free-Form)

Next, you review traces manually. This is an intentionally open-ended pass. You are not scoring or judging yet. You are observing. As you review each trace:

  - Take generous notes and write down anything that surprises you
  - Capture both failures but also moments where the system is impressive

**Three kinds of signals usually emerge: hard performance failures, soft quality issues, and emergent behavior that differentiates your product.** Below are examples of all three.

> *Diagram idea: showing types of trace codes that emerge from analysis based on table below*

|  |  |  |
| :-: | :-: | :-: |
| \*\*Hard performance failures\*\* | \*\*Soft quality issues\*\*  | \*\*Product Differentiators\*\*  |
|   - Hallucinated facts&#10;  - Missed user constraints&#10;  - Tool invocation failures&#10;  - Ignoring parts of the user request&#10;  - Truncating critical context |   - Tone feels off&#10;  - Output is technically correct but unhelpful&#10;  - Missed opportunity to propose next steps&#10;  - Too verbose or too shallow |   - Good at asking the right clarifying questions - users are responding well to this&#10;  - Consistently unique format for the output  |

Early on, resist the urge to formalize. Patterns appear through repetition, not through over-structuring the first ten traces.

### Step 3: Cluster Into Trace Codes

After reviewing 30–50 traces, repetition sets in. This is where structure emerges. You now cluster your notes into trace codes:

  - Groups of similar success or failure patterns
  - Each category represents a recurring behavior worth tracking

A strong trace code has:

  - A short, concrete name
  - A one-sentence definition
  - Clear Yes / No criteria
  - Two or three representative examples

#### **Example 3: Market Research Agent**

Consider a market research agent that searches the web to respond to user questions about competition and general company information. Examples of trace codes for an agent conducting market research might be:

1.  *Unsupported claims* — Makes assertions without citing sources
2.  *Over-generalization* — Treats niche markets as homogeneous
3.  *Missed ambiguity* — Assumes metrics like “market size” without clarification
4.  *Strong synthesis* — Connects multiple weak signals into a coherent insight

**Keeping these codes binary (Yes/No) matters.** They force clarity. If two reviewers can’t agree whether something passes, the code isn’t ready for automated labelling.

Over time, these codes become the foundation for rubrics, datasets, and automation.

## Sourcing a Diverse Dataset: the User Input Grid

Simply asking an LLM to "generate test queries" produces generic inputs that fail to surface critical edge cases. **A user input grid (UIG) mapped to different user intents** is how you bring order to probabilistic complexity by creating a structured grid of query dimensions that mirrors production diversity.

> *Diagram idea: diagram of UIG methodology based on steps below*

### The UIG Methodology

**Step 1: Define 3-5 Key Dimensions**

Identify the variables that create meaningful diversity in your product. Common dimensions include:

  - Ideal Customer Profile (ICP): Enterprise, Mid-market, SMB
  - Persona: End user role (Engineer, Manager, Executive)
  - User Intent: What task they're trying to accomplish
  - Context Richness: Complete information vs. missing details
  - Ambiguity Level: Clear instructions vs. vague requests

**Step 2: Generate Realistic Examples**

Create 2-3 concrete examples for each dimension, grounded in real-world constraints:

ICP Examples:

  - Public SaaS: Companies with publicly available financial data
  - Private B2B: Limited public information, must infer from news/funding
  - Healthcare: HIPAA compliance constraints, specialized terminology

User Intent Examples for our Market Research Agent might include:

  - Competitive analysis: "Who are our direct competitors and what's their positioning?"
  - Market sizing: "What's the TAM for vertical SaaS in manufacturing?"
  - Customer research: "What pain points do customers mention most in G2 reviews?"

**Step 3: Create Combinations**

Form a grid by combining dimensions. For 4 ICPs × 4 Personas × 4 JTBDs = 64 possible combinations. Remove implausible ones (e.g., "Executive researching low-level technical details"), leaving 15-20 realistic scenarios. Example Combination:

  - ICP: Public SaaS
  - Persona: Product Marketing Manager
  - JTBD: Competitive landscape
  - Context: Q4 2024 data needed

**Step 4: Add Real-World Constraints**

Enhance combinations with realistic complications:

  - Missing context: User doesn't specify which market/geography
  - Ambiguous terms: "Best" could mean revenue, growth rate, or customer satisfaction
  - Time sensitivity: "Recent" could mean last month or last year
  - Conflicting requirements: "Comprehensive but concise"
  - Business rules: "Must comply with data privacy regulations"

**Step 5: Formulate Natural Language Queries**

Use an LLM to transform combinations into natural user queries. Provide the combination as structured input, ask for 2-3 variations.

> *Diagram idea: showing an example prompt for user queries based on below*

|  |
| :-: |
| \*\*User Input Grid based prompt for market research agent\*\* \\\#\\\# Create 5 natural user queries for a market research agent in this scenario:\\- ICP: Public SaaS companies\\- Persona: Product Marketing Manager\\- JTBD/User Intent: Competitive landscape analysis\\- Constraint: Needs recent data, geography not specified\\- Ambiguity: "Leading" companies (could mean various metrics) |

Generated Queries could include:

1.  *\*"Which US SaaS companies have the highest customer satisfaction scores in Gartner's 2025 reports?"\**
2.  *\*"Who are the leading CRM platforms by market share, and what are their key differentiators?"\**

Notice these inputs have realistic ambiguity (leading = satisfaction or market share?) and missing context (US assumed but not stated in query 2).

#### **Example 4: Legal Contract Analyzer**

Below is what a user input grid for a legal analysis agent might look like:

> *Diagram idea: showing user input grid for a Legal Agent based on table below*

|  |  |
| :-: | :-: |
| Dimension 1 - Contract Type:  - Employment agreements&#10;  - Non-disclosure agreements (NDAs)&#10;  - Vendor/supplier contracts | Dimension 2 - User Role:  - In-house counsel&#10;  - Paralegal&#10;  - Executive (non-legal background) |
| Dimension 3 - User Intents:  - Risk assessment&#10;  - Clause extraction&#10;  - Compliance verification  | Dimension 4 - Context:  - Complete contract provided&#10;  - Partial contract (missing pages)&#10;  - Verbal description only  |

**Sample Combination:**

  - Employment agreement + In-house counsel + Risk assessment + Complete contract

**Sample Generated Query:**

*"Review this employment agreement for non-standard termination clauses that could expose us to litigation in California. Flag any provisions that deviate from our standard template."*

## Collaboration: Make Trace Analysis a Team Sport

> *Diagram idea: showing different roles and their responsibilities for trace analysis*

**Trace analysis is most effective as a cross-functional team effort.** It turns subjective "product taste" into trusted, repeatable standards the entire team can align on. Different roles reveal distinct failure modes:

  - PMs catch violations of the product promise and user intent
  - Engineers identify fragility in tool execution and architectural issues
  - Designers surface UX issues and formatting problems
  - Subject Matter Experts (SMEs) catch domain-specific mistakes others might miss

**The collaborative workflow:**

1.  Independent labeling: 3-4 team members each label the same 20 traces individually
2.  Comparison meeting: Compare labels, discuss disagreements
3.  Refinement: Tighten category definitions based on where people disagreed
4.  Standardization: Update the rubric, re-label disagreements
5.  Repeat: Continue until team achieves \>90% agreement

### Knowing When to Stop: The Saturation Rate

**A common question: how much data is "enough"?** You don’t need thousands of traces. You stop when you reach saturation:

  - You review ten consecutive traces of different kinds
  - No new codes emerge
  - Existing codes keep repeating

That’s your signal to move on. At that point, more review adds diminishing returns. The work shifts from discovery to formalization. Note, saturation is per-dimension. **You might reach saturation on "tone" after 50 traces but need 150 traces to understand "factual accuracy" failure modes.** Track saturation separately for each quality criterion you're evaluating.

### Playing Offense, Not Just Defense

Trace analysis isn’t only about catching errors. **You should actively look for affirmative patterns and double down on the strategy behind them:**

  - Outputs users accept immediately
  - Moments where the agent anticipates the next question
  - Responses that reduce follow-up work

These are signals of product taste. Capturing them ensures you don’t just eliminate bad behavior but reinforce what’s great.

## Recap and Further Learning

### Key takeaways and definitions

  - **Trace Analysis as UX Research:** Trace analysis is the AI equivalent of UX research, moving teams from abstract quality goals to concrete insights by manually studying real inputs and outputs
  - **Source Diversity with UIGs:** The User Input Grid (UIG) methodology structures test data creation (or sourcing) by defining key dimensions (like ICP and User Intent) and generating realistic, constrained, and ambiguous queries
  - **Collaboration and Standardization:** Trace analysis is a cross-functional effort, and a Trace Code is only ready for automation when reviewers achieve high inter-rater agreement (\>90%)
  - **Knowing When to Stop**: Stop manual review when you reach the Saturation Rate—when no new failure or success categories are emerging
  - **Playing Offense:** Actively look for successful patterns and product differentiators, not just failures, to reinforce effective product behavior

**Trace****
**The complete record of everything that happened inside a single AI request, including all user inputs, model outputs (including intermediate steps), and metadata

**Trace Codes**
Short, concrete names representing recurring success or failure patterns, which are clustered from free-form review notes and form the foundation for automated rubrics and datasets

**User Input Grid (UIG)****
**A structured methodology used to generate a diverse and realistic set of user queries by defining and combining variables such as Customer Profile, Persona, and Ambiguity Level

**Saturation Rate****
**The point at which manual review of diverse traces stops yielding new categories, signaling the discovery phase is complete

### Recommended articles

  - [The AI PM Craft: Evolving Product Leadership](https://www.reforge.com/courses/ai-evals)
  - [Evals, Error Analysis, and Better Prompts](https://www.lennysnewsletter.com/p/evals-error-analysis-and-better-prompts)
  - [Why AI Agents Break: A Field Analysis of Production Failures](https://arize.com/blog/common-ai-agent-failures/)
  - In the next module, we will learn the principles that determine when to automate evaluation, which method to choose, and the common mistakes that make eval suites unreliable.

In the next module, we will learn the principles that determine when to automate evaluation, which method to choose, and the common mistakes that make eval suites unreliable.
