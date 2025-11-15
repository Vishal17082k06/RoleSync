from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional
from ..ai.self_analysis import run_self_analysis
from ..ai.batch_processing import process_batch
from ..ai.duplicate_detector import check_duplicate, file_hash
from ..database.candidate import CandidateDB
from ..database.job_description import JobRoleDB

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/self_analysis")
async def api_self_analysis(file: UploadFile = File(...), job_role_id: Optional[str] = Form(None)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    jd = None
    if job_role_id:
        jd = JobRoleDB.get(job_role_id)
    res = run_self_analysis(temp_path, jd_obj=jd)
    # store candidate
    doc = {"parsed": res.get("parsed"), "analysis":[{"match_score":res.get("match_score"), "skill_gap":res.get("skill_gap")}], "parsed_text": res["parsed"].get("raw_text","")}
    saved = CandidateDB.insert_candidate_doc(doc)
    return {"ok": True, "result": res, "candidate_id": saved.get("_id")}

@router.post("/batch_process")
async def api_batch_process(files: List[UploadFile] = File(...), job_role_id: Optional[str] = Form(None), recruiter_id: Optional[str] = Form(None)):
    # save files
    paths = []
    for file in files:
        p = f"/tmp/{file.filename}"
        with open(p,"wb") as fh:
            fh.write(await file.read())
        paths.append(p)
    job_role = JobRoleDB.get(job_role_id) if job_role_id else None
    results = process_batch(paths, job_role=job_role, recruiter_id=recruiter_id)
    return {"ok": True, "results": results}

@router.post("/detect_duplicate")
async def api_detect_duplicate(file: UploadFile = File(...)):
    p = f"/tmp/{file.filename}"
    with open(p,"wb") as fh:
        fh.write(await file.read())
    # db_check_fn wrapper for candidate DB
    def db_check_fn(hash_val, return_texts=False):
        from ..database.candidate import CandidateDB
        if hash_val:
            r = CandidateDB.find_by_hash(hash_val)
            return r
        if return_texts:
            return CandidateDB.find_texts()
        return None
    res = check_duplicate(p, db_check_fn)
    return res

@router.post("/learning_path")
async def api_learning_path(skill_gaps: List[str] = Form(...), candidate_skills: List[str] = Form(...), target_role: Optional[str] = Form(None)):
    from ..ai.learning_path import generate_learning_path
    res = generate_learning_path(skill_gaps, candidate_skills, target_role)
    return {"ok": True, "learning_path": res}

@router.post("/recruiter_query")
async def api_recruiter_query(query: str = Form(...), job_role_id: Optional[str] = Form(None)):
    from ..ai.recruiter_assistant import answer_recruiter_query
    context = {"job_role_id": job_role_id} if job_role_id else {}
    res = answer_recruiter_query(query, recruiter_context=context)
    return {"ok": True, "answer": res}
