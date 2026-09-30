from app.data.salles import salles
from app.domain.Room import Salle
from app.services.exceptions import NotFound


def get_salle(salle_id: int) -> Salle:
    salle = salles.get(salle_id)
    if salle is None:
        raise NotFound("Salle introuvable")
    return salle


def list_salles() -> list[int]:
    return list(salles.keys())


def get_carte_salle(salle_id: int) -> dict:
    """Carte publique d'une salle : nom et bio, sans l'énoncé."""
    salle = get_salle(salle_id)
    return salle.to_dict()
