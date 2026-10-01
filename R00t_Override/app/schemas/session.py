from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.Inventaire import Inventaire
from app.domain.session import StatutPartie
from app.schemas.player import PlayerRead


class SessionCreate(BaseModel):
    """Payload pour créer une équipe : la session démarre en lobby."""

    team_name: str = Field(..., min_length=1, max_length=50, description="Nom de l'équipe")

    # min_length ne refuse pas "   " (3 caractères) : on vérifie aussi le contenu.
    @field_validator("team_name")
    def team_name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom de l'équipe ne peut pas être vide")
        return v


class JoinTeam(BaseModel):
    """Payload pour qu'un joueur existant rejoigne une équipe."""

    player_id: int = Field(..., gt=0, description="Id d'un joueur existant")


class SessionState(BaseModel):
    """État renvoyé par GET /sessions/{id}/state (lu depuis l'objet domaine Session)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    team_name: str
    current_room: int
    status: StatutPartie
    started_at: datetime | None  # None tant que la partie est en lobby
    temps_restant: int | None  # secondes avant le game over, None en lobby
    penalite_secondes: int  # temps perdu à cause des indices d'Eve
    players: list[PlayerRead]
    inventaire: dict[str, bool]

    @field_validator("inventaire", mode="before")
    def inventaire_to_dict(cls, v):
        return v.items if isinstance(v, Inventaire) else v
