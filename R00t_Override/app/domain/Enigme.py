from abc import ABC, abstractmethod


class Enigme(ABC):
    def __init__(self, id: int, prompt: str):
        self.id = id
        self.prompt = prompt

    @abstractmethod
    def check_solution(self, answer) -> bool: ...


class EnigmeChaine(Enigme):
    """Salle 1 (décodage) et Salle 2 (log/token) : comparaison de chaîne."""

    def __init__(self, id: int, prompt: str, reponse_attendue: str):
        super().__init__(id, prompt)
        self.reponse_attendue = reponse_attendue

    def check_solution(self, answer: str) -> bool:
        return answer.strip() == self.reponse_attendue


class EnigmeConditionnelle(Enigme):
    """Salle 3 : payload JSON de booléens/conditions à neutraliser."""

    def __init__(self, id: int, prompt: str, conditions_attendues: dict[str, bool]):
        super().__init__(id, prompt)
        self.conditions_attendues = conditions_attendues

    def check_solution(self, answer: dict[str, bool]) -> bool:
        return answer == self.conditions_attendues


class EnigmePatch(EnigmeChaine):
    """Salle 4 : comme EnigmeChaine, mais bascule l'état global du jeu en victoire."""

    def check_solution(self, answer: str) -> bool:
        succes = super().check_solution(answer)
        if succes:
            from app.domain.game_state import game_state

            game_state["status"] = "victory"
        return succes
