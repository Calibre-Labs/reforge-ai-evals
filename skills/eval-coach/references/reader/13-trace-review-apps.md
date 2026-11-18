# Ch 13: Vibecoding Custom Trace Analysis apps

Generic observability tools show you one-size-fits-all traces. Custom tools show you *your* traces in the way that matters for *your* product experience.

Teams with custom annotation tools iterate approximately 10x faster, per field research . The reason is not magic. Custom tools show all relevant context from multiple systems in one place, rendered in a product-specific way, with a labeling workflow designed for your specific evaluation criteria. A generic trace viewer shows you JSON. A custom tool shows you a formatted email, alongside the customer's account tier and conversation history, with Pass/Fail buttons mapped to your annotation rubric.

With AI coding tools (Claude Code, Cursor, Lovable, Replit), PMs can build these tools in hours, not weeks. This chapter teaches you what to build, how to build it, and the four patterns that show up across teams.

> *Diagram idea: diagram — generic trace viewer (raw JSON) vs. custom trace viewer (rendered with product context, labels, navigation)*

#### **The limitations of generic observability**

Generic tools (like Langsmith, Arize, Braintrust, etc) handle all the basics: trace logging, metric tracking, prompt playgrounds, etc. They're good at what they do. They struggle with four things.

**Rendering your specific output format.**
If your agent generates emails, a generic tool shows you the raw text. A custom tool renders it as an email. If your agent generates SQL, a generic tool shows the string. A custom tool shows the query with syntax highlighting and the execution results alongside it. Format-specific rendering is the difference between scanning a trace in 10 seconds and spending 2 minutes reconstructing what the agent actually produced.

**Showing business context alongside traces.**
When you're reviewing a support triage response, you need to see the customer's account tier, their ticket history, and whether they've escalated before. That context is in your CRM, not in the trace. Generic tools can't pull it in.

**Supporting your specific labeling workflow.** **
**Your annotation rubric has specific criteria, specific trace code categories from module 4, and specific routing logic for which bucket (dev or test) a labeled trace goes into. Generic tools offer general-purpose labeling. Custom tools enforce your workflow.

**Integrating with your internal systems.** **
**Pushing labels back to your dataset management system, pulling traces from your observability platform, cross-referencing with your CRM or ticketing system. These integrations are product-specific. Generic tools can't know about them.

### What custom tools enable

> *Diagram idea: diagram — four capabilities of custom tools: domain-specific rendering, contextual information, workflow-specific navigation, speed optimizations*

**Domain-specific rendering.** If your agent generates emails, render them as emails. If it generates SQL, show the query with syntax highlighting and execution results. If it generates slide content, show a visual preview. Match the output format to how users actually see it.

**Contextual information.** Show user profile, account tier, conversation history, and related support tickets alongside the trace. The reviewer should never need to open a second tool to understand the context.

**Workflow-specific navigation**. Filter by trace code, sort by failure signal, batch-label similar traces. Jump to the next disagreement between the judge and the human label. Skip traces that have already been reviewed.

**Speed.** Keyboard shortcuts for labeling, progress indicators, and streamlined navigation keep reviewers in flow. The difference between 3 minutes per trace and 45 seconds per trace compounds across hundreds of review sessions.

### What to Build: Core Features

#### **Feature 1: Intelligent trace rendering**

Display the trace in a format that matches your product's output. Collapse less important details (metadata, intermediate reasoning, system-level tokens) into expandable sections. Highlight the parts that matter: user input, agent output, tool calls, and any failure signals.

> *Diagram idea: diagram — trace rendering layout: user input (top), agent output (center, formatted), tool calls (collapsible sidebar), metadata (collapsed footer)*

The rendering should make the reviewer's job obvious: "look at the user's question, look at the agent's response, decide if it's good." Everything else is context available on demand, not visual noise competing for attention.

#### **Feature 2: Labeling interface**

Binary Pass/Fail buttons with a required notes field. A dropdown for trace code assignment (from your taxonomy in Chapter 3). An "Add to dataset" button that routes labeled traces to the appropriate bucket (dev or test).

The labeling interface should enforce your annotation rubric. If the rubric says every Fail must include a reason, the UI should require a notes entry before the Fail label is saved. If the rubric defines 8 trace code categories, the dropdown should list exactly those 8 categories.

#### **Feature 3: Navigation and filtering**

Filter by: trace code, eval result (pass/fail), date range, user segment, product feature.

Sort by: eval score, latency, response length, confidence.

Search by: keyword, semantic similarity.

Progress indicator: "Trace 23 of 50, 46% complete." Reviewers need to know where they are in the queue and how much is left. Without a progress indicator, review sessions feel endless.

#### **Feature 4: Keyboard shortcuts**

N = next trace. P = previous trace. Y = Pass. F = Fail. D = add to dataset.

These small optimizations compound: a reviewer doing 50 traces per session saves 15+ minutes per session with keyboard navigation compared to clicking buttons. Over a quarter of weekly reviews, that's 4+ hours of saved time per team member.

## How to Build It: The Vibecoding Workflow

#### **Step 1: Choose your tool**

> *Diagram idea: diagram — AI coding tool comparison: Lovable/Replit (no code experience, fastest to prototype) vs. Claude Code/Cursor (some technical comfort, more control) vs. Jupyter Notebooks (data-heavy workflows, inline analysis)*

**Lovable or Replit:** Best for PMs with no coding experience. Describe what you want in natural language. These tools generate full web applications from a description.

**Claude Code or Cursor:** Best for PMs with some technical comfort. More control over the implementation. Better for applications that need specific API integrations or custom logic.

**Jupyter Notebooks**: Best for data-heavy workflows. Build widgets and small UIs directly in the notebook. Great for combining trace review with data analysis (e.g., plotting failure distributions while reviewing traces).

#### **Step 2: Start with a minimal prototype**

Don't build everything at once. Start with:

  - Load traces from a CSV or JSON file
  - Display one trace at a time with basic formatting
  - Pass/Fail buttons that write labels to a file
  - Next/Previous navigation

This takes 1 to 2 hours with AI coding tools. The goal is a working tool you can use today, not a polished application.

#### **Example prompt for your first prototype:**

*"Build an app that loads traces from a JSON file where*

  - *\*each trace has fields: user\\\_input, agent\\\_output, tool\\\_calls, and trace\\\_id.\**
  - *\*Display one trace at a time with the user input at the top, the agent output below it formatted as markdown, and tool calls in a collapsible section.\**
  - *\*Add Pass and Fail buttons that write the trace\\\_id and label to a CSV file.\**
  - *\*Add Next and Previous buttons to navigate between traces.\**
  - *\*Show a progress counter: 'Trace 12 of 50.'"\**

That prompt, given to Claude Code or Cursor, produces a working app on the first try. The specificity matters.

"Build me a trace reviewer" produces something generic. Naming your fields, your file format, and your labeling outputs produces something you can actually use.

#### **Step 3: Iterate based on usage**

Use the tool yourself for one review session (20 to 30 traces). Note what's slow, what's missing, what's confusing. The friction points become your feature backlog.

Add features incrementally: filtering, keyboard shortcuts, trace code dropdowns, dataset routing, progress indicators. Each addition should solve a specific pain point you experienced during actual review sessions.

#### **Step 4: Connect to your data sources for automation**

Start with manual steps  for your app to polish the workflow and then try to automate the pipeline.

**Pull traces from your observability platform** via API. This eliminates the manual export step and lets you review traces as they arrive.

**Pull user context from your CRM or database.** The reviewer sees the customer's account tier, past interactions, and relevant metadata alongside the trace.

**Push labels back to your dataset management system.** When a reviewer labels a trace, it goes directly into the dev or test bucket on github or your observability platform. No manual file management.

**API integration is where AI coding tools particularly excel. Describe the API and the data you need. Let the tool generate the integration code.**

### Patterns from the Field

#### **Pattern 1: The trace review app**

Great for daily and weekly error analysis sessions. Optimized for speed and coverage.

**Core features:** Trace rendering, Pass/Fail labels, trace code assignment, keyboard navigation, progress tracking.

**When to build it:** As soon as you start doing regular trace reviews (typically after your first trace analysis cycle). If you're reviewing more than 10 traces per session, you need this.

#### **Pattern 2: The calibration app**

Great for judge calibration sessions from module 9. Shows the trace, the human label, and the judge verdict side by side. Highlights disagreements. Let’s you drill into the judge's reasoning string.

**Core features:** Side-by-side display (trace + human label + judge verdict + reasoning string), disagreement filter, "Override" button for relabeling when the judge is right and the human was wrong.

**When to build it:** When you start calibrating LLM judges and find yourself manually comparing spreadsheets of human labels against judge outputs.

#### **Pattern 3: The dashboard app**

Great for stakeholder communication and team alignment. Shows aggregate eval results, failure funnels (module 13), and trends over time.

**Core features:** Pass rate charts, failure funnel visualization, trend lines, drill-down from aggregate to individual traces.

**When to build it:** When you need to regularly report eval results to leadership or other teams. Not for trace-level review. For pattern-level visibility.

#### **Pattern 4: The collaborative labeling app**

Great for cross-functional trace analysis sessions from Chapter 3. Multiple reviewers label independently, then compare.

**Core features:** Independent labeling queues per reviewer, inter-rater agreement statistics, disagreement highlighting for discussion, rubric reference panel.

**When to build it:** When you start involving multiple people in labeling (PM + domain expert + engineer) and need to measure inter-annotator agreement.

## Case Study: Building a Triage Review App

> *Diagram idea: diagram — wireframe of the triage review app showing the ticket, agent output, label buttons, and navigation*

**Tool used in course demo:** **Lovable.**

**The starting prompt:**

*"Build a web app for reviewing AI support triage results:*

  - *\*I have a JSON file where each entry has: ticket\\\_text (the customer's support ticket), agent\\\_category (the category the agent assigned), agent\\\_sentiment (positive/negative/neutral), agent\\\_urgency (low/medium/high), and a ticket\\\_id.\**
  - *\*Display the ticket text formatted like a support email with a subject line and body. Below it, show the agent's triage output as three labeled fields.\**
  - *\*Add Pass/Fail buttons and a dropdown with these trace codes: correct\\\_triage, wrong\\\_category, wrong\\\_sentiment, wrong\\\_urgency, edge\\\_case, ambiguous\\\_input.\**
  - *\*Include Next/Previous navigation and a progress counter. Export all labels to CSV."\**

**Time to first prototype:** \<2 hours. Lovable generated the full app from this prompt. The only manual adjustments were CSS tweaks to make the email rendering look realistic and fixing the CSV export path.

**What it does:** Loads the 50-ticket golden dataset. Displays each ticket with the agent's triage output (category, sentiment, urgency). Shows the original ticket formatted as a support email (not raw text). Pass/Fail buttons with trace code dropdown. Keyboard shortcuts. Exports labeled data as CSV.

**Iteration 1 (Day 2):** After reviewing 30 traces, two friction points were obvious. First, the reviewer kept opening a spreadsheet to check the golden label. Second, filtering was needed because category errors clustered in specific categories. The follow-up prompt: "Add a toggle button labeled 'Show Reference' that displays the golden label next to the agent's output, with differences highlighted in yellow. Add a category filter dropdown at the top." Review time per trace dropped from 3 minutes to 90 seconds.

**Iteration 2 (Day 4):** The team wanted to review live production traces, not just the golden dataset. The follow-up prompt: "Add an API integration that pulls traces from our Langsmith project via their REST API. Add a 'Flag for Discussion' button that tags traces for the weekly team review. Add a progress indicator showing traces reviewed, traces remaining, and current pass rate." Connecting to the Langsmith API required one round of debugging (the auth token format was wrong), but Lovable fixed it when given the error message.

**Result:** Review time per trace dropped from 90 seconds to 45 seconds (keyboard shortcuts were the biggest gain). The team now reviews 50 traces per week instead of 15. Error analysis that previously required a half-day session now takes 45 minutes.

**Total investment: 6 hours across three sessions.** The return: the team reviews 3x more traces per week, the dataset grows faster, and the calibration loop from Chapter 8 runs in hours instead of days.

## Recap and Further Learning

### Key takeaways and definitions

  - **Custom tools produce a 10x speed-up.** Generic observability handles logging. Custom tools handle your workflow: rendering, labeling, navigation, and context in one place.
  - **Start minimal, iterate fast.** Build a basic trace viewer in 1 to 2 hours with AI coding tools. Add features based on actual usage, not speculation. The first version needs four things: load traces, display one at a time, Pass/Fail buttons, and Next/Previous navigation.
  - **Four patterns cover most needs.** Trace review (daily error analysis), calibration (judge validation), dashboard (stakeholder communication), and collaborative labeling (team alignment). Build the one you need most first.
  - **PMs can build this.** You don't need engineering resources or a sprint cycle. AI coding tools let you describe what you want and get a working app. The hardest part is deciding what to build, not building it.

**Trace rendering** **
**Displaying an agent's output in the format that matches how users actually see it (formatted email, syntax-highlighted SQL, visual preview), rather than showing raw text or JSON.

This concludes the core course material. We hope this serves as a helpful reference to you in your AI product management journey. For additional topics, see the bonus modules in this course.
