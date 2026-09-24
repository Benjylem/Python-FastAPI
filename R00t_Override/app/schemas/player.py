from pydantic import BaseModel, ConfigDict, Field


class PlayerCreate(BaseModel):
    """Payload pour créer un joueur (sans équipe : il en rejoint une ensuite)."""

    name: str = Field(min_length=3)


class PlayerUpdate(BaseModel):
    """Payload pour modifier un joueur (PUT) : l'équipe se gère via /sessions."""

    name: str = Field(min_length=3)


class PlayerRead(BaseModel):
    """Joueur renvoyé par l'API (lu depuis l'objet domaine Player)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    session_id: int | None
