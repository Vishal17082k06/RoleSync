from .resume_parser import parse_resume
from .match_score import compute_match_score
from .skill_gap import get_skill_gap
from .ats_scoring import compute_ats_score
from ..database.candidate import CandidateDB
import os

def process_batch(file_paths, job_role=None, recruiter_id=None):
    results = []
    for f in file_paths:
        parsed = parse_resume(f)
        skills = parsed.get("skills", [])
        required = job_role.get("required_skills", []) if job_role else []
        preferred = job_role.get("preferred_skills", []) if job_role else []
        match_score = compute_match_score(skills, required, preferred)
        gap = get_skill_gap(skills, required)
        ats = compute_ats_score(parsed.get("raw_text",""), required)
        doc = {
            "parsed": parsed,
            "match_score": match_score,
            "skill_gap": gap,
            "ats_score": ats,
            "uploaded_by": recruiter_id
        }
        saved = CandidateDB.insert_candidate_doc(doc)
        results.append({"candidate_id": saved.get("_id"), "match_score": match_score})
    results_sorted = sorted(results, key=lambda x: x["match_score"], reverse=True)
    return results_sorted
