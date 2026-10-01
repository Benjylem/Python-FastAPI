"""Journalisation des routers : chaque route écrit ce qu'elle fait."""

import logging


def messages(caplog) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.name.startswith("app.routers")]


def test_session_creation_is_logged(client, caplog):
    with caplog.at_level(logging.INFO):
        client.post("/sessions/start", json={"team_name": "Hackers"})

    assert any("créée pour l'équipe 'Hackers'" in m for m in messages(caplog))


def test_player_search_is_logged(client, caplog):
    with caplog.at_level(logging.INFO):
        client.get("/players/1")

    assert "Recherche du joueur 1" in messages(caplog)


def test_submit_result_is_logged(client, session_id, caplog):
    with caplog.at_level(logging.INFO):
        client.post(f"/sessions/{session_id}/rooms/1/submit", json={"answer": "faux"})

    assert any("réponse salle 1, success=False" in m for m in messages(caplog))


def test_refused_action_is_not_logged_as_success(client, caplog):
    # Le service lève une erreur (404) : le router ne va pas jusqu'à son log de succès.
    with caplog.at_level(logging.INFO):
        client.delete("/players/999")

    assert not any("supprimé" in m for m in messages(caplog))


# --- Ressources inexistantes : WARNING (services) ---


def warnings(caplog) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]


def test_unknown_player_logs_a_warning(client, caplog):
    with caplog.at_level(logging.INFO):
        assert client.get("/players/999").status_code == 404

    assert "Joueur 999 introuvable" in warnings(caplog)


def test_unknown_room_logs_a_warning(client, caplog):
    with caplog.at_level(logging.INFO):
        assert client.get("/rooms/99").status_code == 404

    assert "Salle 99 introuvable" in warnings(caplog)


def test_unknown_session_logs_a_warning(client, caplog):
    with caplog.at_level(logging.INFO):
        assert client.get("/sessions/999/state").status_code == 404

    assert "Session 999 introuvable" in warnings(caplog)


def test_player_not_in_team_logs_a_warning(client, lobby_id, caplog):
    with caplog.at_level(logging.INFO):
        assert client.delete(f"/sessions/{lobby_id}/players/2").status_code == 404

    assert f"Joueur 2 absent de la session {lobby_id}" in warnings(caplog)


def test_business_rule_violation_is_not_a_warning(client, lobby_id, caplog):
    # 409 (règle métier) : pas une ressource inexistante, donc pas de WARNING.
    with caplog.at_level(logging.INFO):
        assert client.post(f"/sessions/{lobby_id}/launch").status_code == 409

    assert warnings(caplog) == []


# --- Exceptions inattendues : ERROR + 500 (main.py) ---


def test_unexpected_error_is_logged_and_returns_500(monkeypatch, caplog):
    from fastapi.testclient import TestClient

    from app.main import app
    from app.services import room_service

    def plantage():
        raise RuntimeError("bug simulé")

    monkeypatch.setattr(room_service, "list_salles", plantage)
    # raise_server_exceptions=False : sinon le TestClient relance l'exception
    # au lieu de renvoyer la réponse 500 produite par le handler.
    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.INFO):
        response = client.get("/rooms/")

    assert response.status_code == 500
    assert response.json() == {"detail": "Erreur interne"}
    erreurs = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(erreurs) == 1
    assert "Erreur inattendue sur GET /rooms/" in erreurs[0].getMessage()
    assert erreurs[0].exc_info is not None  # la trace complète est journalisée
