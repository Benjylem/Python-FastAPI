from fastapi import APIRouter, HTTPException

from app.domain.Room import salles

router = APIRouter(prefix="/rooms", tags=["rooms"])

# Lecture seule : la soumission des réponses se fait via la session de l'équipe
# (POST /sessions/{id}/rooms/{salle_id}/submit), qui gère progression et inventaire.


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
        "enigme": salle.enigme.prompt,
    }
