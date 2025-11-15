from fastapi import APIRouter, Depends
from ..auth.auth import require_role, get_current_user
from ..database.candidate import CandidateDB

router = APIRouter(prefix="/candidate", tags=["candidate"])

@router.get("/feedback-history")
def get_feedback_history(current_user = Depends(require_role("candidate"))):

    candidate_id = current_user.get("linked_id")
    if not candidate_id:
        return {"feedback": []}

    candidate = CandidateDB.get(candidate_id)
    history = candidate.get("feedback_history", [])

    history_sorted = sorted(history, key=lambda h: h.get("timestamp"), reverse=True)

    return {"feedback": history_sorted}
