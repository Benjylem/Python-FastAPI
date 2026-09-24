from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.data.salles import salles
from app.schemas.enigme import EnigmeChaineSubmission, EnigmeConditionnelleSubmission
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
    return get_session_or_404(session_id)


@router.get("/{session_id}/rooms/{salle_id}/enigma")
def get_session_enigma(session_id: int, salle_id: int):
    session = get_session_or_404(session_id)
    salle = get_salle_or_404(salle_id)

    if salle_id > session["current_room"]:
        raise HTTPException(status_code=403, detail="Salle verrouillée")
    resolue = salle_id < session["current_room"] or session["status"] == "victory"

    return {
        "session_id": session_id,
        "room": salle_id,
        "name": salle["name"],
        "bio": salle["bio"],
        "enigme": salle["enigme"].prompt,
        "resolue": resolue,
    }


# Route dédiée déclarée avant la générique : la salle 3 attend des conditions
# booléennes, pas une chaîne (même principe que dans rooms.py).
@router.post("/{session_id}/rooms/3/submit")
def submit_session_salle3(session_id: int, submission: EnigmeConditionnelleSubmission):
    return valider_soumission(session_id, 3, submission.conditions)


@router.post("/{session_id}/rooms/{salle_id}/submit")
def submit_session_salle(session_id: int, salle_id: int, submission: EnigmeChaineSubmission):
    return valider_soumission(session_id, salle_id, submission.answer)


def get_session_or_404(session_id: int) -> dict:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return session


def get_salle_or_404(salle_id: int) -> dict:
    salle = salles.get(salle_id)
    if salle is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return salle


def valider_soumission(session_id: int, salle_id: int, answer) -> dict:
    """Vérifie que la salle est bien la salle active de la session, valide la
    réponse avec l'énigme et fait avancer la session en cas de succès."""
    session = get_session_or_404(session_id)
    salle = get_salle_or_404(salle_id)

    if session["status"] != "in_progress":
        raise HTTPException(status_code=409, detail="La partie est terminée")
    if salle_id > session["current_room"]:
        raise HTTPException(status_code=403, detail="Salle verrouillée")
    if salle_id < session["current_room"]:
        raise HTTPException(status_code=409, detail="Salle déjà résolue")

    success = salle["enigme"].check_solution(answer)
    if success:
        if salle_id == max(salles):
            session["status"] = "victory"
        else:
            session["current_room"] += 1

    return {
        "success": success,
        "message": "Porte déverrouillée !" if success else "Mauvaise réponse, réessaie.",
        "current_room": session["current_room"],
        "status": session["status"],
    }
