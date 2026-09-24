def test_start_session_returns_initial_state(client):
    response = client.post("/sessions/start", json={"team_name": "Root Squad"})

    assert response.status_code == 200
    body = response.json()
    assert body["team_name"] == "Root Squad"
    assert body["current_room"] == 1
    assert body["status"] == "in_progress"
    assert isinstance(body["id"], int)
    assert "started_at" in body


def test_start_session_assigns_incremental_ids(client):
    first = client.post("/sessions/start", json={"team_name": "Alpha"}).json()
    second = client.post("/sessions/start", json={"team_name": "Beta"}).json()

    assert second["id"] == first["id"] + 1


def test_start_session_rejects_blank_team_name(client):
    response = client.post("/sessions/start", json={"team_name": "   "})

    assert response.status_code == 422


def test_start_session_rejects_missing_team_name(client):
    response = client.post("/sessions/start", json={})

    assert response.status_code == 422


def test_get_session_state(client):
    created = client.post("/sessions/start", json={"team_name": "Root Squad"}).json()

    response = client.get(f"/sessions/{created['id']}/state")

    assert response.status_code == 200
    assert response.json() == created


def test_get_unknown_session_returns_404(client):
    response = client.get("/sessions/999/state")

    assert response.status_code == 404


BONNES_REPONSES = {
    1: {"answer": "cle_externe_valide"},
    2: {"answer": "admin_token_1337"},
    3: {"conditions": {"firewall_neutralise": True, "boucle_stoppee": True}},
    4: {"answer": "reboot --force --patch=core"},
}


def start(client) -> int:
    return client.post("/sessions/start", json={"team_name": "Root Squad"}).json()["id"]


def test_get_enigma_of_current_room(client):
    session_id = start(client)

    response = client.get(f"/sessions/{session_id}/rooms/1/enigma")

    assert response.status_code == 200
    body = response.json()
    assert body["room"] == 1
    assert body["name"] == "Pare-Feu"
    assert body["resolue"] is False
    assert "reponse_attendue" not in body


def test_get_enigma_of_locked_room_returns_403(client):
    session_id = start(client)

    response = client.get(f"/sessions/{session_id}/rooms/2/enigma")

    assert response.status_code == 403


def test_get_enigma_unknown_room_or_session_returns_404(client):
    session_id = start(client)

    assert client.get(f"/sessions/{session_id}/rooms/99/enigma").status_code == 404
    assert client.get("/sessions/999/rooms/1/enigma").status_code == 404


def test_submit_correct_answer_advances_to_next_room(client):
    session_id = start(client)

    response = client.post(f"/sessions/{session_id}/rooms/1/submit", json=BONNES_REPONSES[1])

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["current_room"] == 2
    assert client.get(f"/sessions/{session_id}/state").json()["current_room"] == 2
    assert client.get(f"/sessions/{session_id}/rooms/1/enigma").json()["resolue"] is True


def test_submit_wrong_answer_stays_in_room(client):
    session_id = start(client)

    response = client.post(f"/sessions/{session_id}/rooms/1/submit", json={"answer": "faux"})

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["current_room"] == 1


def test_submit_locked_room_returns_403(client):
    session_id = start(client)

    response = client.post(f"/sessions/{session_id}/rooms/2/submit", json=BONNES_REPONSES[2])

    assert response.status_code == 403


def test_submit_already_solved_room_returns_409(client):
    session_id = start(client)
    client.post(f"/sessions/{session_id}/rooms/1/submit", json=BONNES_REPONSES[1])

    response = client.post(f"/sessions/{session_id}/rooms/1/submit", json=BONNES_REPONSES[1])

    assert response.status_code == 409


def test_submit_salle3_requires_conditions_schema(client):
    session_id = start(client)
    for salle in (1, 2):
        client.post(f"/sessions/{session_id}/rooms/{salle}/submit", json=BONNES_REPONSES[salle])

    response = client.post(f"/sessions/{session_id}/rooms/3/submit", json={"answer": "x"})

    assert response.status_code == 422


def test_full_run_ends_in_victory(client):
    session_id = start(client)

    for salle in (1, 2, 3, 4):
        response = client.post(f"/sessions/{session_id}/rooms/{salle}/submit", json=BONNES_REPONSES[salle])
        assert response.json()["success"] is True

    state = client.get(f"/sessions/{session_id}/state").json()
    assert state["status"] == "victory"
    assert state["current_room"] == 4


def test_submit_after_victory_returns_409(client):
    session_id = start(client)
    for salle in (1, 2, 3, 4):
        client.post(f"/sessions/{session_id}/rooms/{salle}/submit", json=BONNES_REPONSES[salle])

    response = client.post(f"/sessions/{session_id}/rooms/4/submit", json=BONNES_REPONSES[4])

    assert response.status_code == 409


def test_sessions_progress_independently(client):
    alpha = start(client)
    beta = start(client)

    client.post(f"/sessions/{alpha}/rooms/1/submit", json=BONNES_REPONSES[1])

    assert client.get(f"/sessions/{alpha}/state").json()["current_room"] == 2
    assert client.get(f"/sessions/{beta}/state").json()["current_room"] == 1
