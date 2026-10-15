"""
Plain-Language Grounded Explainer and Multilingual Generator.
Operates strictly as a guarded presentation layer:
The language layer NEVER overrides deterministic rule outcomes.
Includes offline instant template synthesis and optional external LLM integration.
"""

from typing import Dict, List, Any, Optional
import os


# Pre-built bilingual translations for common policy terms
TRANSLATIONS = {
    "ELIGIBLE": {"en": "Eligible (Matches All Criteria)", "hi": "पात्र (सभी मानदंडों को पूरा करता है)"},
    "CONDITIONALLY_ELIGIBLE": {"en": "Conditionally Eligible", "hi": "सशर्त पात्र (दस्तावेज़ सत्यापन आवश्यक)"},
    "MISSING_INFO": {"en": "Action Needed: Missing Information", "hi": "कार्रवाई आवश्यक: अधूरी जानकारी"},
    "INELIGIBLE": {"en": "Not Eligible", "hi": "अपात्र (मानदंड पूरे नहीं होते)"},
    "passed": {"en": "Passed Rules", "hi": "संतुष्ट शर्तें"},
    "failed": {"en": "Disqualifying Criteria", "hi": "अपात्रता के कारण"},
    "missing": {"en": "Missing Details", "hi": "अपेक्षित अतिरिक्त विवरण"},
    "docs": {"en": "Required Documents Checklist", "hi": "आवश्यक दस्तावेजों की सूची"},
    "next_steps": {"en": "Application Next Steps", "hi": "आवेदन प्रक्रिया एवं अगले कदम"}
}


class Explainer:
    """
    Translates deterministic rule evaluation audit trails into compassionate,
    plain-language explanations with official citations and zero hallucination.
    """

    def __init__(self):
        pass

    def generate_explanation(
        self,
        evaluation: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generates a grounded plain-language explanation strictly conditioned on
        the deterministic evaluation report.
        """
        status = evaluation["status"]
        name = evaluation["name"]
        hindi_name = evaluation.get("hindi_name", name)
        scheme_id = evaluation["scheme_id"]
        benefit = evaluation.get("benefit_value", "")
        passed = evaluation.get("passed_checks", [])
        failed = evaluation.get("failed_checks", [])
        missing = evaluation.get("missing_checks", [])
        docs = evaluation.get("required_documents", [])
        process = evaluation.get("application_process", {})

        lang = "hi" if language.lower() in ["hi", "hindi"] else "en"
        display_name = f"{name} ({hindi_name})" if lang == "hi" else name

        if lang == "hi":
            summary_text = self._build_hindi_summary(status, display_name, benefit, passed, failed, missing)
        else:
            summary_text = self._build_english_summary(status, display_name, benefit, passed, failed, missing)

        # Build auditable citation list
        citations = []
        for p in passed:
            if "citation" in p:
                citations.append(p["citation"])
        for f in failed:
            if "citation" in f:
                citations.append(f["citation"])

        # Deduplicate citations
        unique_citations = list(dict.fromkeys(citations))

        return {
            "scheme_id": scheme_id,
            "status": status,
            "status_label": TRANSLATIONS.get(status, {}).get(lang, status),
            "summary_text": summary_text,
            "citations": unique_citations,
            "required_documents": docs,
            "application_steps": process.get("steps", []),
            "portal_url": process.get("portal_url", ""),
            "offline_center": process.get("offline_center", "")
        }

    def _build_english_summary(
        self,
        status: str,
        name: str,
        benefit: str,
        passed: List[Dict],
        failed: List[Dict],
        missing: List[Dict]
    ) -> str:
        if status == "ELIGIBLE":
            msg = f"You satisfy all established eligibility requirements for **{name}**. "
            if benefit:
                msg += f"Through this program, eligible beneficiaries receive **{benefit}**. "
            msg += "\n\n**Verified Eligibility Points:**\n"
            for p in passed:
                msg += f"- {p['criterion']}: {p['reason']} *{p.get('citation', '')}*\n"
            msg += "\nTo proceed, please ensure you have the mandatory documents listed below."
            return msg

        elif status == "MISSING_INFO":
            msg = f"We could not definitively determine your eligibility for **{name}** because some required profile information is missing:\n\n"
            for m in missing:
                msg += f"- **{m['criterion']}**: {m['question']} (*Impact: {m['impact']}*)\n"
            msg += "\nPlease provide these details in the profile form to receive a verified eligibility decision."
            return msg

        elif status == "INELIGIBLE":
            msg = f"Based on statutory policy guidelines, you are currently not eligible for **{name}**.\n\n"
            msg += "**Disqualifying Factor(s):**\n"
            for f in failed:
                msg += f"- **{f['criterion']}**: {f['reason']} *{f.get('citation', '')}*\n"
            if passed:
                msg += "\n*Criteria that were satisfied:*\n"
                for p in passed[:3]:
                    msg += f"- {p['criterion']}: {p['reason']}\n"
            return msg

        else:
            return f"Status for {name}: {status}."

    def _build_hindi_summary(
        self,
        status: str,
        name: str,
        benefit: str,
        passed: List[Dict],
        failed: List[Dict],
        missing: List[Dict]
    ) -> str:
        if status == "ELIGIBLE":
            msg = f"बधाई हो! आप **{name}** के सभी निर्धारित पात्रता मानदंडों को पूरा करते हैं। "
            if benefit:
                msg += f"इस योजना के अंतर्गत पात्र लाभार्थियों को **{benefit}** प्रदान किया जाता है। "
            msg += "\n\n**सत्यापित पात्रता बिंदु:**\n"
            for p in passed:
                msg += f"- {p['criterion']}: {p['reason']} *{p.get('citation', '')}*\n"
            msg += "\nकृपया आवेदन के लिए नीचे दिए गए आवश्यक दस्तावेज़ तैयार रखें।"
            return msg

        elif status == "MISSING_INFO":
            msg = f"हम **{name}** के लिए आपकी पात्रता का पूर्ण निर्धारण नहीं कर सके क्योंकि कुछ आवश्यक जानकारी अधूरी है:\n\n"
            for m in missing:
                msg += f"- **{m['criterion']}**: {m['question']} (*महत्व: {m['impact']}*)\n"
            msg += "\nकृपया निश्चित परिणाम जानने के लिए यह जानकारी प्रोफाइल में दर्ज करें।"
            return msg

        elif status == "INELIGIBLE":
            msg = f"सरकारी नियमों के अनुसार, आप वर्तमान में **{name}** के लिए पात्र नहीं हैं।\n\n"
            msg += "**अपात्रता के मुख्य कारण:**\n"
            for f in failed:
                msg += f"- **{f['criterion']}**: {f['reason']} *{f.get('citation', '')}*\n"
            return msg

        else:
            return f"{name} की स्थिति: {status}."


# Canonical System Prompt for external AI Integration (Groq/OpenAI/Gemini/Claude)
EXTERNAL_AI_SYSTEM_PROMPT = """You are the Civic Policy Explanation Assistant for the Government Scheme Eligibility Navigator.
Your role is to explain deterministic eligibility outcomes to citizens in compassionate, clear, plain language.

STRICT SAFETY AND FAIRNESS GUARDRAILS:
1. NEVER OVERRIDE OR CONTRADICT the deterministic eligibility status (ELIGIBLE, MISSING_INFO, or INELIGIBLE).
   The deterministic rule engine is the sole source of truth. You must never grant or deny eligibility on your own.
2. DO NOT HALLUCINATE criteria or benefits. Use only the provided scheme rules and retrieved official policy passages.
3. ZERO BIAS: Treat all citizens with equal respect regardless of caste, creed, religion, gender, or state of origin.
4. GROUNDING & CITATIONS: Always ground disqualifications or qualifications with the exact policy clause citations (e.g. [PM-KISAN:Sec3.1]).
5. ACTIONABLE GUIDANCE: For eligible citizens, clearly explain the next steps and required documents. For missing info, ask polite questions.
6. STATUTORY DISCLAIMER: Always remind citizens that this assistant is an informational tool and does not confer legal entitlement.
"""


def get_llm_prompt(evaluation_report: Dict[str, Any], language: str = "en") -> str:
    """
    Generates the exact formatted user prompt for any external LLM
    (such as Groq, Gemini, OpenAI, Claude).
    """
    return f"""Please provide a citizen-friendly plain-language explanation in {language} for the following deterministic evaluation:

SCHEME DETAILS:
- Name: {evaluation_report['name']} ({evaluation_report.get('hindi_name', '')})
- ID: {evaluation_report['scheme_id']}
- Department: {evaluation_report.get('department')}
- Benefit: {evaluation_report.get('benefit_value')}

DETERMINISTIC EVALUATION OUTCOME:
- Status: {evaluation_report['status']} (Confidence: {evaluation_report.get('confidence_score', 1.0)})
- Passed Criteria: {evaluation_report.get('passed_checks')}
- Disqualifying / Failed Criteria: {evaluation_report.get('failed_checks')}
- Missing Profile Attributes: {evaluation_report.get('missing_checks')}

OFFICIAL GROUNDING POLICY PASSAGES:
{evaluation_report.get('policy_passages', [])}

TASK:
Write a warm, empathetic, and clear explanation following the strict guardrails.
"""
