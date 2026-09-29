from fastapi import APIRouter

from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from app.services import player_service

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/", response_model=list[PlayerRead])
def get_players():
    return player_service.list_players()


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int):
    return player_service.get_player(player_id)


@router.post("/", response_model=PlayerRead)
def create_player(payload: PlayerCreate):
    player = player_service.create_player(payload.name)
    return player


@router.put("/{player_id}", response_model=PlayerRead)
def update_player(player_id: int, payload: PlayerUpdate):
    player = player_service.rename_player(player_id, payload.name)
    return player


@router.delete("/{player_id}", status_code=204)
def delete_player(player_id: int):
    player_service.delete_player(player_id)
