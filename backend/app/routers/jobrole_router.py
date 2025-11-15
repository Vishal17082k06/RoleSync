from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import Optional, List
import os
from ..auth.auth import require_role, get_current_user
from ..database.jobrole import JobRoleDB
from ..ai.jd_parser import parse_jd
from ..database.user import get_user_by_id

router = APIRouter(prefix="/jobrole", tags=["jobrole"])


@router.post("/create")
async def create_jobrole(
    title: str = Form(...),
    company: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    recruiter_id: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None),
    current_user = Depends(require_role("recruiter"))
):
    """
    Create a job role. Provide either jd_file (pdf/docx/txt) OR jd_text.
    The JD will be parsed and stored in `parsed` field.
    """
    text = ""
    if jd_file:
        tmp = f"/tmp/{jd_file.filename}"
        with open(tmp, "wb") as fh:
            fh.write(await jd_file.read())
        from ..ai.resume_parser import extract_text
        text = extract_text(tmp)
        try:
            os.remove(tmp)
        except:
            pass
    elif jd_text:
        text = jd_text
    else:
        raise HTTPException(status_code=400, detail="Provide jd_file or jd_text")

    parsed = parse_jd_with_text(text := text) if False else None  

    from ..ai.jd_parser import parse_jd_with_ai

    parsed = parse_jd_with_ai(text)

    doc = {
        "title": title,
        "company": company,
        "location": location,
        "recruiter_id": recruiter_id or current_user["_id"],
        "required_skills": parsed.get("required_skills", []),
        "preferred_skills": parsed.get("preferred_skills", []),
        "responsibilities": parsed.get("responsibilities", []),
        "tech_stack": parsed.get("tech_stack", []),
        "experience_min": parsed.get("experience_level") or parsed.get("ideal_experience"),
        "parsed": parsed
    }

    created = JobRoleDB.create(doc)
    return {"ok": True, "job_role": created}


@router.get("/get/{job_role_id}")
def get_jobrole(job_role_id: str, current_user = Depends(require_role("recruiter"))):
    job = JobRoleDB.get(job_role_id)
    if not job:
        raise HTTPException(404, "Job role not found")
    return {"ok": True, "job_role": job}


@router.put("/update/{job_role_id}")
def update_jobrole(job_role_id: str, updates: dict, current_user = Depends(require_role("recruiter"))):
    job = JobRoleDB.get(job_role_id)
    if not job:
        raise HTTPException(404, "Job role not found")
    updated = JobRoleDB.update(job_role_id, updates)
    return {"ok": True, "job_role": updated}


@router.get("/list")
def list_jobroles(current_user = Depends(require_role("recruiter"))):
    roles = JobRoleDB.find_by_recruiter(current_user["_id"])
    return {"ok": True, "roles": roles}

@router.post("/parse")
async def parse_jd_endpoint(jd_file: Optional[UploadFile] = File(None), jd_text: Optional[str] = Form(None), current_user = Depends(require_role("recruiter"))):
    if jd_file:
        tmp = f"/tmp/{jd_file.filename}"
        with open(tmp, "wb") as fh:
            fh.write(await jd_file.read())
        from ..ai.jd_parser import parse_jd
        parsed = parse_jd(tmp)
        try:
            os.remove(tmp)
        except:
            pass
        return {"ok": True, "parsed": parsed}
    elif jd_text:
        from ..ai.jd_parser import parse_jd_with_ai
        parsed = parse_jd_with_ai(jd_text)
        return {"ok": True, "parsed": parsed}
    else:
        raise HTTPException(400, "Provide jd_file or jd_text")
