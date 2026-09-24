from fastapi import APIRouter, HTTPException

from app.data.salles import salles

router = APIRouter(prefix="/rooms", tags=["rooms"])

# « Carte » publique du jeu : nom et bio de chaque salle, sans l'énoncé.
# L'énoncé n'est lisible que via la session, une fois la salle débloquée
# (GET /sessions/{id}/rooms/{salle_id}/enigma).


@router.get("/")
def get_rooms():
    return list(salles.keys())


@router.get("/{salle_id}")
def get_room(salle_id: int):
    salle = salles.get(salle_id)
    if salle is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return {
        "id": salle.id,
        "name": salle.name,
        "bio": salle.bio,
    }
