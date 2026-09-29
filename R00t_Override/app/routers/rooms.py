from fastapi import APIRouter

from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])

# « Carte » publique du jeu : nom et bio de chaque salle, sans l'énoncé.
# L'énoncé n'est lisible que via la session, une fois la salle débloquée
# (GET /sessions/{id}/rooms/{salle_id}/enigma).


@router.get("/")
def get_rooms():
    return room_service.list_salles()


@router.get("/{salle_id}")
def get_room(salle_id: int):
    return room_service.get_carte_salle(salle_id)
