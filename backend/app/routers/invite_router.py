from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..database.invite import InviteDB
from ..database.candidate import CandidateDB

router = APIRouter(prefix="/invite", tags=["invite"])

@router.get("/{token}")
def verify_invite(token: str):
    invite = InviteDB.get_by_token(token)
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite link")

    return {
        "ok": True,
        "email": invite["email"],
        "candidate_temp_id": str(invite["candidate_temp_id"]),
        "job_role_id": invite["job_role_id"],
        "message": "Valid invite. Prompt user to create an account."
    }


@router.post("/activate/{token}")
def activate_invite(token: str, user_id: str):
    """
    Call after candidate signs up.
    Auto-link their resume & clear invite.
    """
    invite = InviteDB.get_by_token(token)
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite")

    CandidateDB.link_resume_to_user(invite["candidate_temp_id"], user_id)

    InviteDB.mark_used(token)

    return {"ok": True, "message": "Invite activated and resume linked successfully"}
