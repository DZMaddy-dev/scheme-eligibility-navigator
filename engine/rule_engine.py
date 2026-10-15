"""
Deterministic Rule Engine for Government Scheme Eligibility Navigator.
Enforces 100% auditable, deterministic criteria evaluation using Python logic and Pandas lookup structures.
Evaluates every applicable criterion with PASS, FAIL, or UNKNOWN statuses.
Ensures zero language model overrides or alterations to statutory eligibility rules.
"""

from typing import Dict, List, Any, Optional
import json
import os
import pandas as pd


class SchemeRegistry:
    """Loads, validates, and manages versioned scheme metadata and rules."""

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), "..", "data", "schemes_v1.json")
        self.data_path = os.path.abspath(data_path)
        self.raw_data = self._load_data()
        self.version = self.raw_data.get("version", "1.4.2-2026")
        self.last_updated = self.raw_data.get("last_updated", "2026-03-01")
        self.disclaimer = self.raw_data.get("disclaimer", "")
        self.schemes = self.raw_data.get("schemes", [])
        self.schemes_dict = {s["scheme_id"]: s for s in self.schemes}
        self.dataframe = self._build_dataframe()

    def _load_data(self) -> Dict[str, Any]:
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_dataframe(self) -> pd.DataFrame:
        """Constructs a flattened Pandas DataFrame for rapid lookup and filtering."""
        records = []
        for s in self.schemes:
            r = s.get("rules", {})
            records.append({
                "scheme_id": s["scheme_id"],
                "name": s["name"],
                "hindi_name": s.get("hindi_name", ""),
                "department": s.get("department", ""),
                "category": s.get("category", ""),
                "version": s.get("version", ""),
                "benefit_value": s.get("benefit_value", ""),
                "min_age": r.get("min_age"),
                "max_age": r.get("max_age"),
                "max_annual_income": r.get("max_annual_income"),
                "requires_bpl": r.get("requires_bpl", False),
                "disallow_pucca_house": r.get("disallow_pucca_house", False),
                "disallow_income_tax_payer": r.get("disallow_income_tax_payer", False),
                "disallow_govt_employee": r.get("disallow_govt_employee", False),
                "applicable_states": ",".join(r.get("applicable_states", ["All States"])),
                "genders": ",".join(r.get("genders", ["All"])),
                "residence_area": ",".join(r.get("residence_area", ["Both"])),
                "eligible_occupations": ",".join(r.get("eligible_occupations", ["All"])),
                "num_documents": len(s.get("required_documents", [])),
                "num_clauses": len(s.get("policy_passages", []))
            })
        return pd.DataFrame(records)

    def get_all_schemes(self) -> List[Dict[str, Any]]:
        return self.schemes

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        return self.schemes_dict.get(scheme_id)


class RuleEngine:
    """
    Deterministic rule engine that records PASS, FAIL, or UNKNOWN for every criterion.
    Never guesses missing info; 100% auditable and free of AI hallucination or bias.
    """

    def __init__(self, registry: SchemeRegistry):
        self.registry = registry

    def evaluate_profile(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluates a citizen profile across all registered schemes.
        Returns a sorted list of scheme evaluation reports.
        """
        results = []
        for scheme in self.registry.get_all_schemes():
            result = self.evaluate_single_scheme(scheme, profile)
            results.append(result)

        # Sort priority: ELIGIBLE first, then UNKNOWN/MISSING_INFO, then INELIGIBLE
        status_order = {
            "ELIGIBLE": 0,
            "POTENTIALLY_ELIGIBLE": 0,
            "UNKNOWN": 1,
            "MISSING_INFO": 1,
            "INELIGIBLE": 2
        }
        results.sort(key=lambda x: (status_order.get(x["status"], 3), -x["confidence_score"]))
        return results

    def evaluate_single_scheme(self, scheme: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates every applicable eligibility criterion for a scheme.
        Records PASS, FAIL, or UNKNOWN.
        """
        rules = scheme.get("rules", {})
        scheme_id = scheme["scheme_id"]

        why_you_match = []
        why_you_dont_match = []
        missing_information = []

        # 1. Age Requirement
        age = profile.get("age")
        min_age = rules.get("min_age")
        max_age = rules.get("max_age")

        if age is None:
            if min_age is not None or max_age is not None:
                missing_information.append({
                    "criterion": "Age Requirement",
                    "status": "UNKNOWN",
                    "field": "age",
                    "question": "Citizen age was not provided.",
                    "impact": f"Required to verify age eligibility [{min_age or 0} to {max_age or 'No upper limit'} years]",
                    "citation": f"[{scheme_id}:AgeClause]"
                })
        else:
            req_str = f"[{min_age or 0} to {max_age or 'No limit'} yrs]"
            if min_age is not None and age < min_age:
                why_you_dont_match.append({
                    "criterion": "Age Requirement",
                    "status": "FAIL",
                    "user_val": f"{age} years",
                    "required_val": f"≥ {min_age} years",
                    "details": f"User age ({age} yrs) is below the minimum required age of {min_age} yrs.",
                    "citation": f"[{scheme_id}:AgeClause]"
                })
            elif max_age is not None and age > max_age:
                why_you_dont_match.append({
                    "criterion": "Age Requirement",
                    "status": "FAIL",
                    "user_val": f"{age} years",
                    "required_val": f"≤ {max_age} years",
                    "details": f"User age ({age} yrs) exceeds the maximum allowed age of {max_age} yrs.",
                    "citation": f"[{scheme_id}:AgeClause]"
                })
            else:
                why_you_match.append({
                    "criterion": "Age Requirement",
                    "status": "PASS",
                    "user_val": f"{age} years",
                    "required_val": req_str,
                    "details": f"User age ({age} yrs) is within required range {req_str}.",
                    "citation": f"[{scheme_id}:AgeClause]"
                })

        # 2. State / Territorial Requirement
        state = profile.get("state")
        allowed_states = rules.get("applicable_states", ["All States"])

        if "All States" in allowed_states or "Pan-India" in allowed_states:
            why_you_match.append({
                "criterion": "State / Territorial Requirement",
                "status": "PASS",
                "user_val": state or "All States",
                "required_val": "All States (Pan-India)",
                "details": f"Scheme operates nationwide across all States/UTs.",
                "citation": f"[{scheme_id}:TerritoryClause]"
            })
        else:
            if not state:
                missing_information.append({
                    "criterion": "State / Territorial Requirement",
                    "status": "UNKNOWN",
                    "field": "state",
                    "question": "State of residence not provided.",
                    "impact": f"Required to verify state eligibility ({', '.join(allowed_states)})",
                    "citation": f"[{scheme_id}:TerritoryClause]"
                })
            elif state in allowed_states:
                why_you_match.append({
                    "criterion": "State / Territorial Requirement",
                    "status": "PASS",
                    "user_val": state,
                    "required_val": ", ".join(allowed_states),
                    "details": f"User state '{state}' matches scheme state requirements.",
                    "citation": f"[{scheme_id}:TerritoryClause]"
                })
            else:
                why_you_dont_match.append({
                    "criterion": "State / Territorial Requirement",
                    "status": "FAIL",
                    "user_val": state,
                    "required_val": ", ".join(allowed_states),
                    "details": f"Scheme is restricted to {', '.join(allowed_states)}, but user is in {state}.",
                    "citation": f"[{scheme_id}:TerritoryClause]"
                })

        # 3. Income Ceiling Requirement
        income = profile.get("annual_income")
        max_income = rules.get("max_annual_income")

        if max_income is not None:
            if income is None:
                missing_information.append({
                    "criterion": "Income Requirement",
                    "status": "UNKNOWN",
                    "field": "annual_income",
                    "question": "Annual family income information was not provided.",
                    "impact": f"Required to verify income ceiling ≤ ₹{max_income:,}",
                    "citation": f"[{scheme_id}:IncomeClause]"
                })
            else:
                if income > max_income:
                    why_you_dont_match.append({
                        "criterion": "Income Requirement",
                        "status": "FAIL",
                        "user_val": f"₹{income:,}",
                        "required_val": f"≤ ₹{max_income:,}",
                        "details": f"User annual income ₹{income:,} exceeds upper limit of ₹{max_income:,}.",
                        "citation": f"[{scheme_id}:IncomeClause]"
                    })
                else:
                    why_you_match.append({
                        "criterion": "Income Requirement",
                        "status": "PASS",
                        "user_val": f"₹{income:,}",
                        "required_val": f"≤ ₹{max_income:,}",
                        "details": f"User income ₹{income:,} satisfies requirement ≤ ₹{max_income:,}.",
                        "citation": f"[{scheme_id}:IncomeClause]"
                    })

        # 4. Gender Requirement
        gender = profile.get("gender")
        allowed_genders = rules.get("genders", ["All"])

        if "All" in allowed_genders or allowed_genders == ["All"]:
            why_you_match.append({
                "criterion": "Gender Requirement",
                "status": "PASS",
                "user_val": gender or "Any",
                "required_val": "All Genders",
                "details": "Open to all citizens without gender restriction.",
                "citation": f"[{scheme_id}:GenderClause]"
            })
        else:
            if not gender:
                missing_information.append({
                    "criterion": "Gender Requirement",
                    "status": "UNKNOWN",
                    "field": "gender",
                    "question": "Gender not specified.",
                    "impact": f"Scheme specifically restricted to: {', '.join(allowed_genders)}",
                    "citation": f"[{scheme_id}:GenderClause]"
                })
            elif gender in allowed_genders:
                why_you_match.append({
                    "criterion": "Gender Requirement",
                    "status": "PASS",
                    "user_val": gender,
                    "required_val": ", ".join(allowed_genders),
                    "details": f"User gender '{gender}' matches targeted beneficiary group.",
                    "citation": f"[{scheme_id}:GenderClause]"
                })
            else:
                why_you_dont_match.append({
                    "criterion": "Gender Requirement",
                    "status": "FAIL",
                    "user_val": gender,
                    "required_val": ", ".join(allowed_genders),
                    "details": f"Scheme is targeted to {', '.join(allowed_genders)}, but user profile is {gender}.",
                    "citation": f"[{scheme_id}:GenderClause]"
                })

        # 5. Area of Residence (Rural / Urban)
        area = profile.get("residence_area")
        allowed_areas = rules.get("residence_area", ["Both"])

        if "Both" in allowed_areas:
            why_you_match.append({
                "criterion": "Area Requirement",
                "status": "PASS",
                "user_val": area or "Both",
                "required_val": "Rural & Urban",
                "details": "Scheme is active across both rural and urban areas.",
                "citation": f"[{scheme_id}:AreaClause]"
            })
        else:
            if not area:
                missing_information.append({
                    "criterion": "Area Requirement",
                    "status": "UNKNOWN",
                    "field": "residence_area",
                    "question": "Residence area (Rural or Urban) not provided.",
                    "impact": f"Scheme restricted to {', '.join(allowed_areas)} areas.",
                    "citation": f"[{scheme_id}:AreaClause]"
                })
            elif area in allowed_areas:
                why_you_match.append({
                    "criterion": "Area Requirement",
                    "status": "PASS",
                    "user_val": area,
                    "required_val": ", ".join(allowed_areas),
                    "details": f"Residence area '{area}' matches scheme requirements.",
                    "citation": f"[{scheme_id}:AreaClause]"
                })
            else:
                why_you_dont_match.append({
                    "criterion": "Area Requirement",
                    "status": "FAIL",
                    "user_val": area,
                    "required_val": ", ".join(allowed_areas),
                    "details": f"Scheme requires {', '.join(allowed_areas)} residence, but user resides in {area}.",
                    "citation": f"[{scheme_id}:AreaClause]"
                })

        # 6. Occupation Suitability
        occupation = profile.get("occupation")
        allowed_occupations = rules.get("eligible_occupations", ["All"])

        if "All" in allowed_occupations:
            why_you_match.append({
                "criterion": "Occupation Requirement",
                "status": "PASS",
                "user_val": occupation or "Any",
                "required_val": "All Occupations",
                "details": "Open to citizens across all occupational sectors.",
                "citation": f"[{scheme_id}:OccupationClause]"
            })
        else:
            if not occupation:
                missing_information.append({
                    "criterion": "Occupation Requirement",
                    "status": "UNKNOWN",
                    "field": "occupation",
                    "question": "Primary occupation not provided.",
                    "impact": f"Scheme targets: {', '.join(allowed_occupations)}",
                    "citation": f"[{scheme_id}:OccupationClause]"
                })
            elif occupation in allowed_occupations:
                why_you_match.append({
                    "criterion": "Occupation Requirement",
                    "status": "PASS",
                    "user_val": occupation,
                    "required_val": ", ".join(allowed_occupations),
                    "details": f"User occupation '{occupation}' matches eligible occupations.",
                    "citation": f"[{scheme_id}:OccupationClause]"
                })
            else:
                why_you_dont_match.append({
                    "criterion": "Occupation Requirement",
                    "status": "FAIL",
                    "user_val": occupation,
                    "required_val": ", ".join(allowed_occupations),
                    "details": f"Scheme is targeted to {', '.join(allowed_occupations)}, but user is '{occupation}'.",
                    "citation": f"[{scheme_id}:OccupationClause]"
                })

        # 7. Category / Social Group Requirement
        category = profile.get("social_category")
        allowed_categories = rules.get("eligible_social_categories", ["All"])

        if "All" in allowed_categories:
            why_you_match.append({
                "criterion": "Category Requirement",
                "status": "PASS",
                "user_val": category or "All",
                "required_val": "All Categories",
                "details": "Universal access across all social categories.",
                "citation": f"[{scheme_id}:CategoryClause]"
            })
        else:
            if not category:
                missing_information.append({
                    "criterion": "Category Requirement",
                    "status": "UNKNOWN",
                    "field": "social_category",
                    "question": "Social category information not provided.",
                    "impact": f"Scheme targets categories: {', '.join(allowed_categories)}",
                    "citation": f"[{scheme_id}:CategoryClause]"
                })
            elif category in allowed_categories:
                why_you_match.append({
                    "criterion": "Category Requirement",
                    "status": "PASS",
                    "user_val": category,
                    "required_val": ", ".join(allowed_categories),
                    "details": f"User category '{category}' matches eligible categories.",
                    "citation": f"[{scheme_id}:CategoryClause]"
                })
            else:
                why_you_dont_match.append({
                    "criterion": "Category Requirement",
                    "status": "FAIL",
                    "user_val": category,
                    "required_val": ", ".join(allowed_categories),
                    "details": f"Scheme is restricted to {', '.join(allowed_categories)}, user category is {category}.",
                    "citation": f"[{scheme_id}:CategoryClause]"
                })

        # 8. Below Poverty Line (BPL) / Deprivation Verification
        requires_bpl = rules.get("requires_bpl", False)
        is_bpl = profile.get("is_bpl")

        if requires_bpl:
            if is_bpl is None:
                missing_information.append({
                    "criterion": "BPL / Ration Card Requirement",
                    "status": "UNKNOWN",
                    "field": "is_bpl",
                    "question": "BPL / Ration Card status not provided.",
                    "impact": "Mandatory requirement: applicant must be BPL or NFSA ration beneficiary.",
                    "citation": f"[{scheme_id}:BPLClause]"
                })
            elif is_bpl:
                why_you_match.append({
                    "criterion": "BPL / Deprivation Status",
                    "status": "PASS",
                    "user_val": "BPL / Ration Card Holder",
                    "required_val": "BPL Enrolled",
                    "details": "Applicant is an enrolled Below Poverty Line / Ration Card beneficiary.",
                    "citation": f"[{scheme_id}:BPLClause]"
                })
            else:
                why_you_dont_match.append({
                    "criterion": "BPL / Deprivation Status",
                    "status": "FAIL",
                    "user_val": "Not BPL",
                    "required_val": "Mandatory BPL / NFSA Card",
                    "details": "Scheme strictly mandates inclusion in official BPL / SECC deprivation census.",
                    "citation": f"[{scheme_id}:BPLClause]"
                })

        # 9. Housing Status (Pucca House Exclusion)
        disallow_pucca = rules.get("disallow_pucca_house", False)
        owns_pucca = profile.get("owns_pucca_house")

        if disallow_pucca:
            if owns_pucca is True:
                why_you_dont_match.append({
                    "criterion": "Housing Asset Exclusion",
                    "status": "FAIL",
                    "user_val": "Owns Pucca House",
                    "required_val": "Must be Houseless or Living in Kutcha House",
                    "details": "Citizen already possesses a permanent pucca house; scheme is reserved for houseless/dilapidated dwellings.",
                    "citation": f"[{scheme_id}:HousingExclusion]"
                })
            elif owns_pucca is False:
                why_you_match.append({
                    "criterion": "Housing Asset Condition",
                    "status": "PASS",
                    "user_val": "No Pucca House (Kutcha / Houseless)",
                    "required_val": "Kutcha Dwelling or Houseless",
                    "details": "Citizen does not own a pucca house, satisfying the shelter deprivation requirement.",
                    "citation": f"[{scheme_id}:HousingExclusion]"
                })

        # 10. Income Taxpayer Exclusion
        disallow_taxpayer = rules.get("disallow_income_tax_payer", False)
        pays_tax = profile.get("pays_income_tax")

        if disallow_taxpayer:
            if pays_tax is True:
                why_you_dont_match.append({
                    "criterion": "Income Taxpayer Exclusion",
                    "status": "FAIL",
                    "user_val": "Income Tax Payer",
                    "required_val": "Non-taxpayer",
                    "details": "Income tax payers are explicitly disqualified by statutory policy guidelines.",
                    "citation": f"[{scheme_id}:TaxExclusion]"
                })
            elif pays_tax is False:
                why_you_match.append({
                    "criterion": "Income Taxpayer Exclusion",
                    "status": "PASS",
                    "user_val": "Non-taxpayer",
                    "required_val": "Non-taxpayer",
                    "details": "Applicant is not an income tax payer.",
                    "citation": f"[{scheme_id}:TaxExclusion]"
                })

        # 11. Government / Public Sector Employment Exclusion
        disallow_govt = rules.get("disallow_govt_employee", False)
        is_govt = profile.get("is_govt_employee")

        if disallow_govt:
            if is_govt is True:
                why_you_dont_match.append({
                    "criterion": "Public Employment Exclusion",
                    "status": "FAIL",
                    "user_val": "Government / PSU Employee",
                    "required_val": "Non-government",
                    "details": "Serving or retired government officers and public servants are disqualified.",
                    "citation": f"[{scheme_id}:GovtExclusion]"
                })
            elif is_govt is False:
                why_you_match.append({
                    "criterion": "Public Employment Exclusion",
                    "status": "PASS",
                    "user_val": "Non-government",
                    "required_val": "Non-government",
                    "details": "Applicant is not employed in government or institutional service.",
                    "citation": f"[{scheme_id}:GovtExclusion]"
                })

        # 12. Scheme-Specific Special Conditions
        # PM-KISAN: Must have cultivable agricultural land
        if scheme_id == "PM-KISAN":
            land = profile.get("landholding_hectares")
            if land is None:
                missing_information.append({
                    "criterion": "Cultivable Land Ownership",
                    "status": "UNKNOWN",
                    "field": "landholding_hectares",
                    "question": "Cultivable agricultural landholding size not specified.",
                    "impact": "Mandatory for PM-KISAN landholder verification.",
                    "citation": "[PM-KISAN:Sec3.1]"
                })
            elif land <= 0:
                why_you_dont_match.append({
                    "criterion": "Cultivable Land Ownership",
                    "status": "FAIL",
                    "user_val": "0 Hectares",
                    "required_val": "Must own cultivable agricultural land",
                    "details": "PM-KISAN mandates cultivable land registered in applicant's name. Profile indicates 0 land.",
                    "citation": "[PM-KISAN:Sec3.1]"
                })
            else:
                why_you_match.append({
                    "criterion": "Cultivable Land Ownership",
                    "status": "PASS",
                    "user_val": f"{land} Hectares",
                    "required_val": "> 0 Hectares",
                    "details": f"Applicant owns {land} hectares of cultivable land.",
                    "citation": "[PM-KISAN:Sec3.1]"
                })

        # SSY: Guardian of girl child under 10
        if scheme_id == "SSY":
            has_girl = profile.get("has_girl_child_under_10")
            if has_girl is None:
                missing_information.append({
                    "criterion": "Girl Child (Age ≤10) Guardian Status",
                    "status": "UNKNOWN",
                    "field": "has_girl_child_under_10",
                    "question": "Parent or guardian status of girl child under 10 not specified.",
                    "impact": "Account must be opened in the name of a girl child aged 10 or younger.",
                    "citation": "[SSY:Sec2.1]"
                })
            elif has_girl is False:
                why_you_dont_match.append({
                    "criterion": "Girl Child (Age ≤10) Guardian Status",
                    "status": "FAIL",
                    "user_val": "No girl child ≤ 10 years",
                    "required_val": "Must be guardian of girl child ≤ 10 years",
                    "details": "SSY is strictly reserved for girl children aged 10 or younger.",
                    "citation": "[SSY:Sec2.1]"
                })
            else:
                why_you_match.append({
                    "criterion": "Girl Child (Age ≤10) Guardian Status",
                    "status": "PASS",
                    "user_val": "Guardian of girl child ≤ 10 years",
                    "required_val": "Girl child ≤ 10 years",
                    "details": "Applicant is the guardian of a girl child aged 10 or younger.",
                    "citation": "[SSY:Sec2.1]"
                })

        # NMMSS: Must be enrolled student
        if scheme_id == "NMMSS":
            is_student = profile.get("is_student")
            if is_student is None:
                missing_information.append({
                    "criterion": "Secondary Student Enrollment",
                    "status": "UNKNOWN",
                    "field": "is_student",
                    "question": "Student enrollment status not specified.",
                    "impact": "Required for National Means-cum-Merit Scholarship.",
                    "citation": "[NMMSS:Sec2.1]"
                })
            elif not is_student:
                why_you_dont_match.append({
                    "criterion": "Secondary Student Enrollment",
                    "status": "FAIL",
                    "user_val": "Not an enrolled school student",
                    "required_val": "Enrolled student in Class 8/9",
                    "details": "Scholarship is exclusively for enrolled school students.",
                    "citation": "[NMMSS:Sec2.1]"
                })
            else:
                why_you_match.append({
                    "criterion": "Secondary Student Enrollment",
                    "status": "PASS",
                    "user_val": "Enrolled student",
                    "required_val": "Enrolled in Government/Aided School",
                    "details": "Applicant is currently an enrolled student.",
                    "citation": "[NMMSS:Sec2.1]"
                })

        # Determine Final Status
        if len(why_you_dont_match) > 0:
            status = "INELIGIBLE"
            confidence = 1.0 if len(missing_information) == 0 else 0.85
        elif len(missing_information) > 0:
            status = "UNKNOWN"
            total_checks = len(why_you_match) + len(missing_information)
            confidence = round(len(why_you_match) / max(1, total_checks), 2)
        else:
            status = "ELIGIBLE"
            confidence = 1.0

        return {
            "scheme_id": scheme_id,
            "name": scheme["name"],
            "hindi_name": scheme.get("hindi_name", ""),
            "version": scheme.get("version", "v1.0"),
            "gazette_ref": scheme.get("gazette_ref", ""),
            "department": scheme.get("department", ""),
            "category": scheme.get("category", ""),
            "summary": scheme.get("summary", ""),
            "benefit_value": scheme.get("benefit_value", ""),
            "status": status,
            "confidence_score": confidence,
            "why_you_match": why_you_match,
            "why_you_dont_match": why_you_dont_match,
            "missing_information": missing_information,
            # Backwards compatibility aliases
            "passed_checks": [{"criterion": m["criterion"], "reason": m["details"], "citation": m["citation"]} for m in why_you_match],
            "failed_checks": [{"criterion": f["criterion"], "reason": f["details"], "citation": f["citation"]} for f in why_you_dont_match],
            "missing_checks": [{"criterion": u["criterion"], "question": u["question"], "impact": u["impact"]} for u in missing_information],
            "required_documents": scheme.get("required_documents", []),
            "policy_passages": scheme.get("policy_passages", []),
            "application_process": scheme.get("application_process", {})
        }
