from pydantic import BaseModel, Field, field_validator

from app.domain.Enigme import ValeurCondition


class EnigmeChaineSubmission(BaseModel):
    """Salle 1, 2 et 4 : réponse sous forme de chaîne de caractères."""

    answer: str = Field(..., description="Réponse soumise par l'équipe")

    @field_validator("answer")
    def answer_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La réponse ne peut pas être vide")
        return v


class EnigmeConditionnelleSubmission(BaseModel):
    """Salle 3 : payload JSON de conditions (booléens, entiers, chaînes)."""

    conditions: dict[str, ValeurCondition] = Field(
        ..., description="État des conditions soumis par l'équipe"
    )

    @field_validator("conditions")
    def conditions_must_not_be_empty(cls, v: dict[str, ValeurCondition]) -> dict[str, ValeurCondition]:
        if not v:
            raise ValueError("Le payload de conditions ne peut pas être vide")
        return v
