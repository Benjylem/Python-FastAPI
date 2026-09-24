from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.session import Inventaire, StatutPartie
from app.schemas.player import PlayerRead


class SessionCreate(BaseModel):
    """Payload pour créer une équipe : la session démarre en lobby."""

    team_name: str = Field(..., description="Nom de l'équipe")

    @field_validator("team_name")
    def team_name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom de l'équipe ne peut pas être vide")
        return v


class JoinTeam(BaseModel):
    """Payload pour qu'un joueur existant rejoigne une équipe."""

    player_id: int


class SessionState(BaseModel):
    """État renvoyé par GET /sessions/{id}/state (lu depuis l'objet domaine Session)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    team_name: str
    current_room: int
    status: StatutPartie
    started_at: datetime | None  # None tant que la partie est en lobby
    players: list[PlayerRead]
    inventaire: dict[str, bool]

    @field_validator("inventaire", mode="before")
    def inventaire_to_dict(cls, v):
        return v.items if isinstance(v, Inventaire) else v
