from fastapi import APIRouter, HTTPException

from app.domain.Enigme import EnigmeChaine, EnigmeConditionnelle, EnigmePatch
from app.domain.game_state import game_state
from app.schemas.enigme import EnigmeChaineSubmission, EnigmeConditionnelleSubmission

router = APIRouter(prefix="/rooms", tags=["rooms"])

salles = {
    1: {"name": "Pare-Feu", "bio": "Obtenez la Clé de Validation Externe"},
    2: {"name": "Proxy", "bio": "Décrochez les Privilèges Intermédiaires"},
    3: {"name": "Contre-Mesures", "bio": "Récupérez le Module de Déchiffrement du Cœur"},
    4: {"name": "Noyau Central", "bio": "Injectez le patch et validez le reboot"},
}

# Enigmes en dur pour tester ; remplacé plus tard par les vraies données/DB
enigmes = {
    1: EnigmeChaine(1, "Décode la chaîne fournie", reponse_attendue="cle_externe_valide"),
    2: EnigmeChaine(2, "Trouve le token dans les logs", reponse_attendue="admin_token_1337"),
    3: EnigmeConditionnelle(3, "Neutralise la boucle de rétroaction", conditions_attendues={"firewall_neutralise": True, "boucle_stoppee": True}),
    4: EnigmePatch(4, "Injecte le patch final", reponse_attendue="reboot --force --patch=core"),
}


@router.get("/")
def get_rooms():
    return list(salles.keys())


@router.get("/{salle_id}")
def get_room(salle_id: int):
    salle = salles.get(salle_id)
    if salle is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return {"id": salle_id, **salle}


@router.post("/3/submit")
def submit_salle3(submission: EnigmeConditionnelleSubmission):
    enigme = enigmes[3]
    success = enigme.check_solution(submission.conditions)
    return {
        "success": success,
        "message": "Boucle neutralisée !" if success else "La contre-mesure est toujours active.",
    }


@router.post("/{salle_id}/submit")
def submit_salle(salle_id: int, submission: EnigmeChaineSubmission):
    if salle_id == 3:
        raise HTTPException(status_code=400, detail="Utilise POST /rooms/3/submit pour cette salle")

    enigme = enigmes.get(salle_id)
    if enigme is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")

    success = enigme.check_solution(submission.answer)
    return {
        "success": success,
        "message": "Porte déverrouillée !" if success else "Mauvaise réponse, réessaie.",
        "game_status": game_state["status"],
    }


@router.get("/status/game")
def get_game_status():
    return game_state
