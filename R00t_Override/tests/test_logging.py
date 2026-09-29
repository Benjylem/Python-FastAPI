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
