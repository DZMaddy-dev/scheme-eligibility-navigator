"""
Root compatibility wrapper for Deterministic Eligibility Engine.
Conforms to project structure specification in Hackathon Master Prompt Section 15.
"""

from engine.rule_engine import SchemeRegistry, RuleEngine

# Singleton registry and engine
_registry = None
_engine = None


def get_engine() -> RuleEngine:
    global _registry, _engine
    if _engine is None:
        _registry = SchemeRegistry()
        _engine = RuleEngine(_registry)
    return _engine


def evaluate_profile(profile: dict) -> list:
    """Evaluates citizen profile against all registered schemes."""
    return get_engine().evaluate_profile(profile)


def get_all_schemes() -> list:
    """Returns all registered schemes."""
    if _registry is None:
        get_engine()
    return _registry.get_all_schemes()
