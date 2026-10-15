"""
Root compatibility wrapper for Grounded Document Retrieval.
Indexes curated scheme documents from documents/*.txt and provides TF-IDF vector retrieval.
Conforms to project structure specification in Hackathon Master Prompt Section 15.
"""

from typing import List, Dict, Any, Optional
import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from engine.rule_engine import SchemeRegistry
from engine.retriever import PolicyRetriever


class DocumentRetriever:
    """Indexes text files in documents/ folder and provides grounded search."""

    def __init__(self, doc_dir: Optional[str] = None):
        if doc_dir is None:
            doc_dir = os.path.join(os.path.dirname(__file__), "documents")
        self.doc_dir = os.path.abspath(doc_dir)
        self.docs: List[Dict[str, Any]] = []
        self._load_and_index_documents()

    def _load_and_index_documents(self):
        txt_files = glob.glob(os.path.join(self.doc_dir, "*.txt"))
        corpus = []
        self.docs = []

        for fpath in txt_files:
            fname = os.path.basename(fpath)
            scheme_id = os.path.splitext(fname)[0]
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            # Split document into sections/paragraphs
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 30]
            for p_idx, p_text in enumerate(paragraphs):
                # Extract potential heading/section
                lines = p_text.split("\n")
                heading = lines[0].strip() if len(lines) > 1 else f"Clause {p_idx+1}"
                self.docs.append({
                    "scheme_id": scheme_id,
                    "file_name": fname,
                    "section": heading,
                    "text": p_text,
                    "citation": f"[{scheme_id}:{heading[:25]}]"
                })
                corpus.append(f"{scheme_id} {heading} {p_text}")

        if corpus:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        else:
            self.vectorizer = None
            self.tfidf_matrix = None

    def search_documents(self, query: str, top_k: int = 3, scheme_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches documents using TF-IDF and returns top matching passages."""
        if not query or not query.strip() or self.vectorizer is None:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        ranked = scores.argsort()[::-1]
        results = []

        for idx in ranked:
            score = float(scores[idx])
            doc = self.docs[idx]

            if scheme_filter and doc["scheme_id"] != scheme_filter:
                continue

            results.append({
                **doc,
                "relevance_score": round(score, 3)
            })

            if len(results) >= top_k:
                break

        return results


# Global singleton instance
_retriever = None


def get_retriever() -> DocumentRetriever:
    global _retriever
    if _retriever is None:
        _retriever = DocumentRetriever()
    return _retriever


def search_policy_documents(query: str, top_k: int = 3, scheme_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    return get_retriever().search_documents(query, top_k=top_k, scheme_filter=scheme_filter)
