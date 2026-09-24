from datetime import datetime, timedelta
from enum import StrEnum

from app.data import players as players_data
from app.data.salles import salles
from app.domain.players import Player
from app.domain.Room import Salle

DERNIERE_SALLE = max(salles)
DUREE_PARTIE = timedelta(minutes=60)


class StatutPartie(StrEnum):
    LOBBY = "lobby"  # l'équipe se constitue, le chrono n'a pas démarré
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    GAME_OVER = "game_over"  # timer écoulé


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
        self.ended_at: datetime | None = None  # fige le chrono à la fin de la partie
        self.inventaire = Inventaire([s.reward for s in salles.values() if s.reward])

    @property
    def players(self) -> list[Player]:
        # Le lien est porté par Player.session_id : on filtre au lieu de tenir une
        # seconde liste à synchroniser.
        return [p for p in players_data.players.values() if p.session_id == self.id]

    @property
    def terminee(self) -> bool:
        return self.status in (StatutPartie.VICTORY, StatutPartie.GAME_OVER)

    @property
    def temps_restant(self) -> int | None:
        """Secondes restantes avant le game over ; None tant que la partie est en lobby."""
        if self.started_at is None:
            return None
        fin = self.ended_at or datetime.now()
        restant = DUREE_PARTIE - (fin - self.started_at)
        return max(0, int(restant.total_seconds()))

    def verifier_timer(self) -> None:
        """Passe la partie en game over si le chrono est écoulé. Appelé à chaque
        accès à la session : pas besoin de tâche de fond qui tourne en parallèle."""
        if self.status == StatutPartie.IN_PROGRESS and self.temps_restant == 0:
            self.status = StatutPartie.GAME_OVER
            self.ended_at = self.started_at + DUREE_PARTIE

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
                self.ended_at = datetime.now()
            else:
                self.current_room = salle.id + 1
        return success

