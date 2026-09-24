from fastapi import APIRouter, HTTPException

from app.data import players as players_data
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate

router = APIRouter(prefix="/players", tags=["players"])


def _get_player(player_id: int):
    player = players_data.players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/", response_model=list[PlayerRead])
def get_players():
    return list(players_data.players.values())


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int):
    return _get_player(player_id)


@router.post("/", response_model=PlayerRead)
def create_player(payload: PlayerCreate):
    return players_data.create_player(payload.name)


@router.put("/{player_id}", response_model=PlayerRead)
def update_player(player_id: int, payload: PlayerUpdate):
    player = _get_player(player_id)
    player.name = payload.name
    return player


@router.delete("/{player_id}", status_code=204)
def delete_player(player_id: int):
    # Le lien d'équipe est porté par le joueur : le supprimer le retire
    # automatiquement de son équipe.
    _get_player(player_id)
    del players_data.players[player_id]
