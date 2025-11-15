from difflib import SequenceMatcher
import re

def _clean(s):
    return re.sub(r'\s+', ' ', (s or "").strip().lower())

def _similarity(a, b):
    return SequenceMatcher(None, _clean(a), _clean(b)).ratio()

def project_relevance_score(projects, responsibilities, threshold=0.35):
    """
    projects: list of strings (project descriptions)
    responsibilities: list of role responsibility strings
    Returns a score 0..1 representing how relevant the candidate's projects are to responsibilities.
    Algorithm:
      - For each responsibility, find best matching project by text similarity.
      - Score is average of best similarities (clamped).
    """
    if not responsibilities:
        return 1.0  

    if not projects:
        return 0.0

    scores = []
    for r in responsibilities:
        best = 0.0
        for p in projects:
            sim = _similarity(p, r)
            if sim > best:
                best = sim
        scores.append(best if best >= threshold else 0.0)
    avg = sum(scores) / len(scores)
    return round(avg, 3)
