"""Rule-based first-pass screening. Output is a *candidate* list that a human
reviewer must confirm at title/abstract and full-text stages."""
import re
from typing import Dict, Tuple

from . import config


def classify_design(pub_types: str) -> str:
    pt = pub_types.lower()
    if "meta-analysis" in pt:
        return "Meta-analysis"
    if "systematic review" in pt:
        return "Systematic review"
    if "randomized controlled trial" in pt or "clinical trial" in pt:
        return "RCT / clinical trial"
    if "observational" in pt or "cohort" in pt:
        return "Observational"
    if "review" in pt:
        return "Narrative review"
    return "Other"


def screen_record(rec: Dict) -> Tuple[str, str]:
    """Return (decision, reason). decision is 'include_candidate' or 'exclude'."""
    text = f"{rec.get('title', '')} {rec.get('abstract', '')}".lower()
    pub_types = {p.strip() for p in rec.get("pub_types", "").split(";") if p.strip()}

    if rec.get("language") and rec["language"].lower() not in {"eng", "en"}:
        return "exclude", "non-English"
    if pub_types & config.EXCLUDED_PUBTYPES:
        return "exclude", "excluded publication type"
    if not rec.get("abstract"):
        return "exclude", "no abstract available"
    if not any(w in text for w in config.INTERVENTION_WORDS):
        return "exclude", "no GLP-1/incretin term"
    if not any(w in text for w in config.OBESITY_WORDS):
        return "exclude", "no obesity/weight term"
    animal = re.search(r"\b(mice|mouse|rats?|murine|rodents?)\b", text)
    human = re.search(r"\b(patients|participants|adults|humans?|individuals)\b", text)
    if animal and not human:
        return "exclude", "animal study"
    paeds = re.search(r"\b(adolescents?|children|paediatric|pediatric)\b", rec.get("title", "").lower())
    if paeds and "adult" not in text:
        return "exclude", "paediatric population (out of scope)"
    return "include_candidate", "meets rule-based criteria"
