def get_skill_gap(candidate_skills, required_skills):
    cand = set([s.lower() for s in candidate_skills])
    req = set([s.lower() for s in required_skills])
    gap = list(req - cand)
    return gap
