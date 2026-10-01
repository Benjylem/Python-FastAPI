"""Contraintes Field des schemas : les entrées hors limites renvoient une 422."""


def test_team_name_too_long_is_rejected(client):
    assert client.post("/sessions/start", json={"team_name": "x" * 51}).status_code == 422


def test_team_name_at_max_length_is_accepted(client):
    assert client.post("/sessions/start", json={"team_name": "x" * 50}).status_code == 200


def test_player_name_too_long_is_rejected(client):
    assert client.post("/players/", json={"name": "x" * 31}).status_code == 422


def test_player_rename_too_long_is_rejected(client):
    assert client.put("/players/1", json={"name": "x" * 31}).status_code == 422


def test_player_id_must_be_positive(client, lobby_id):
    for player_id in (0, -1):
        response = client.post(f"/sessions/{lobby_id}/players", json={"player_id": player_id})
        assert response.status_code == 422


def test_answer_too_long_is_rejected(client, session_id):
    response = client.post(f"/sessions/{session_id}/rooms/1/submit", json={"answer": "x" * 201})

    assert response.status_code == 422


def test_empty_answer_string_is_rejected(client, session_id):
    response = client.post(f"/sessions/{session_id}/rooms/1/submit", json={"answer": ""})

    assert response.status_code == 422


def test_too_many_conditions_are_rejected(client, session_id):
    trop = {f"cle_{i}": True for i in range(11)}

    response = client.post(f"/sessions/{session_id}/rooms/3/submit", json={"conditions": trop})

    assert response.status_code == 422
