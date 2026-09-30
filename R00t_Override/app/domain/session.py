from datetime import datetime, timedelta
from enum import StrEnum

from app.data import players as players_data
from app.data.indices import indices
from app.data.salles import salles
from app.domain.Inventaire import Inventaire
from app.domain.players import Player
from app.domain.Room import Salle

DERNIERE_SALLE = max(salles)
DUREE_PARTIE = timedelta(minutes=60)
PENALITE_INDICE = timedelta(minutes=2)  # temps retiré au chrono par indice d'Eve


class StatutPartie(StrEnum):
    LOBBY = "lobby"  # l'équipe se constitue, le chrono n'a pas démarré
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    GAME_OVER = "game_over"  # timer écoulé





class Session:
    """Une équipe et sa partie : joueurs, progression, inventaire et statut."""

    def __init__(self, id: int, team_name: str):
        self.id = id
        self.team_name = team_name
        self.current_room = 1
        self.status = StatutPartie.LOBBY
        self.started_at: datetime | None = None
        self.ended_at: datetime | None = None  # fige le chrono à la fin de la partie
        self.penalite = timedelta(0)  # cumul des pénalités d'indices
        self.indices_reveles: dict[int, int] = {}  # id de salle -> nombre d'indices révélés
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
        restant = DUREE_PARTIE - self.penalite - (fin - self.started_at)
        return max(0, int(restant.total_seconds()))

    @property
    def penalite_secondes(self) -> int:
        return int(self.penalite.total_seconds())

    def verifier_timer(self) -> None:
        """Passe la partie en game over si le chrono est écoulé. Appelé à chaque
        accès à la session : pas besoin de tâche de fond qui tourne en parallèle."""
        if self.status == StatutPartie.IN_PROGRESS and self.temps_restant == 0:
            self.status = StatutPartie.GAME_OVER
            self.ended_at = self.started_at + DUREE_PARTIE - self.penalite

    def indices_de(self, salle_id: int) -> list[str]:
        """Indices d'Eve déjà révélés pour cette salle (les relire est gratuit)."""
        return indices.get(salle_id, [])[: self.indices_reveles.get(salle_id, 0)]

    def demander_indice(self, salle_id: int) -> str | None:
        """Révèle l'indice suivant de la salle et applique la pénalité de temps ;
        None si Eve n'a plus rien à dire sur cette salle."""
        disponibles = indices.get(salle_id, [])
        deja_reveles = self.indices_reveles.get(salle_id, 0)
        if deja_reveles >= len(disponibles):
            return None
        self.indices_reveles[salle_id] = deja_reveles + 1
        self.penalite += PENALITE_INDICE
        self.verifier_timer()  # la pénalité peut faire tomber le chrono à 0
        return disponibles[deja_reveles]

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

