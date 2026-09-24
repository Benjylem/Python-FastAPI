class Player:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        # Équipe (session) du joueur ; None tant qu'il n'a rejoint personne.
        # Seul endroit où le lien joueur <-> équipe est stocké (future clé étrangère en DB).
        self.session_id: int | None = None
