from .project_relevance import project_relevance_score

def compute_skill_coverage(candidate_skills, required_skills, preferred_skills):
    candidate = set([s.lower() for s in candidate_skills])
    required = [s.lower() for s in required_skills]
    preferred = [s.lower() for s in preferred_skills]

    if len(required) == 0:
        required_score = 1
    else:
        found_required = sum(1 for s in required if s in candidate)
        required_score = found_required / len(required)

    if len(preferred) == 0:
        preferred_score = 1
    else:
        found_preferred = sum(1 for s in preferred if s in candidate)
        preferred_score = found_preferred / len(preferred)

    return required_score, preferred_score

def compute_experience_score(candidate_exp, ideal_exp):
    if ideal_exp is None or ideal_exp <= 0:
        return 1
    if candidate_exp < ideal_exp:
        diff = ideal_exp - candidate_exp
        if diff > 5:
            return 0
        return max(0, 1 - (diff * 0.15))
    if candidate_exp > ideal_exp:
        diff = candidate_exp - ideal_exp
        if diff > 10:
            return 0.5
        return max(0.6, 1 - (diff * 0.05))
    return 1

def compute_match_score(
    candidate_skills,
    required_skills,
    preferred_skills,
    experience_years=0,
    ideal_experience=None,
    projects=None,
    responsibilities=None,
    weights=None
):

    if weights is None:
        weights = {"required":0.55, "preferred":0.15, "experience":0.15, "projects":0.15}

    required_score, preferred_score = compute_skill_coverage(candidate_skills, required_skills, preferred_skills)
    experience_score = compute_experience_score(experience_years, ideal_experience)

    project_score = 1.0
    if projects and responsibilities:
        project_score = project_relevance_score(projects, responsibilities)

    total = sum(weights.values())
    norm = {k: v/total for k,v in weights.items()}

    final = (
        required_score * norm["required"]
        + preferred_score * norm["preferred"]
        + experience_score * norm["experience"]
        + project_score * norm["projects"]
    ) * 100

    return round(final, 2)
