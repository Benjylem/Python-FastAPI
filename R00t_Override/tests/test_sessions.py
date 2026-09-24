"""Déroulé d'une partie : lobby, équipe, progression salle par salle, inventaire partagé, victoire."""

SALLE3_OK = {"bypass_firewall": True, "override_lock": "ACTIVE", "port_status": 80}

BONNES_REPONSES = {
    1: {"answer": "root_override"},
    2: {"answer": "ADMIN_TOKEN_X987F"},
    3: {"conditions": SALLE3_OK},
    4: {"answer": "system.reboot(true)"},
}


def submit(client, session_id, salle_id, payload):
    return client.post(f"/sessions/{session_id}/rooms/{salle_id}/submit", json=payload)


def test_start_session_creates_lobby_with_empty_inventory(client):
    response = client.post("/sessions/start", json={"team_name": "Hackers"})

    assert response.status_code == 200
    body = response.json()
    assert body["current_room"] == 1
    assert body["status"] == "lobby"
    assert body["started_at"] is None
    assert body["players"] == []
    assert body["inventaire"] == {
        "cle_validation_externe": False,
        "privileges_intermediaires": False,
        "module_dechiffrement": False,
    }


def test_start_session_rejects_empty_team_name(client):
    assert client.post("/sessions/start", json={"team_name": "  "}).status_code == 422


def test_start_session_rejects_missing_team_name(client):
    assert client.post("/sessions/start", json={}).status_code == 422


def test_start_session_assigns_incremental_ids(client):
    first = client.post("/sessions/start", json={"team_name": "Alpha"}).json()
    second = client.post("/sessions/start", json={"team_name": "Beta"}).json()

    assert second["id"] == first["id"] + 1


def test_get_session_state_matches_created_session(client):
    created = client.post("/sessions/start", json={"team_name": "Root Squad"}).json()

    assert client.get(f"/sessions/{created['id']}/state").json() == created


def test_unknown_session_returns_404(client):
    assert client.get("/sessions/999/state").status_code == 404
    assert submit(client, 999, 1, BONNES_REPONSES[1]).status_code == 404


def test_submit_unknown_room_returns_404(client, session_id):
    assert submit(client, session_id, 99, {"answer": "x"}).status_code == 404


def test_correct_answer_gives_reward_and_opens_next_room(client, session_id):
    response = submit(client, session_id, 1, BONNES_REPONSES[1])

    body = response.json()
    assert body["success"] is True
    assert body["reward"] == "cle_validation_externe"
    assert body["current_room"] == 2

    state = client.get(f"/sessions/{session_id}/state").json()
    assert state["inventaire"]["cle_validation_externe"] is True
    assert state["inventaire"]["privileges_intermediaires"] is False


def test_wrong_answer_keeps_team_in_same_room(client, session_id):
    response = submit(client, session_id, 1, {"answer": "mauvaise_reponse"})

    body = response.json()
    assert body["success"] is False
    assert body["reward"] is None
    assert body["current_room"] == 1


def test_cannot_skip_to_a_later_room(client, session_id):
    response = submit(client, session_id, 4, BONNES_REPONSES[4])

    assert response.status_code == 403
    assert client.get(f"/sessions/{session_id}/state").json()["status"] == "in_progress"


def test_cannot_replay_a_passed_room(client, session_id):
    submit(client, session_id, 1, BONNES_REPONSES[1])

    response = submit(client, session_id, 1, BONNES_REPONSES[1])

    assert response.status_code == 409
    assert response.json()["detail"] == "Salle déjà résolue"


def test_empty_answer_is_rejected(client, session_id):
    assert submit(client, session_id, 1, {"answer": "   "}).status_code == 422


def test_salle3_route_expects_conditions_schema(client, session_id):
    # route dédiée (EnigmeConditionnelleSubmission) : le format "answer" est rejeté
    assert submit(client, session_id, 3, {"answer": "x"}).status_code == 422


def test_salle3_with_empty_conditions_is_rejected(client, session_id):
    assert submit(client, session_id, 3, {"conditions": {}}).status_code == 422


def test_full_run_fills_inventory_and_wins(client, session_id):
    for salle_id in (1, 2, 3):
        assert submit(client, session_id, salle_id, BONNES_REPONSES[salle_id]).json()["success"] is True

    final = submit(client, session_id, 4, {"answer": "  System.Reboot( TRUE ) "}).json()
    assert final["success"] is True
    assert final["game_status"] == "victory"

    state = client.get(f"/sessions/{session_id}/state").json()
    assert state["status"] == "victory"
    assert all(state["inventaire"].values())


def test_no_submission_after_victory(client, session_id):
    for salle_id in (1, 2, 3, 4):
        submit(client, session_id, salle_id, BONNES_REPONSES[salle_id])

    assert submit(client, session_id, 4, BONNES_REPONSES[4]).status_code == 409


def test_sessions_are_independent(client, session_id):
    other_id = client.post("/sessions/start", json={"team_name": "Rivaux"}).json()["id"]

    submit(client, session_id, 1, BONNES_REPONSES[1])

    other = client.get(f"/sessions/{other_id}/state").json()
    assert other["current_room"] == 1
    assert other["inventaire"]["cle_validation_externe"] is False


# --- Lobby et lancement ---


def test_cannot_submit_while_in_lobby(client, lobby_id):
    assert submit(client, lobby_id, 1, BONNES_REPONSES[1]).status_code == 409


def test_cannot_launch_without_players(client, lobby_id):
    assert client.post(f"/sessions/{lobby_id}/launch").status_code == 409


def test_launch_starts_the_game(client, lobby_id):
    client.post(f"/sessions/{lobby_id}/players", json={"player_id": 1})

    response = client.post(f"/sessions/{lobby_id}/launch")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["started_at"] is not None


def test_cannot_launch_twice(client, session_id):
    assert client.post(f"/sessions/{session_id}/launch").status_code == 409


# --- Rejoindre / quitter une équipe ---


def test_join_team_links_player_to_session(client, lobby_id):
    response = client.post(f"/sessions/{lobby_id}/players", json={"player_id": 2})

    assert response.status_code == 200
    assert [p["name"] for p in response.json()["players"]] == ["Jasmine"]
    assert client.get("/players/2").json()["session_id"] == lobby_id


def test_join_unknown_player_returns_404(client, lobby_id):
    assert client.post(f"/sessions/{lobby_id}/players", json={"player_id": 999}).status_code == 404


def test_join_same_team_twice_is_rejected(client, lobby_id):
    client.post(f"/sessions/{lobby_id}/players", json={"player_id": 2})

    assert client.post(f"/sessions/{lobby_id}/players", json={"player_id": 2}).status_code == 409


def test_cannot_be_in_two_teams(client, lobby_id):
    other_id = client.post("/sessions/start", json={"team_name": "Rivaux"}).json()["id"]
    client.post(f"/sessions/{lobby_id}/players", json={"player_id": 2})

    assert client.post(f"/sessions/{other_id}/players", json={"player_id": 2}).status_code == 409


def test_late_player_joins_running_game_and_sees_progress(client, session_id):
    submit(client, session_id, 1, BONNES_REPONSES[1])
    late_id = client.post("/players/", json={"name": "Charlie"}).json()["id"]

    response = client.post(f"/sessions/{session_id}/players", json={"player_id": late_id})

    assert response.status_code == 200
    body = response.json()
    assert "Charlie" in [p["name"] for p in body["players"]]
    assert body["current_room"] == 2
    assert body["inventaire"]["cle_validation_externe"] is True


def test_cannot_join_finished_game(client, session_id):
    for salle_id in (1, 2, 3, 4):
        submit(client, session_id, salle_id, BONNES_REPONSES[salle_id])

    assert client.post(f"/sessions/{session_id}/players", json={"player_id": 2}).status_code == 409


def test_leave_then_join_another_team(client, lobby_id):
    other_id = client.post("/sessions/start", json={"team_name": "Rivaux"}).json()["id"]
    client.post(f"/sessions/{lobby_id}/players", json={"player_id": 2})

    leave = client.delete(f"/sessions/{lobby_id}/players/2")
    assert leave.status_code == 200
    assert leave.json()["players"] == []

    join = client.post(f"/sessions/{other_id}/players", json={"player_id": 2})
    assert join.status_code == 200
    assert client.get("/players/2").json()["session_id"] == other_id


def test_leave_team_player_is_not_in_returns_404(client, lobby_id):
    assert client.delete(f"/sessions/{lobby_id}/players/2").status_code == 404


def test_can_leave_finished_game(client, session_id):
    for salle_id in (1, 2, 3, 4):
        submit(client, session_id, salle_id, BONNES_REPONSES[salle_id])

    assert client.delete(f"/sessions/{session_id}/players/1").status_code == 200


# --- Énoncés (GET /sessions/{id}/rooms/{n}/enigma) ---


def enigma(client, session_id, salle_id):
    return client.get(f"/sessions/{session_id}/rooms/{salle_id}/enigma")


def test_enigma_of_current_room(client, session_id):
    response = enigma(client, session_id, 1)

    assert response.status_code == 200
    body = response.json()
    assert body["room"] == 1
    assert body["name"] == "Pare-Feu"
    assert "cm9vdF9vdmVycmlkZQ==" in body["enigme"]
    assert body["resolue"] is False
    assert "reponse_attendue" not in body


def test_enigma_of_room2_contains_logs(client, session_id):
    submit(client, session_id, 1, BONNES_REPONSES[1])

    assert "ADMIN_TOKEN_X987F" in enigma(client, session_id, 2).json()["enigme"]


def test_enigma_of_locked_room_returns_403(client, session_id):
    assert enigma(client, session_id, 2).status_code == 403


def test_enigma_hidden_while_in_lobby(client, lobby_id):
    assert enigma(client, lobby_id, 1).status_code == 409


def test_enigma_unknown_room_or_session_returns_404(client, session_id):
    assert enigma(client, session_id, 99).status_code == 404
    assert enigma(client, 999, 1).status_code == 404


def test_enigma_marked_resolved_after_success(client, session_id):
    submit(client, session_id, 1, BONNES_REPONSES[1])

    assert enigma(client, session_id, 1).json()["resolue"] is True
    assert enigma(client, session_id, 2).json()["resolue"] is False


def test_all_enigmas_resolved_after_victory(client, session_id):
    for salle_id in (1, 2, 3, 4):
        submit(client, session_id, salle_id, BONNES_REPONSES[salle_id])

    assert all(enigma(client, session_id, n).json()["resolue"] for n in (1, 2, 3, 4))


# --- Timer (60 min) ---
# Pour ne pas attendre 60 minutes, on recule toute la chronologie de la session
# (started_at et ended_at) : ça revient au même que laisser le temps passer.


def avancer_le_temps(session_id, **duree):
    from datetime import timedelta

    from app.data.sessions import sessions

    session = sessions[session_id]
    session.started_at -= timedelta(**duree)
    if session.ended_at is not None:
        session.ended_at -= timedelta(**duree)


def state(client, session_id):
    return client.get(f"/sessions/{session_id}/state").json()


def test_timer_is_none_while_in_lobby(client, lobby_id):
    assert state(client, lobby_id)["temps_restant"] is None


def test_timer_starts_at_60_minutes_on_launch(client, session_id):
    assert 3595 <= state(client, session_id)["temps_restant"] <= 3600


def test_timer_counts_down(client, session_id):
    avancer_le_temps(session_id, minutes=10)

    assert 2995 <= state(client, session_id)["temps_restant"] <= 3000


def test_timer_expired_sets_game_over(client, session_id):
    avancer_le_temps(session_id, minutes=61)

    body = state(client, session_id)
    assert body["status"] == "game_over"
    assert body["temps_restant"] == 0


def test_cannot_submit_after_game_over(client, session_id):
    avancer_le_temps(session_id, minutes=61)

    response = submit(client, session_id, 1, BONNES_REPONSES[1])

    assert response.status_code == 409
    assert "Temps écoulé" in response.json()["detail"]


def test_cannot_join_team_after_game_over(client, session_id):
    avancer_le_temps(session_id, minutes=61)

    assert client.post(f"/sessions/{session_id}/players", json={"player_id": 2}).status_code == 409


def test_submit_returns_remaining_time(client, session_id):
    response = submit(client, session_id, 1, BONNES_REPONSES[1])

    assert 3595 <= response.json()["temps_restant"] <= 3600


def test_timer_frozen_after_victory(client, session_id):
    avancer_le_temps(session_id, minutes=20)
    for salle_id in (1, 2, 3, 4):
        submit(client, session_id, salle_id, BONNES_REPONSES[salle_id])
    restant_a_la_victoire = state(client, session_id)["temps_restant"]

    # Même si le chrono continue de tourner, une partie gagnée ne passe jamais en game over.
    avancer_le_temps(session_id, minutes=60)

    body = state(client, session_id)
    assert body["status"] == "victory"
    assert body["temps_restant"] == restant_a_la_victoire
