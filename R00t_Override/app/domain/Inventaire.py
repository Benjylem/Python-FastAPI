class Inventaire:
    """Inventaire partagé par toute l'équipe : un booléen par reward de salle."""

    def __init__(self, rewards: list[str]):
        self.items: dict[str, bool] = {reward: False for reward in rewards}

    def ajouter(self, reward: str) -> None:
        self.items[reward] = True

    def possede(self, reward: str) -> bool:
        return self.items.get(reward, False)