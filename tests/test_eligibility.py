"""
Unit Test Suite for Government Scheme Eligibility Navigator.
Conforms to Hackathon Master Prompt Section 15: tests/test_eligibility.py
Run via: python -m unittest tests/test_eligibility.py
"""

import unittest
import os
import json
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.rule_engine import SchemeRegistry, RuleEngine
from engine.retriever import PolicyRetriever
from engine.bias_checker import BiasAuditor
from retrieval import DocumentRetriever


class TestEligibilityNavigator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registry = SchemeRegistry()
        cls.engine = RuleEngine(cls.registry)
        cls.bias_auditor = BiasAuditor(cls.engine)
        cls.doc_retriever = DocumentRetriever()

        profiles_path = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_profiles.json")
        with open(profiles_path, "r", encoding="utf-8") as f:
            cls.synthetic_profiles = json.load(f)

    def test_01_registry_loads_all_schemes(self):
        """Verify scheme registry loads 5 versioned schemes with disclaimer."""
        schemes = self.registry.get_all_schemes()
        self.assertEqual(len(schemes), 5, "Expected exactly 5 curated schemes.")
        self.assertTrue(self.registry.version, "Scheme registry version missing.")
        self.assertIn("DISCLAIMER", self.registry.disclaimer, "Statutory disclaimer missing.")

    def test_02_marginal_farmer_eligibility(self):
        """Verify rural farmer (Ramesh Kumar) matches PM-KISAN, PM-JAY, PMAY-G."""
        profile = self.synthetic_profiles[0]["attributes"]
        results = self.engine.evaluate_profile(profile)
        eligible = {r["scheme_id"]: r for r in results if r["status"] == "ELIGIBLE"}

        self.assertIn("PM-KISAN", eligible, "Ramesh Kumar should be eligible for PM-KISAN.")
        self.assertIn("PM-JAY", eligible, "Ramesh Kumar should be eligible for PM-JAY.")
        self.assertIn("PMAY-G", eligible, "Ramesh Kumar should be eligible for PMAY-G.")

        # Check why_you_match details
        pm_kisan = eligible["PM-KISAN"]
        pass_criteria = [p["criterion"] for p in pm_kisan["why_you_match"]]
        self.assertIn("Age Requirement", pass_criteria)
        self.assertIn("Cultivable Land Ownership", pass_criteria)

    def test_03_urban_vendor_eligibility(self):
        """Verify urban street vendor (Sunita Devi) matches PM-SVANIDHI, PM-JAY."""
        profile = self.synthetic_profiles[1]["attributes"]
        results = self.engine.evaluate_profile(profile)
        eligible = {r["scheme_id"]: r for r in results if r["status"] == "ELIGIBLE"}

        self.assertIn("PM-SVANIDHI", eligible, "Sunita Devi should be eligible for PM-SVANIDHI.")
        self.assertIn("PM-JAY", eligible, "Sunita Devi should be eligible for PM-JAY.")

    def test_04_high_income_disqualification(self):
        """Verify high income corporate applicant is disqualified from subsidized welfare."""
        profile = self.synthetic_profiles[6]["attributes"]  # Vikram Adani, ₹22L income
        results = self.engine.evaluate_profile(profile)
        ineligible = {r["scheme_id"]: r for r in results if r["status"] == "INELIGIBLE"}

        self.assertIn("PM-JAY", ineligible, "High income should disqualify from PM-JAY.")
        self.assertIn("PMAY-G", ineligible, "High income should disqualify from PMAY-G.")

        # Check why_you_dont_match reason
        pm_jay_fails = [f["criterion"] for f in ineligible["PM-JAY"]["why_you_dont_match"]]
        self.assertIn("Income Requirement", pm_jay_fails)

    def test_05_missing_info_uncertainty(self):
        """Verify incomplete profile yields UNKNOWN status without guessing."""
        profile = self.synthetic_profiles[7]["attributes"]  # Arun Prasad with None values
        results = self.engine.evaluate_profile(profile)
        unknown_schemes = [r for r in results if r["status"] == "UNKNOWN"]

        self.assertGreater(len(unknown_schemes), 0, "Incomplete profile must return UNKNOWN status.")
        first_unknown = unknown_schemes[0]
        self.assertGreater(len(first_unknown["missing_information"]), 0)
        self.assertLess(first_unknown["confidence_score"], 1.0, "Confidence score should reflect missing info.")

    def test_06_grounded_document_retrieval(self):
        """Verify document retriever finds supporting text from documents/*.txt."""
        res = self.doc_retriever.search_documents("street vendor working capital loan", top_k=1)
        self.assertGreater(len(res), 0, "Should retrieve policy document passage.")
        self.assertEqual(res[0]["scheme_id"], "PM-SVANIDHI", "Should retrieve PM-SVANIDHI document.")
        self.assertIn("citation", res[0], "Passage must include citation.")

    def test_07_demographic_parity_zero_bias(self):
        """Verify counterfactual perturbation audit confirms zero demographic bias."""
        profile = self.synthetic_profiles[0]["attributes"]
        audit = self.bias_auditor.audit_profile_fairness(profile)
        self.assertTrue(audit["is_certified_unbiased"], "System must be certified 100% unbiased.")
        self.assertEqual(audit["violations_detected"], 0, "No demographic parity violations permitted.")
        self.assertEqual(audit["demographic_fairness_score"], "100.0%")


if __name__ == "__main__":
    unittest.main()
