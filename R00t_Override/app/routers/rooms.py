from fastapi import APIRouter, HTTPException

from app.domain.Enigme import EnigmeChaine, EnigmeConditionnelle, EnigmePatch
from app.domain.game_state import game_state
from app.schemas.enigme import EnigmeChaineSubmission, EnigmeConditionnelleSubmission

router = APIRouter(prefix="/rooms", tags=["rooms"])

# Salles en dur pour tester ; remplacé plus tard par les vraies données/DB.
# Chaque salle porte son propre objet Enigme : une seule source de vérité par id,
# au lieu de deux dicts (salles / enigmes) tenus en synchro à la main.
salles = {
    1: {
        "name": "Pare-Feu",
        "bio": "Obtenez la Clé de Validation Externe",
        "enigme": EnigmeChaine(1, "Décode la chaîne fournie", reponse_attendue="cle_externe_valide"),
    },
    2: {
        "name": "Proxy",
        "bio": "Décrochez les Privilèges Intermédiaires",
        "enigme": EnigmeChaine(2, "Trouve le token dans les logs", reponse_attendue="admin_token_1337"),
    },
    3: {
        "name": "Contre-Mesures",
        "bio": "Récupérez le Module de Déchiffrement du Cœur",
        "enigme": EnigmeConditionnelle(
            3,
            "Neutralise la boucle de rétroaction",
            conditions_attendues={"firewall_neutralise": True, "boucle_stoppee": True},
        ),
    },
    4: {
        "name": "Noyau Central",
        "bio": "Injectez le patch et validez le reboot",
        "enigme": EnigmePatch(4, "Injecte le patch final", reponse_attendue="reboot --force --patch=core"),
    },
}


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
