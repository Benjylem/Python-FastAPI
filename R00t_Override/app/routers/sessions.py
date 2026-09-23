from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.schemas.session import SessionCreate, SessionState

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Sessions en memoire pour tester ; remplace plus tard par une vraie table DB.
sessions: dict[int, dict] = {}


@router.post("/start", response_model=SessionState)
def start_session(payload: SessionCreate):
    new_id = max(sessions.keys(), default=0) + 1
    session = {
        "id": new_id,
        "team_name": payload.team_name,
        "current_room": 1,
        "status": "in_progress",
        "started_at": datetime.now(),
    }
    sessions[new_id] = session
    return session


@router.get("/{session_id}/state", response_model=SessionState)
def get_session_state(session_id: int):
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return session
