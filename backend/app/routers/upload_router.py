from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import os
from dotenv import load_dotenv

from ..auth.auth import require_role
from ..ai.resume_parser import parse_resume
from ..database.candidate import CandidateDB
from ..database.user import get_user_by_email
from ..database.invite import InviteDB

router = APIRouter(prefix="/upload", tags=["upload"])

load_dotenv()


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    job_role_id: str = Form(...),
    current_user=Depends(require_role("recruiter"))
):
    """
    Recruiter uploads a resume:
    1. Parse resume (PDF/DOCX)
    2. Save candidate temp entry
    3. Generate invite link ONLY if candidate has no account
    """

    temp_path = f"/tmp/{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    parsed = parse_resume(temp_path)

    try:
        os.remove(temp_path)
    except:
        pass

    if "error" in parsed:
        raise HTTPException(status_code=400, detail="Resume parsing failed")

    email = parsed.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Resume has no email. Cannot proceed.")

    candidate_doc = CandidateDB.insert_candidate_doc({
        "email": email,
        "name": parsed.get("name"),
        "skills": parsed.get("skills"),
        "projects": parsed.get("projects"),
        "parsed_text": parsed.get("parsed_text", ""),
        "experience_years": parsed.get("experience_years", 0),
        "analysis": [],
        "linked_user_id": None    
    })

    existing_user = get_user_by_email(email)

    if existing_user:
        CandidateDB.link_resume_to_user(candidate_doc["_id"], existing_user["_id"])

        return {
            "ok": True,
            "candidate_id": candidate_doc["_id"],
            "message": "Resume uploaded and linked to existing candidate account.",
            "invite_needed": False
        }

    invite = InviteDB.create_invite(
        candidate_temp_id=candidate_doc["_id"],
        email=email,
        job_role_id=job_role_id
    )

    invite_link = f"https://rolesync.com/invite/{invite['token']}"

    return {
        "ok": True,
        "candidate_id": candidate_doc["_id"],
        "invite_needed": True,
        "invite_link": invite_link,
        "message": "Candidate does not have an account. Share invite link with them."
    }
