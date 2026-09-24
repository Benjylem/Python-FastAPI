from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/players", tags=["players"])


class Player(BaseModel):
    name: str = Field(min_length=3)
    reward1: bool
    reward2: bool
    reward3: bool


players = [
    {"id": 1, "name": "Joe", "reward1": False, "reward2": False, "reward3": False},
    {"id": 2, "name": "Jasmine", "reward1": False, "reward2": False, "reward3": False},
]


@router.get("/")
def get_players():
    return players


@router.get("/{player_id}")
def get_player(player_id: int):
    for player in players:
        if player["id"] == player_id:
            return player
    raise HTTPException(status_code=404, detail="Player not found")


@router.post("/")
def create_player(player: Player):
    new_id = max((p["id"] for p in players), default=0) + 1
    new_player = {"id": new_id, **player.model_dump()}
    players.append(new_player)
    return new_player


@router.put("/{player_id}")
def update_player(player_id: int, player: Player):
    for existing in players:
        if existing["id"] == player_id:
            existing.update(player.model_dump())
            return existing
    raise HTTPException(status_code=404, detail="Player not found")


@router.delete("/{player_id}", status_code=204)
def delete_player(player_id: int):
    for index, player in enumerate(players):
        if player["id"] == player_id:
            players.pop(index)
            return
    raise HTTPException(status_code=404, detail="Player not found")
