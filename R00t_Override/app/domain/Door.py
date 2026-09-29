from app.domain.GameElement import GameElement

class Door(GameElement):
    def __init__(self, id: int, name: str, bio: str, is_locked: bool, required_item_id: str | None, message_eve: str):
        super().__init__(id, name, bio)
        self.is_locked = is_locked
        self.required_item_id = required_item_id
        self.message_eve = message_eve

    def est_ouverte(self, inventaire) -> bool:
        # Pas decondition la porte est ferme par defaut
        if (self.required_item_id is None):
            return False
        return (inventaire.possede(self.required_item_id))
