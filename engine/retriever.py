"""
Grounded Document Retrieval Engine using TF-IDF & Cosine Semantic Similarity.
Indexes all official scheme policy clauses and retrieves verbatim passages with auditable citations.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from engine.rule_engine import SchemeRegistry


class PolicyRetriever:
    """Indexes and retrieves official policy passages with exact citation anchors."""

    def __init__(self, registry: SchemeRegistry):
        self.registry = registry
        self.passages: List[Dict[str, Any]] = []
        self._build_index()

    def _build_index(self):
        """Extracts all policy passages and builds TF-IDF matrix."""
        self.passages = []
        corpus = []

        for scheme in self.registry.get_all_schemes():
            scheme_id = scheme["scheme_id"]
            scheme_name = scheme["name"]
            dept = scheme.get("department", "")
            category = scheme.get("category", "")

            # Include scheme summary and description as high-level passage
            if scheme.get("summary"):
                self.passages.append({
                    "passage_id": f"{scheme_id}:Overview",
                    "scheme_id": scheme_id,
                    "scheme_name": scheme_name,
                    "clause_no": "Overview",
                    "title": f"Scheme Scope: {scheme_name}",
                    "text": f"{scheme['summary']} Target Category: {category}. Department: {dept}.",
                    "department": dept,
                    "category": category
                })
                corpus.append(f"{scheme_name} {scheme_id} {scheme['summary']} {dept} {category}")

            # Include detailed policy clauses
            for p in scheme.get("policy_passages", []):
                self.passages.append({
                    "passage_id": p["passage_id"],
                    "scheme_id": scheme_id,
                    "scheme_name": scheme_name,
                    "clause_no": p.get("clause_no", ""),
                    "title": p.get("title", ""),
                    "text": p["text"],
                    "department": dept,
                    "category": category
                })
                # Rich text for vectorization
                full_text = f"{scheme_name} {p.get('title', '')} {p['text']}"
                corpus.append(full_text)

        # Build TF-IDF vectorizer with unigram and bigram representation
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search_passages(
        self,
        query: str,
        top_k: int = 4,
        scheme_id_filter: Optional[str] = None,
        min_score: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant policy passages matching a user query or topic.
        Filters by scheme_id if specified.
        """
        if not query or not query.strip():
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        ranked_indices = np.argsort(scores)[::-1]
        results = []

        for idx in ranked_indices:
            score = float(scores[idx])
            passage = self.passages[idx]

            if scheme_id_filter and passage["scheme_id"] != scheme_id_filter:
                continue

            if score < min_score and len(results) >= 1:
                break

            results.append({
                **passage,
                "relevance_score": round(score, 3),
                "citation": f"[{passage['passage_id']}]"
            })

            if len(results) >= top_k:
                break

        return results

    def get_passages_for_scheme(self, scheme_id: str) -> List[Dict[str, Any]]:
        """Returns all policy passages registered for a specific scheme."""
        return [p for p in self.passages if p["scheme_id"] == scheme_id]

    def ground_reason(self, scheme_id: str, reason_text: str) -> Optional[Dict[str, Any]]:
        """Finds the single best grounded policy clause supporting an eligibility reason."""
        matches = self.search_passages(reason_text, top_k=1, scheme_id_filter=scheme_id, min_score=0.01)
        if matches:
            return matches[0]
        # Fallback to first scheme clause
        scheme_passages = self.get_passages_for_scheme(scheme_id)
        if scheme_passages:
            return scheme_passages[0]
        return None
