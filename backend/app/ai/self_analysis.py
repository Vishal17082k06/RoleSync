from .resume_parser import parse_resume
from .ats_scoring import compute_ats_score
from .match_score import compute_match_score
from .skill_gap import get_skill_gap
from .feedback import generate_feedback
from datetime import datetime

def run_self_analysis(file_path, target_role=None, jd_obj=None):
    parsed = parse_resume(file_path)
    resume_text = parsed.get("raw_text", "") if isinstance(parsed, dict) and parsed.get("raw_text") else ""
    candidate_skills = parsed.get("skills", [])
    experience = parsed.get("experience_years", 0)

    required = jd_obj.get("required_skills", []) if jd_obj else []
    preferred = jd_obj.get("preferred_skills", []) if jd_obj else []

    ats = compute_ats_score(resume_text or "", required)
    match = compute_match_score(candidate_skills, required, preferred)
    gap = get_skill_gap(candidate_skills, required)
    feedback = generate_feedback(parsed, jd_obj or {"required_skills":required, "preferred_skills":preferred})

    result = {
        "parsed": parsed,
        "ats_score": ats,
        "match_score": match,
        "skill_gap": gap,
        "feedback": feedback,
        "timestamp": datetime.utcnow().isoformat()
    }
    return result
