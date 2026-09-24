from app.domain.Enigme import Enigme
from app.domain.GameElement import GameElement


class Salle(GameElement):
    def __init__(self, id: int, name: str, bio: str, enigme: Enigme, reward: str | None = None):
        super().__init__(id, name, bio)
        self.enigme = enigme
        # Objet ajouté à l'inventaire de l'équipe quand la salle est validée
        # (None pour la salle finale : la réussir fait gagner la partie).
        self.reward = reward
