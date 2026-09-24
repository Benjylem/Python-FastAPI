from fastapi import APIRouter, HTTPException

from app.data import players as players_data
from app.data import sessions as sessions_data
from app.data.salles import salles
from app.domain.players import Player
from app.domain.Room import Salle
from app.domain.session import Session, StatutPartie
from app.schemas.enigme import EnigmeChaineSubmission, EnigmeConditionnelleSubmission
from app.schemas.session import JoinTeam, SessionCreate, SessionState

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_session(session_id: int) -> Session:
    session = sessions_data.sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return session


def _get_player(player_id: int) -> Player:
    player = players_data.players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


def _get_salle(salle_id: int) -> Salle:
    salle = salles.get(salle_id)
    if salle is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return salle


def _verifier_lancee(session: Session) -> None:
    if session.status == StatutPartie.LOBBY:
        raise HTTPException(status_code=409, detail="La partie n'a pas encore été lancée")


def _verifier_debloquee(session: Session, salle_id: int) -> None:
    if salle_id > session.current_room:
        raise HTTPException(status_code=403, detail="Salle verrouillée")


def _soumettre(session_id: int, salle_id: int, answer) -> dict:
    session = _get_session(session_id)
    salle = _get_salle(salle_id)
    _verifier_lancee(session)
    if session.terminee:
        raise HTTPException(status_code=409, detail="La partie est terminée")
    _verifier_debloquee(session, salle_id)
    if salle_id < session.current_room:
        raise HTTPException(status_code=409, detail="Salle déjà résolue")

    success = session.soumettre(salle, answer)
    return {
        "success": success,
        "message": "Porte déverrouillée !" if success else "Mauvaise réponse, réessaie.",
        "reward": salle.reward if success else None,
        "current_room": session.current_room,
        "game_status": session.status,
    }


@router.post("/start", response_model=SessionState)
def start_session(payload: SessionCreate):
    """Crée l'équipe, en lobby : les joueurs la rejoignent avant le lancement."""
    return sessions_data.create_session(payload.team_name)


@router.get("/{session_id}/state", response_model=SessionState)
def get_session_state(session_id: int):
    return _get_session(session_id)


@router.post("/{session_id}/players", response_model=SessionState)
def join_team(session_id: int, payload: JoinTeam):
    """Un joueur existant rejoint l'équipe (possible aussi en cours de partie : retardataire)."""
    session = _get_session(session_id)
    player = _get_player(payload.player_id)
    if session.terminee:
        raise HTTPException(status_code=409, detail="La partie est terminée")
    if player.session_id == session_id:
        raise HTTPException(status_code=409, detail="Le joueur est déjà dans cette équipe")
    if player.session_id is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Le joueur est déjà dans l'équipe {player.session_id} : il doit la quitter d'abord",
        )

    session.ajouter_joueur(player)
    return session


@router.delete("/{session_id}/players/{player_id}", response_model=SessionState)
def leave_team(session_id: int, player_id: int):
    """Le joueur quitte l'équipe (autorisé dans tous les états, pour pouvoir en rejoindre une autre)."""
    session = _get_session(session_id)
    player = _get_player(player_id)
    if player.session_id != session_id:
        raise HTTPException(status_code=404, detail="Le joueur ne fait pas partie de cette équipe")

    session.retirer_joueur(player)
    return session


@router.post("/{session_id}/launch", response_model=SessionState)
def launch_session(session_id: int):
    """Sortie du lobby : la partie commence et le chrono démarre."""
    session = _get_session(session_id)
    if session.status != StatutPartie.LOBBY:
        raise HTTPException(status_code=409, detail="La partie a déjà été lancée")
    if not session.players:
        raise HTTPException(status_code=409, detail="Impossible de lancer une partie sans joueur")

    session.lancer()
    return session


@router.get("/{session_id}/rooms/{salle_id}/enigma")
def get_session_enigma(session_id: int, salle_id: int):
    """Énoncé d'une salle, visible seulement une fois la partie lancée et la salle débloquée."""
    session = _get_session(session_id)
    salle = _get_salle(salle_id)
    _verifier_lancee(session)
    _verifier_debloquee(session, salle_id)

    return {
        "session_id": session_id,
        "room": salle_id,
        "name": salle.name,
        "bio": salle.bio,
        "enigme": salle.enigme.prompt,
        "resolue": salle_id < session.current_room or session.status == StatutPartie.VICTORY,
    }


# Route dédiée déclarée avant la générique : la salle 3 attend un payload de
# conditions, pas une chaîne.
@router.post("/{session_id}/rooms/3/submit")
def submit_salle3(session_id: int, submission: EnigmeConditionnelleSubmission):
    return _soumettre(session_id, 3, submission.conditions)


@router.post("/{session_id}/rooms/{salle_id}/submit")
def submit_salle(session_id: int, salle_id: int, submission: EnigmeChaineSubmission):
    return _soumettre(session_id, salle_id, submission.answer)
