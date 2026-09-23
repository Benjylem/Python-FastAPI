from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SessionCreate(BaseModel):
    """Payload pour démarrer une session : le nom de l'équipe qui joue."""

    team_name: str = Field(..., description="Nom de l'équipe")

    @field_validator("team_name")
    def team_name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom de l'équipe ne peut pas être vide")
        return v


class SessionState(BaseModel):
    """État renvoyé par GET /sessions/{id}/state."""

    id: int
    team_name: str
    current_room: int
    status: str
    started_at: datetime
