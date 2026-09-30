from app.domain.Door import Door
from app.domain.Enigme import Enigme
from app.domain.GameElement import GameElement


class Salle(GameElement):
    def __init__(self, id: int, name: str, bio: str, enigme: Enigme, reward: str | None = None, doors: list[Door] | None = None, message_victoire: str | None = None):
        super().__init__(id, name, bio)
        self.enigme = enigme
        # Objet ajouté à l'inventaire de l'équipe quand la salle est validée
        # (None pour la salle finale : la réussir fait gagner la partie).
        self.reward = reward
        self.message_victoire = message_victoire
        if doors is None:
            self.doors = []
        else:
            self.doors = doors