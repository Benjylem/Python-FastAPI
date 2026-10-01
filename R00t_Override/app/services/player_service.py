import logging

from app.data import players as players_data
from app.domain.players import Player
from app.services.exceptions import NotFound

logger = logging.getLogger(__name__)


def get_player(player_id: int) -> Player:
    player = players_data.players.get(player_id)
    if player is None:
        logger.warning("Joueur %s introuvable", player_id)
        raise NotFound("Player not found")
    return player


def list_players() -> list[Player]:
    return list(players_data.players.values())


def create_player(name: str) -> Player:
    return players_data.create_player(name)


def rename_player(player_id: int, name: str) -> Player:
    player = get_player(player_id)
    player.name = name
    return player


def delete_player(player_id: int) -> None:
    # Le lien d'équipe est porté par le joueur : le supprimer le retire
    # automatiquement de son équipe.
    get_player(player_id)
    del players_data.players[player_id]
