from datetime import datetime
from enum import StrEnum

from app.domain import players as players_domain
from app.domain.players import Player
from app.domain.Room import Salle, salles

DERNIERE_SALLE = max(salles)


class StatutPartie(StrEnum):
    LOBBY = "lobby"  # l'équipe se constitue, le chrono n'a pas démarré
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    GAME_OVER = "game_over"  # timer écoulé (pas encore implémenté)


class Inventaire:
    """Inventaire partagé par toute l'équipe : un booléen par reward de salle."""

    def __init__(self, rewards: list[str]):
        self.items: dict[str, bool] = {reward: False for reward in rewards}

    def ajouter(self, reward: str) -> None:
        self.items[reward] = True

    def possede(self, reward: str) -> bool:
        return self.items.get(reward, False)


class Session:
    """Une équipe et sa partie : joueurs, progression, inventaire et statut."""

    def __init__(self, id: int, team_name: str):
        self.id = id
        self.team_name = team_name
        self.current_room = 1
        self.status = StatutPartie.LOBBY
        self.started_at: datetime | None = None
        self.inventaire = Inventaire([s.reward for s in salles.values() if s.reward])

    @property
    def players(self) -> list[Player]:
        # Le lien est porté par Player.session_id : on filtre au lieu de tenir une
        # seconde liste à synchroniser.
        return [p for p in players_domain.players.values() if p.session_id == self.id]

    @property
    def terminee(self) -> bool:
        return self.status in (StatutPartie.VICTORY, StatutPartie.GAME_OVER)

    def ajouter_joueur(self, player: Player) -> None:
        player.session_id = self.id

    def retirer_joueur(self, player: Player) -> None:
        player.session_id = None

    def lancer(self) -> None:
        """Sortie du lobby : la partie commence, le chrono démarre maintenant."""
        self.status = StatutPartie.IN_PROGRESS
        self.started_at = datetime.now()

    def soumettre(self, salle: Salle, answer) -> bool:
        """Valide la réponse de la salle courante ; en cas de succès, donne le
        reward à l'équipe puis ouvre la salle suivante (ou fait gagner la partie)."""
        success = salle.enigme.check_solution(answer)
        if success:
            if salle.reward:
                self.inventaire.ajouter(salle.reward)
            if salle.id == DERNIERE_SALLE:
                self.status = StatutPartie.VICTORY
            else:
                self.current_room = salle.id + 1
        return success


# Sessions en mémoire pour tester ; remplacé plus tard par une vraie table DB.
sessions: dict[int, Session] = {}


def create_session(team_name: str) -> Session:
    new_id = max(sessions.keys(), default=0) + 1
    session = Session(new_id, team_name)
    sessions[new_id] = session
    return session
