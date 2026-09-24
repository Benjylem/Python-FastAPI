from fastapi import APIRouter, HTTPException

from app.domain import players as players_domain
from app.schemas.player import PlayerCreate, PlayerRead

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/", response_model=list[PlayerRead])
def get_players():
    return list(players_domain.players.values())


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int):
    player = players_domain.players.get(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("/", response_model=PlayerRead)
def create_player(payload: PlayerCreate):
    return players_domain.create_player(payload.name)
