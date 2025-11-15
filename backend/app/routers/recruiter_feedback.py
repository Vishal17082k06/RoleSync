from fastapi import APIRouter, Depends, HTTPException
from bson.objectid import ObjectId
import datetime
import google.generativeai as genai
import os

from ..auth.auth import require_role, get_current_user
from ..database.candidate import CandidateDB
from ..database.jobrole import JobRoleDB  
from ..database.user import get_user_by_id

router = APIRouter(prefix="/recruiter", tags=["recruiter"])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@router.post("/generate-feedback")
def generate_feedback(candidate_id: str, job_role_id: str, current_user = Depends(require_role("recruiter"))):

    candidate = CandidateDB.get(candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    job_role = JobRoleDB.get(job_role_id)
    if not job_role:
        raise HTTPException(404, "Job Role not found")

    prompt = f"""
    Generate concise recruiter-style rejection feedback.

    Job Role:
    Required Skills: {job_role.get("required_skills", [])}
    Preferred Skills: {job_role.get("preferred_skills", [])}

    Candidate:
    Skills: {candidate.get("skills", [])}
    Experience: {candidate.get("experience_years")}
    Projects: {candidate.get("projects", [])}

    Provide:
    - Key missing skills
    - Why the candidate is not a good fit
    - Keep it short, factual, professional.
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return {"ai_feedback": response.text}

@router.post("/submit-feedback")
def submit_feedback(candidate_id: str, job_role_id: str, final_feedback: str,
                    current_user = Depends(require_role("recruiter"))):

    if len(final_feedback.strip()) == 0:
        raise HTTPException(400, "Feedback cannot be empty")

    CandidateDB.add_feedback(
        candidate_id=candidate_id,
        job_role_id=job_role_id,
        recruiter_id=current_user["_id"],
        feedback_text=final_feedback
    )

    return {"ok": True, "message": "Feedback saved successfully"}


