"""Règles d'une partie : lobby, équipe, lancement, salles, réponses et indices.

Les routers appellent ces fonctions ; la logique « pure » (chrono, inventaire,
vérification d'une réponse) reste dans les classes du domaine.
"""

from app.data import sessions as sessions_data
from app.data.indices import indices
from app.domain.session import PENALITE_INDICE, Session, StatutPartie
from app.services import player_service, room_service
from app.services.exceptions import Conflict, Forbidden, NotFound


# --- Accès et vérifications ---


def get_session(session_id: int) -> Session:
    session = sessions_data.sessions.get(session_id)
    if session is None:
        raise NotFound("Session introuvable")
    session.verifier_timer()
    return session


def _verifier_lancee(session: Session) -> None:
    if session.status == StatutPartie.LOBBY:
        raise Conflict("La partie n'a pas encore été lancée")


def _verifier_debloquee(session: Session, salle_id: int) -> None:
    if salle_id > session.current_room:
        raise Forbidden("Salle verrouillée")


def _verifier_salle_active(session: Session, salle_id: int) -> None:
    """La partie est en cours et salle_id est la salle sur laquelle l'équipe joue."""
    _verifier_lancee(session)
    if session.status == StatutPartie.GAME_OVER:
        raise Conflict("Temps écoulé : la partie est perdue")
    if session.terminee:
        raise Conflict("La partie est terminée")
    _verifier_debloquee(session, salle_id)
    if salle_id < session.current_room:
        raise Conflict("Salle déjà résolue")


# --- Lobby et équipe ---


def create_session(team_name: str) -> Session:
    return sessions_data.create_session(team_name)


def join_team(session_id: int, player_id: int) -> Session:
    """Un joueur existant rejoint l'équipe (possible aussi en cours de partie : retardataire)."""
    session = get_session(session_id)
    player = player_service.get_player(player_id)
    if session.terminee:
        raise Conflict("La partie est terminée")
    if player.session_id == session_id:
        raise Conflict("Le joueur est déjà dans cette équipe")
    if player.session_id is not None:
        raise Conflict(f"Le joueur est déjà dans l'équipe {player.session_id} : il doit la quitter d'abord")

    session.ajouter_joueur(player)
    return session


def leave_team(session_id: int, player_id: int) -> Session:
    """Le joueur quitte l'équipe (autorisé dans tous les états, pour pouvoir en rejoindre une autre)."""
    session = get_session(session_id)
    player = player_service.get_player(player_id)
    if player.session_id != session_id:
        raise NotFound("Le joueur ne fait pas partie de cette équipe")

    session.retirer_joueur(player)
    return session


def launch(session_id: int) -> Session:
    """Sortie du lobby : la partie commence et le chrono démarre."""
    session = get_session(session_id)
    if session.status != StatutPartie.LOBBY:
        raise Conflict("La partie a déjà été lancée")
    if not session.players:
        raise Conflict("Impossible de lancer une partie sans joueur")

    session.lancer()
    return session


# --- Partie ---


def get_enigma(session_id: int, salle_id: int) -> dict:
    """Énoncé d'une salle, visible seulement une fois la partie lancée et la salle débloquée."""
    session = get_session(session_id)
    salle = room_service.get_salle(salle_id)
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


def submit(session_id: int, salle_id: int, answer) -> dict:
    """Valide la réponse de la salle active ; en cas de succès : reward dans
    l'inventaire, puis salle suivante (ou victoire)."""
    session = get_session(session_id)
    salle = room_service.get_salle(salle_id)
    _verifier_salle_active(session, salle_id)

    success = session.soumettre(salle, answer)

    return {
        "success": success,
        "message": "Porte déverrouillée !" if success else "Mauvaise réponse, réessaie.",
        "reward": salle.reward if success else None,
        "current_room": session.current_room,
        "game_status": session.status,
        "temps_restant": session.temps_restant,
    }


def ask_hint(session_id: int, salle_id: int) -> dict:
    """Eve révèle l'indice suivant de la salle active, contre une pénalité de temps."""
    session = get_session(session_id)
    room_service.get_salle(salle_id)
    _verifier_salle_active(session, salle_id)

    indice = session.demander_indice(salle_id)
    if indice is None:
        raise Conflict("Eve n'a plus d'indice pour cette salle")

    return {
        "room": salle_id,
        "eve": indice,
        "numero": len(session.indices_de(salle_id)),
        "total": len(indices.get(salle_id, [])),
        "penalite_secondes": int(PENALITE_INDICE.total_seconds()),
        "temps_restant": session.temps_restant,
        "game_status": session.status,
    }


def get_hints(session_id: int, salle_id: int) -> dict:
    """Relire les indices déjà obtenus pour une salle débloquée (gratuit)."""
    session = get_session(session_id)
    room_service.get_salle(salle_id)
    _verifier_lancee(session)
    _verifier_debloquee(session, salle_id)

    reveles = session.indices_de(salle_id)
    return {
        "room": salle_id,
        "indices": reveles,
        "restants": len(indices.get(salle_id, [])) - len(reveles),
    }
