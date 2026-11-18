# Appendix: Capability deep dives (RAG, multimodal and voice)

## The Specialized Capabilities Challenge

Chapters 4-6 covered general evaluation strategies applicable to most AI systems. But three capabilities: RAG (search and retrieval), multimodal parsing (especially PDFs), and voice agents appear in many enterprise AI products and each requires specialized evaluation techniques.

These aren't just different features; they introduce fundamentally different architectural complexity:

  - **RAG** splits your system into two distinct stages (retrieval + generation), each requiring independent evaluation
  - **Multimodal parsing** handles non-semantic layouts where the same content can appear in infinite visual arrangements
  - **Voice** operates under harsher latency constraints with cascading failure modes across speech-to-text, reasoning, and text-to-speech

This chapter provides the technical playbook for measuring these capabilities. Each section follows the same pattern: explain the unique challenge, define the metrics, and show how to implement evaluation in practice.

## Part 1: Retrieval Augmented Generation (RAG)

### **The RAG Architecture**

RAG is the architectural standard for ensuring LLMs respond using context that's independent of their static training data. Models have knowledge cutoff dates and lack access to private enterprise data. RAG "grounds" the model by providing relevant document chunks to analyze before generating an answer.

**The two-stage process:**

1.  **Retrieval:** Search a document corpus, return top-k most relevant chunks
2.  **Generation:** LLM reads those chunks and generates a response

From a product perspective, the spec is no longer just the prompt. It is the behavior of a composed system that selects context, passes it forward, and then reasons over it.

### **Stage 1: Evaluating Retrieval (Search Relevance)**

Retrieval must be evaluated **independently** from generation to isolate where errors occur. The core objective is measuring whether the system collected the most relevant information to meet the user's intent.

You need a **ground truth dataset**: queries paired with labels indicating which documents are relevant. This requires manual labeling—there's no shortcut here.

### **Retrieval Metrics**

**Precision@k** measures noise. Of the documents returned, how many were actually useful? Precision matters when users expect a small, trustworthy set of results and scanning irrelevant material is costly.

*Example:* Your system retrieves 5 documents. You labeled 3 as relevant beforehand. Your system found 3 relevant documents in those 5 results.

Precision@5 = 3 relevant / 5 total returned = 0.6 (60%)

**Recall@k** measures coverage. Of all relevant documents that exist, how many did the system find? Recall matters when missing information creates downstream risk and hallucination pressure.

*Example***:** Your corpus contains 3 total relevant documents for this query (your ground truth). Your system's top-5 results included 3 of those relevant documents.

Recall@5 = 3 found / 3 total relevant = 1.0 (100%)

**The Precision/Recall Trade-off:**

You can't maximize both simultaneously. Retrieving more documents (higher k) generally improves recall but hurts precision.

*Example***:**

  - With k=3: You might get 2 relevant docs out of 3 → Precision = 67%, Recall = 67%.
  - With k=10: You might get all 3 relevant docs out of 10 → Precision = 30%, Recall = 100%

Your product requirements dictate which to prioritize.

**MRR (Mean Reciprocal Rank)** measures how quickly the system surfaces the first useful document. It reflects whether users can treat the top result as “the answer” rather than a list to explore. This measures the position of the first relevant result, averaged across many queries.

**Example:**

  - Query 1: First relevant result at position 2 → score = 1/2 = 0.5
  - Query 2: First relevant result at position 1 → score = 1/1 = 1.0
  - Query 3: First relevant result at position 4 → score = 1/4 = 0.25

MRR = (0.5 + 1.0 + 0.25) / 3 = 0.58

**Interpretation:**

  - MRR = 1.0 means first result is always relevant (perfect)
  - MRR = 0.5 means first relevant result is at position 2 on average
  - MRR = 0.2 means first relevant result is at position 5 on average

**NDCG (Normalized Discounted Cumulative Gain)** captures graded relevance and ranking quality. It matters when some documents are clearly better than others and position strongly affects usability. This is the most sophisticated metric accounting for two things:

1.  **Relevance isn't binary** (some docs are "highly relevant," others "somewhat relevant")
2.  **Position matters** (rank 1 is more valuable than rank 5)

**Example:**

Instead of labeling documents as simply "relevant" or "not relevant," you assign relevance scores:

  - 2 = highly relevant
  - 1 = somewhat relevant
  - 0 = not relevant

NDCG rewards systems that place highly relevant items at the top. A "somewhat relevant" document at position 1 scores lower than a "highly relevant" document at position 1.

### **Which Metric to Prioritize?**

This is a **product decision**, not a purely technical one. It directly impacts user experience.

**Prioritize Precision when:**

  - Users need high confidence in a small result set
  - False positives are costly (waste user time, erode trust)
  - Example: Legal research tool where one wrong case citation damages credibility

**Prioritize Recall when:**

  - Comprehensiveness matters more than precision
  - Users can tolerate scanning extra results
  - Missing information is catastrophic
  - Example: Medical diagnosis support where missing a relevant study could harm patients

**Prioritize MRR when:**

  - Users expect the first result to be the answer
  - Most queries have one clear "best" document
  - Example: Internal knowledge base for FAQ-style questions

**Prioritize NDCG when:**

  - Relevance exists on a spectrum (not binary relevant/irrelevant)
  - Ranking quality matters more than absolute recall
  - Example: E-commerce search where "somewhat relevant" products should rank lower but still appear

### **Choosing k Is Also a Product Decision**

Picking the "k" value (how many documents to retrieve) is a product decision that balances completeness against noise and cost.

Small *k* values favor precision, speed, and cost, but increase the chance of missing context. Large *k* values improve recall but introduce noise, token pressure, and ranking sensitivity.

Exploratory tools tend to tolerate higher *k*. Answer-oriented tools do not. Multi-step agents often sit in between, needing enough context to reason without overwhelming later steps. There is no correct value outside of user expectations.

### **Stage 2: Evaluating Generation**

Once retrieval succeeds, the model's response must be evaluated for **Faithfulness** (absence of hallucinations) and **Relevance** (actually answers the question).

**Faithfulness: Does the response only include information from the retrieved documents?**

This is typically evaluated using LLM-as-judge (from Chapter 5), asking:

  - Can every factual claim be traced to a source document?
  - Are there invented details, dates, numbers, or names?
  - Does it properly attribute information to sources?
  - When sources don't contain the answer, does it say "I don't know"?

**Relevance: Does the response actually answer the user's question?**

A response can be perfectly faithful and still useless if it summarizes documents instead of synthesizing an answer.

**Example:**

User query: "What are our Q4 hiring plans for engineering?"

Retrieved documents: Q4 budget document

Response: "The Q4 budget document was updated on October 15th and contains 47 pages of information about various departments."

**Relevance evaluation:**

  - Faithful? ✓ (information is accurate)
  - Relevant? ✗ (doesn't answer what the hiring plans are)

This response summarizes the retrieved documents without synthesizing the answer to the user's question.

## Part 2: Multimodal Deep Dive—The PDF Challenge

PDFs are the dominant medium for enterprise knowledge: policies, invoices, contracts, research papers, technical specs. But they present a unique multimodal challenge that text-only evaluation can't handle.

### **The PDF Problem: Non-Semantic Layouts**

Unlike structured data (JSON, databases) or clean text (markdown, plain text), PDFs have **non-semantic layouts** where information appears in arbitrary visual arrangements:

  - Headers, footers, watermarks scattered across pages
  - Multi-column layouts where reading order isn't left-to-right
  - Tables that span multiple pages
  - Scanned images with varying quality
  - Forms with fields in unpredictable positions
  - Mixed content (text + images + charts)

**The core challenge:** The same information can appear in infinite visual formats. Your system must extract structured data from unstructured layouts.

### **System-Level Reliability Checks**

These checks ensure basic structural integrity before any customer-specific validation. They're fast (milliseconds), deterministic, and catch major failures.

Example checks include:

  - **Field Accuracy.** All required fields are populated (no missing data).
  - **Type Consistency.** Field values match expected data types.
  - **Summation Validation.** Line items should sum to the stated total.
  - **Date Validity.** Dates are plausible and properly formatted.
  - **No Corruption Markers.** Extracted data doesn't contain placeholder text indicating extraction failure.

### **Customer-Specific Validation**

System governance validates structure; customer checks validate **content accuracy** against real-world format diversity.

Customer-level validation relies on small, curated sets of representative documents with human-verified outputs. These examples define what “correct” means for that customer’s layout, vocabulary, and business rules.

Example validation checks include:

  - **Layout Interpretation:** Can the system handle this customer's specific visual format?
  - **Domain Terminology:** Does it correctly parse this customer's industry-specific terms?
  - **Business Rules:** Does output comply with this customer's specific requirements?
  - **Format Diversity:** Does it work on both their native PDFs and scanned images?

As ambiguity increases due to low-quality scans, handwritten annotations, or dense tables cross-model comparison becomes useful. When different models disagree on critical fields, the document should be flagged for review rather than forced into a false sense of certainty.

### **The Number Problem**

Numbers are a persistent failure mode in multimodal extraction. Models are good at recognizing text visually but unreliable at interpreting or transforming numeric values.

The practical solution is separation of concerns: extract numbers exactly as they appear, then apply deterministic parsing and validation outside the model. This prevents plausible but invented values from entering downstream systems.

## Part 3: Voice Agents and Real-Time Constraints

### **Why Voice Is Different**

Voice systems operate under irreversible conditions. Once a word is misheard or a pause feels awkward, the experience degrades immediately. Users cannot skim, reread, or correct silently.

The architecture compounds this risk. Speech-to-text, reasoning, and text-to-speech form a serial pipeline where delays and errors accumulate. Evaluation must therefore focus on timing, continuity, and recovery — not just correctness.

### **The Voice Agent Architecture**

The standard architecture has three sequential components:

User speaks

    ↓

Speech-to-Text (STT): Converts audio to text transcription

    ↓

LLM: Processes text, generates response text

    ↓

Text-to-Speech (TTS): Converts response text to audio

    ↓

User hears response

### **Latency as a Distribution, Not a Target**

Voice interaction is sensitive to rhythm. Consistent pauses of two to three seconds feel broken even if individual responses are “acceptable.” Short, predictable delays are often better than occasional long ones.

Latency should be evaluated as a distribution: typical response time, tail behavior, and worst-case pauses. Different query types justify different budgets, but inconsistency is what users notice first.

**Breaking down the latency budget:**

  - STT (Speech-to-Text): 200-300ms to transcribe user's speech
  - LLM inference: 300-400ms to generate response
  - TTS (Text-to-Speech): 150-200ms to synthesize audio
  - Network overhead: 100ms for transmission
  - **Total: 750-1000ms**

There's very little room for error. A slow database lookup or an extra LLM call can push you over the threshold and break the conversational feel.

### **Interruption and Turn-Taking**

Users interrupt. Systems that cannot stop speaking quickly feel mechanical and frustrating. Evaluation should measure how fast interruptions are detected, whether the agent acknowledges them, and whether it correctly switches intent.

There are exceptions. Compliance-critical speech must sometimes resist interruption. These cases should be explicit in both product design and evaluation criteria.

### **Long-Horizon Context Management**

Voice conversations can span many turns. As context grows, quality often degrades unless critical information is deliberately reinforced.

Evaluation should measure task success across conversation length, not just at the beginning. Drops in success rate after ten or fifteen turns usually indicate context dilution rather than reasoning failure.

### **Evaluating Voice: Three Testing Modalities**

Effective voice evaluation uses three different testing environments. Each reveals different failure modes that the others miss.

**Modality 1: Text-Only Testing**

**What:** Standard text inputs and outputs with no audio involved

**When to use:** Testing conversation logic, instruction following, context management

**What it catches:**

  - Does the agent follow conversation context correctly across multiple turns?
  - Does it ask appropriate clarifying questions when needed?
  - Does response content make logical sense?
  - Does it maintain relevant information from earlier in the conversation?

**What it misses:**

  - Audio-specific failures (misheard words, background noise)
  - Latency issues
  - Prosody and tone problems in synthesized speech
  - Interruption handling

**Modality 2: Synthetic Speech Testing**

**What:** Text-to-speech conversion of test inputs, agent responds with audio output

**When to use:** Testing latency, interruption handling, turn detection, basic STT accuracy

**What it catches:**

  - **End-to-end latency:** Are responses within the 800ms target?
  - **Turn detection:** Does the agent correctly recognize when the user has finished speaking?
  - **"Barge-in" handling:** Can users interrupt the agent mid-response?
  - **Basic STT accuracy:** Does the system transcribe clean, synthetic speech correctly?

**What it misses:**

  - Real-world audio noise (phone line quality, background conversations, traffic)
  - Natural speech patterns (hesitations, "um"s, self-corrections, talking over oneself)
  - Emotional tone detection (frustration, confusion, urgency)
  - Accent and dialect variations

**Modality 3: Human Speech Testing**

**What:** Real humans speaking naturally to the agent in realistic environments

**When to use:** Final validation before launch, ongoing production quality monitoring

**What it catches:**

  - **Accent handling:** Non-native speakers, regional dialects, speech impediments
  - **Background noise tolerance:** Coffee shops (65dB ambient), open offices (55dB), cars (70dB with road noise)
  - **Natural speech patterns:** "Um," "uh," false starts, self-corrections, run-on sentences
  - **Emotional tone detection:** Can the agent recognize when a user is frustrated vs. happy?
  - **Real-world edge cases:** Scenarios synthetic testing would never surface

**What it requires:**

  - Human testers (expensive, doesn't scale)
  - Diverse speaker demographics (age, gender, accent, native language)
  - Realistic audio environments
  - Time for manual analysis

## What You've Learned

By completing this chapter, you now understand:

1.  Why RAG must be evaluated as retrieval and generation, not a single step
2.  How precision, recall, ranking, and *k* reflect product tradeoffs, not just model quality
3.  Why PDFs require separating structural reliability from semantic correctness
4.  Why voice quality depends on consistency, interruption handling, and long-horizon context
5.  How different testing environments expose different classes of failure

Across these capabilities, the pattern is the same. As architectures become more complex, evaluation shifts from judging outputs to managing risk across systems. The techniques in this chapter are not special cases: they are extensions of the same principles you’ve applied throughout the course, pushed into environments where mistakes are harder to hide and more expensive to ignore.
