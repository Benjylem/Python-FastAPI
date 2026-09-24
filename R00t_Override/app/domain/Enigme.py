from abc import ABC, abstractmethod

# Types acceptés dans le payload de la salle 3 (JSON : true/false, nombres, chaînes).
ValeurCondition = bool | int | str


class Enigme(ABC):
    def __init__(self, id: int, prompt: str):
        self.id = id
        self.prompt = prompt

    @abstractmethod
    def check_solution(self, answer) -> bool: ...


class EnigmeChaine(Enigme):
    """Salle 1 (décodage) et Salle 2 (log/token) : comparaison de chaîne."""

    def __init__(self, id: int, prompt: str, reponse_attendue: str, ignorer_casse: bool = False):
        super().__init__(id, prompt)
        self.reponse_attendue = reponse_attendue
        self.ignorer_casse = ignorer_casse

    def _normaliser(self, texte: str) -> str:
        texte = texte.strip()
        return texte.lower() if self.ignorer_casse else texte

    def check_solution(self, answer: str) -> bool:
        return self._normaliser(answer) == self._normaliser(self.reponse_attendue)


class EnigmeConditionnelle(Enigme):
    """Salle 3 : payload JSON de conditions (booléens, entiers, chaînes) à reproduire."""

    def __init__(self, id: int, prompt: str, conditions_attendues: dict[str, ValeurCondition]):
        super().__init__(id, prompt)
        self.conditions_attendues = conditions_attendues

    def check_solution(self, answer: dict[str, ValeurCondition]) -> bool:
        if answer.keys() != self.conditions_attendues.keys():
            return False
        # On compare aussi le type : en Python 1 == True, donc sans ce test
        # {"bypass_firewall": 1} serait accepté à la place de true.
        return all(
            type(answer[cle]) is type(attendu) and answer[cle] == attendu
            for cle, attendu in self.conditions_attendues.items()
        )


class EnigmePatch(EnigmeChaine):
    """Salle 4 : commande de patch tolérante (casse + espaces ignorés).
    La victoire est déclenchée par la Session quand la dernière salle est validée."""

    def __init__(self, id: int, prompt: str, reponse_attendue: str):
        super().__init__(id, prompt, reponse_attendue, ignorer_casse=True)

    def _normaliser(self, texte: str) -> str:
        # "  System.Reboot( TRUE ) " -> "system.reboot(true)"
        return "".join(super()._normaliser(texte).split())
