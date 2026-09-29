"""Erreurs métier levées par les services.

Les services ne connaissent pas HTTP : ils lèvent ces exceptions, et main.py
les traduit en réponse JSON avec le bon code (404, 403, 409).
"""


class ServiceError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFound(ServiceError):
    """Ressource inexistante (session, salle, joueur)."""

    status_code = 404


class Forbidden(ServiceError):
    """Action interdite pour l'instant (salle pas encore débloquée)."""

    status_code = 403


class Conflict(ServiceError):
    """Action incompatible avec l'état actuel (partie pas lancée, terminée…)."""

    status_code = 409
