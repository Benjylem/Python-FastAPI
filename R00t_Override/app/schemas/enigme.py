from pydantic import BaseModel, Field, field_validator

from app.domain.Enigme import ValeurCondition


class EnigmeChaineSubmission(BaseModel):
    """Salle 1, 2 et 4 : réponse sous forme de chaîne de caractères."""

    answer: str = Field(..., min_length=1, max_length=200, description="Réponse soumise par l'équipe")

    # min_length ne refuse pas "   " (3 caractères) : on vérifie aussi le contenu.
    @field_validator("answer")
    def answer_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La réponse ne peut pas être vide")
        return v


class EnigmeConditionnelleSubmission(BaseModel):
    """Salle 3 : payload JSON de conditions (booléens, entiers, chaînes)."""

    conditions: dict[str, ValeurCondition] = Field(
        ..., min_length=1, max_length=10, description="État des conditions soumis par l'équipe"
    )
