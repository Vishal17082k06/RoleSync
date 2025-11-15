from .match_score import compute_match_score
from .skill_gap import get_skill_gap

def shortlist(candidate, job_role):
    score = compute_match_score(
        candidate_skills=candidate["skills"],
        required_skills=job_role["required_skills"],
        preferred_skills=job_role.get("preferred_skills", [])
    )

    gap = get_skill_gap(
        candidate_skills=candidate["skills"],
        required_skills=job_role["required_skills"]
    )

    status = "shortlisted" if score >= 70 else "rejected"

    return {
        "match_score": score,
        "skill_gap": gap,
        "status": status
    }
