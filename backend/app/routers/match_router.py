from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List, Optional
import os
import json
import google.generativeai as genai

from ..auth.auth import require_role, get_current_user
from ..database.candidate import CandidateDB
from ..database.jobrole import JobRoleDB
from ..ai.match_score import compute_match_score
from ..ai.ats_scoring import compute_ats_score
from ..ai.semantic_fit import explain_semantic_fit
from ..ai.batch_processing import process_batch

router = APIRouter(prefix="/match", tags=["match"])
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


@router.post("/score")
def score_candidate_for_role(candidate_id: str = Form(...), job_role_id: str = Form(...), current_user = Depends(require_role("recruiter"))):
    """
    Compute match score, ATS score, semantic fit and store analysis.
    """
    candidate = CandidateDB.get(candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    job = JobRoleDB.get(job_role_id)
    if not job:
        raise HTTPException(404, "Job role not found")

    cand_skills = candidate.get("skills", [])
    cand_projects = candidate.get("projects", [])
    cand_exp = candidate.get("experience_years", 0)
    raw_text = candidate.get("parsed_text", "")

    required = job.get("required_skills", []) or job.get("parsed", {}).get("required_skills", [])
    preferred = job.get("preferred_skills", []) or job.get("parsed", {}).get("preferred_skills", [])
    responsibilities = job.get("responsibilities", []) or job.get("parsed", {}).get("responsibilities", [])
    ideal_exp = job.get("experience_min") or job.get("parsed", {}).get("ideal_experience")

    match = compute_match_score(
        candidate_skills=cand_skills,
        required_skills=required,
        preferred_skills=preferred,
        experience_years=cand_exp,
        ideal_experience=ideal_exp,
        projects=cand_projects,
        responsibilities=responsibilities
    )

    ats = compute_ats_score(raw_text or "", required)

    semantic = explain_semantic_fit(candidate, job)

    analysis = {
        "job_role_id": job_role_id,
        "match_score": match,
        "ats_score": ats,
        "skill_gaps": [s for s in required if s.lower() not in set([x.lower() for x in cand_skills])],
        "project_relevance": None,
        "semantic": semantic,
        "timestamp": __import__("datetime").datetime.utcnow()
    }

    CandidateDB.add_analysis(candidate_id, job_role_id, match, ats)
    JobRoleDB.add_candidate_analysis(job_role_id, candidate_id, match, ats)

    return {"ok": True, "analysis": analysis}


@router.post("/batch")
async def batch_match_for_role(files: List[UploadFile] = File(...), job_role_id: Optional[str] = Form(None), recruiter_id: Optional[str] = Form(None), current_user = Depends(require_role("recruiter"))):
    """
    Upload multiple resumes and rank them for a job role.
    Uses your batch_processing module.
    """
    tmp_paths = []
    for f in files:
        p = f"/tmp/{f.filename}"
        with open(p, "wb") as fh:
            fh.write(await f.read())
        tmp_paths.append(p)

    job_role = JobRoleDB.get(job_role_id) if job_role_id else None
    results = process_batch(tmp_paths, job_role=job_role, recruiter_id=recruiter_id or current_user["_id"])

    for p in tmp_paths:
        try:
            os.remove(p)
        except:
            pass

    return {"ok": True, "results": results}


@router.post("/shortlist")
def shortlist_candidate(candidate_id: str = Form(...), job_role_id: str = Form(...), action: str = Form(...), manual_feedback: Optional[str] = Form(None), current_user = Depends(require_role("recruiter"))):
    """
    action: "shortlist" or "reject"
    If reject and manual_feedback not provided, AI will generate a rejection reason draft which recruiter can edit later (or accept directly).
    """

    if action not in ("shortlist", "reject"):
        raise HTTPException(400, "action must be 'shortlist' or 'reject'")

    candidate = CandidateDB.get(candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    job = JobRoleDB.get(job_role_id)
    if not job:
        raise HTTPException(404, "Job role not found")
    CandidateDB.add_submission(candidate_id, job_role_id, current_user["_id"])

    if action == "shortlist":
        CandidateDB.add_analysis(candidate_id, job_role_id, analysis_dict := {"match_score": None})
        return {"ok": True, "message": "Candidate shortlisted."}

    final_feedback = manual_feedback
    if not final_feedback:
        prompt = f"""
You are a concise recruiter assistant. Produce a short factual rejection message for the candidate.

Job Role Title: {job.get('title')}
Required Skills: {job.get('required_skills', [])}
Preferred Skills: {job.get('preferred_skills', [])}

Candidate Skills: {candidate.get('skills', [])}
Experience Years: {candidate.get('experience_years')}
Projects: {candidate.get('projects', [])}

Provide 2 short bullet sentences: first sentence = main reason, second = actionable suggestion.
Return plain text.
"""
        model = genai.GenerativeModel("gemini-pro")
        resp = model.generate_content(prompt)
        draft = resp.text.strip()
        final_feedback = draft

    CandidateDB.add_feedback(candidate_id, job_role_id, current_user["_id"], final_feedback)

    return {"ok": True, "message": "Candidate rejected and feedback saved.", "feedback": final_feedback}


@router.get("/role_candidates/{job_role_id}")
def role_candidates(job_role_id: str, current_user = Depends(require_role("recruiter"))):
    ranked = JobRoleDB.ranked_candidates(job_role_id)
    return {"ok": True, "candidates": ranked}
