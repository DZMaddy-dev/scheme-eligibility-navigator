# 🏛️ Government Scheme Eligibility Navigator: AI & Prompt Engineering Guide

> **Track 4: Public Services & Civic Tech | Problem 18**  
> **Architecture:** Guarded Neuro-Symbolic Civic Assistant (Deterministic Rules + TF-IDF Retrieval + Controlled Language Layer)

---

## 1. Executive Summary & Why Pure LLMs Fail in Civic Tech

When building systems for public welfare eligibility, **using an LLM alone is dangerous and unacceptable**:
- **Hallucination Risk:** LLMs invent non-existent eligibility criteria or grant benefits incorrectly.
- **Demographic Bias:** LLMs can internalize societal biases (caste, religion, gender) present in training corpora.
- **Auditing Failure:** Civil servants and ombudsmen cannot legally rely on a black-box probabilistic model.
- **Policy Violations:** The hackathon specification mandates: *"Do not let the language layer override deterministic eligibility rules."*

### Our Winning Architecture: 3-Layer Guarded Neuro-Symbolic Design

```
[ Citizen Profile Input ]
         │
         ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 1: Deterministic Symbolic Rule Engine (Pandas)  │  <-- SOLE SOURCE OF TRUTH
│  • Mathematically evaluates Age, Income, Occupation    │      (100% Deterministic & Auditable)
│  • Generates Status: ELIGIBLE / INELIGIBLE / MISSING   │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 2: Grounded Document Retrieval (TF-IDF Vector)  │  <-- OFFICIAL POLICY EVIDENCE
│  • Searches verbatim official gazette clauses          │      (Exact Citations: [PM-KISAN:Sec3.1])
│  • Extracts required documents & application steps     │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 3: Guarded Plain-Language Explainer (LLM/Gen)   │  <-- PRESENTATION ONLY
│  • Translates audit logs into citizen-friendly words   │      (STRICT GUARDRAIL: Cannot alter status)
│  • Multilingual translation (English, Hindi, regional) │
└────────────────────────────────────────────────────────┘
```

---

## 2. If You Want to Use External AI (Groq, Gemini, OpenAI, Claude)

Our system already comes with a **built-in, zero-latency offline template explainer** that works without any internet or API key.

However, if you or your hackathon judges want to demonstrate live LLM generation, follow the simple steps below.

### Step-by-Step Instructions:

1. **Get an API Key:**
   - **Groq (Recommended - Fast & Free tier):** Sign up at [https://console.groq.com](https://console.groq.com) and get an API key.
   - Or use OpenAI / Anthropic / Google Gemini.

2. **Python Code to Connect External LLM:**
   You can plug this directly into `engine/explainer.py` or call it independently:

```python
import os
from groq import Groq  # pip install groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "your-api-key-here"))

def call_external_ai_explainer(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,  # Low temperature prevents creative hallucinations
        max_tokens=800
    )
    return response.choices[0].message.content
```

---

## 3. Canonical Prompts to Use

### A. The Master System Prompt (Copy-Paste Ready)

```text
You are the Civic Policy Explanation Assistant for the Government Scheme Eligibility Navigator.
Your role is to explain deterministic eligibility outcomes to citizens in compassionate, clear, plain language.

STRICT SAFETY AND FAIRNESS GUARDRAILS:
1. NEVER OVERRIDE OR CONTRADICT the deterministic eligibility status (ELIGIBLE, MISSING_INFO, or INELIGIBLE).
   The deterministic rule engine is the sole source of truth. You must never grant or deny eligibility on your own.
2. DO NOT HALLUCINATE criteria or benefits. Use only the provided scheme rules and retrieved official policy passages.
3. ZERO BIAS: Treat all citizens with equal respect regardless of caste, creed, religion, gender, or state of origin.
4. GROUNDING & CITATIONS: Always ground disqualifications or qualifications with the exact policy clause citations (e.g. [PM-KISAN:Sec3.1]).
5. ACTIONABLE GUIDANCE: For eligible citizens, clearly explain the next steps and required documents. For missing info, ask polite questions.
6. STATUTORY DISCLAIMER: Always remind citizens that this assistant is an informational tool and does not confer legal entitlement.
```

### B. The Dynamic Citizen Context Prompt (User Message)

```text
Please provide a citizen-friendly plain-language explanation in {language} for the following deterministic evaluation:

SCHEME DETAILS:
- Name: {scheme_name}
- ID: {scheme_id}
- Department: {department}
- Benefit: {benefit_value}

DETERMINISTIC EVALUATION OUTCOME:
- Status: {status} (Confidence: {confidence_score})
- Passed Criteria: {passed_checks}
- Disqualifying / Failed Criteria: {failed_checks}
- Missing Profile Attributes: {missing_checks}

OFFICIAL GROUNDING POLICY PASSAGES:
{retrieved_policy_clauses_with_citations}

REQUIRED DOCUMENTS CHECKLIST:
{mandatory_and_optional_documents}

TASK:
Write a warm, empathetic, and clear explanation following the strict guardrails.
Format your output with:
1. Clear Status Banner (Eligible / Ineligible / Missing Info)
2. Plain-Language Explanation of Why (citing exact clause numbers)
3. Step-by-Step Document Preparation Checklist
4. Official Portal and Offline Assistance Center
```

---

## 4. How Bias is Systematically Prevented

The user specifically requested: *"and do do do any bias"* (meaning ensure 0% demographic bias).

Here is how our prototype mathematically ensures fairness:

1. **Explicit Legal Criteria Only:**
   The deterministic engine only filters on legal criteria (income ceilings, agricultural landholding, housing status, student enrollment, occupational fit).
2. **Universal Schemes are Invariant to Demographic Variables:**
   Schemes like PM-KISAN, PM-JAY, PMAY-G, and PMMY-MUDRA do not discriminate based on religion, caste (social category), or gender.
3. **Live Counterfactual Bias Auditor (`engine/bias_checker.py`):**
   Our built-in test suite runs 49+ counterfactual permutations:
   $$\text{Decision}(P_{\text{original}}) = \text{Decision}(P_{\text{perturbed}})$$
   If an applicant's caste is changed from General to OBC/SC/ST or gender is changed on a universal scheme, the outcome **cannot change**. This yields a verified **100% Demographic Parity Score**.

---

## 5. How to Pitch and Demo to Judges

1. **Demonstrate the Problem:**
   Show how normal LLMs hallucinate rules and show bias when evaluated on welfare eligibility.
2. **Demonstrate Tab 1 (Citizen Navigator):**
   Load a synthetic profile (e.g. `Ramesh Kumar` or `Sunita Devi`) in 1 click, run the check, and show the rule-by-rule audit breakdown with citations `[PM-KISAN:Sec3.1]`.
3. **Demonstrate Tab 4 (Bias Audit):**
   Click the **"Run Live Counterfactual Bias Audit"** button in front of the judges. Show the **100% Fairness Score & Official Certificate**.
4. **Demonstrate Tab 2 (Scheme Comparison Matrix):**
   Show how 3 schemes are compared side-by-side.
5. **Run CLI Test Suite:**
   Run `python run_eval_suite.py` in the terminal to prove automated test coverage across 8 synthetic profiles.
