from app.domain.players import Player

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
