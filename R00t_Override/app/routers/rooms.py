from fastapi import APIRouter, HTTPException

from app.data.salles import salles
from app.domain.game_state import game_state
from app.schemas.enigme import EnigmeChaineSubmission, EnigmeConditionnelleSubmission

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/")
def get_rooms():
    return list(salles.keys())


@router.get("/{salle_id}")
def get_room(salle_id: int):
    salle = salles.get(salle_id)
    if salle is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return {
        "id": salle_id,
        "name": salle["name"],
        "bio": salle["bio"],
        "enigme": salle["enigme"].prompt,
    }


@router.post("/3/submit")
def submit_salle3(submission: EnigmeConditionnelleSubmission):
    enigme = salles[3]["enigme"]
    success = enigme.check_solution(submission.conditions)
    return {
        "success": success,
        "message": "Boucle neutralisée !" if success else "La contre-mesure est toujours active.",
    }


@router.post("/{salle_id}/submit")
def submit_salle(salle_id: int, submission: EnigmeChaineSubmission):
    salle = salles.get(salle_id)
    if salle is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")

    success = salle["enigme"].check_solution(submission.answer)
    return {
        "success": success,
        "message": "Porte déverrouillée !" if success else "Mauvaise réponse, réessaie.",
        "game_status": game_state["status"],
    }


@router.get("/status/game")
def get_game_status():
    return game_state
