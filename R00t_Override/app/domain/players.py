class Player:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        # Équipe (session) du joueur ; None tant qu'il n'a rejoint personne.
        # Seul endroit où le lien joueur <-> équipe est stocké (future clé étrangère en DB).
        self.session_id: int | None = None


# Joueurs en dur pour tester ; remplacé plus tard par les vraies données/DB.
# Les rewards ne sont pas portés par le joueur : ils vivent dans l'inventaire
# partagé de l'équipe (voir app/domain/session.py).
_PLAYERS = [
    Player(1, "Joe"),
    Player(2, "Jasmine"),
]

players: dict[int, Player] = {player.id: player for player in _PLAYERS}


def create_player(name: str) -> Player:
    new_id = max(players.keys(), default=0) + 1
    player = Player(new_id, name)
    players[new_id] = player
    return player
