from fastapi import APIRouter

from app.schemas.enigme import EnigmeChaineSubmission, EnigmeConditionnelleSubmission
from app.schemas.session import JoinTeam, SessionCreate, SessionState
from app.services import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionState)
def start_session(payload: SessionCreate):
    """Crée l'équipe, en lobby : les joueurs la rejoignent avant le lancement."""
    session = session_service.create_session(payload.team_name)
    return session


@router.get("/{session_id}/state", response_model=SessionState)
def get_session_state(session_id: int):
    return session_service.get_session(session_id)


@router.post("/{session_id}/players", response_model=SessionState)
def join_team(session_id: int, payload: JoinTeam):
    """Un joueur existant rejoint l'équipe (possible aussi en cours de partie : retardataire)."""
    session = session_service.join_team(session_id, payload.player_id)
    return session


@router.delete("/{session_id}/players/{player_id}", response_model=SessionState)
def leave_team(session_id: int, player_id: int):
    """Le joueur quitte l'équipe, pour pouvoir en rejoindre une autre."""
    session = session_service.leave_team(session_id, player_id)
    return session


@router.post("/{session_id}/launch", response_model=SessionState)
def launch_session(session_id: int):
    """Sortie du lobby : la partie commence et le chrono démarre."""
    session = session_service.launch(session_id)
    return session


@router.get("/{session_id}/rooms/{salle_id}/enigma")
def get_session_enigma(session_id: int, salle_id: int):
    """Énoncé d'une salle, visible une fois la partie lancée et la salle débloquée."""
    return session_service.get_enigma(session_id, salle_id)


# Route dédiée déclarée avant la générique : la salle 3 attend un payload de
# conditions, pas une chaîne.
@router.post("/{session_id}/rooms/3/submit")
def submit_salle3(session_id: int, submission: EnigmeConditionnelleSubmission):
    resultat = session_service.submit(session_id, 3, submission.conditions)
    return resultat


@router.post("/{session_id}/rooms/{salle_id}/submit")
def submit_salle(session_id: int, salle_id: int, submission: EnigmeChaineSubmission):
    resultat = session_service.submit(session_id, salle_id, submission.answer)
    return resultat


@router.post("/{session_id}/rooms/{salle_id}/hint")
def ask_hint(session_id: int, salle_id: int):
    """Eve révèle l'indice suivant de la salle active, contre 2 min de pénalité."""
    resultat = session_service.ask_hint(session_id, salle_id)
    return resultat


@router.get("/{session_id}/rooms/{salle_id}/hints")
def get_hints(session_id: int, salle_id: int):
    """Relire gratuitement les indices déjà obtenus pour une salle."""
    return session_service.get_hints(session_id, salle_id)
