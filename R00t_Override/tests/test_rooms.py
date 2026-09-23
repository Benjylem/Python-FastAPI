def test_get_rooms_returns_all_ids(client):
    response = client.get("/rooms/")

    assert response.status_code == 200
    assert response.json() == [1, 2, 3, 4]


def test_get_room_includes_enigme_prompt(client):
    response = client.get("/rooms/1")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Pare-Feu"
    assert "enigme" in body
    assert "reponse_attendue" not in body


def test_get_unknown_room_returns_404(client):
    response = client.get("/rooms/99")

    assert response.status_code == 404


def test_submit_salle1_correct_answer_unlocks_door(client):
    response = client.post("/rooms/1/submit", json={"answer": "cle_externe_valide"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["game_status"] == "in_progress"


def test_submit_salle1_wrong_answer_fails(client):
    response = client.post("/rooms/1/submit", json={"answer": "mauvaise_reponse"})

    assert response.status_code == 200
    assert response.json()["success"] is False


def test_submit_empty_answer_is_rejected(client):
    response = client.post("/rooms/1/submit", json={"answer": "   "})

    assert response.status_code == 422


def test_submit_unknown_room_returns_404(client):
    response = client.post("/rooms/99/submit", json={"answer": "x"})

    assert response.status_code == 404


def test_submit_salle3_route_expects_conditions_schema(client):
    # /rooms/3/submit est une route dediee (EnigmeConditionnelleSubmission) :
    # un payload au format "answer" (celui des autres salles) est rejete par
    # la validation Pydantic, pas par une verification manuelle salle_id == 3.
    response = client.post("/rooms/3/submit", json={"answer": "x"})

    assert response.status_code == 422


def test_submit_salle3_with_correct_conditions_succeeds(client):
    response = client.post(
        "/rooms/3/submit",
        json={"conditions": {"firewall_neutralise": True, "boucle_stoppee": True}},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_submit_salle3_with_incomplete_conditions_fails(client):
    response = client.post(
        "/rooms/3/submit",
        json={"conditions": {"firewall_neutralise": True, "boucle_stoppee": False}},
    )

    assert response.status_code == 200
    assert response.json()["success"] is False


def test_submit_salle3_with_empty_conditions_is_rejected(client):
    response = client.post("/rooms/3/submit", json={"conditions": {}})

    assert response.status_code == 422


def test_submit_salle4_correct_patch_sets_victory(client):
    response = client.post(
        "/rooms/4/submit", json={"answer": "reboot --force --patch=core"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["game_status"] == "victory"


def test_game_status_endpoint_reflects_state(client):
    assert client.get("/rooms/status/game").json() == {"status": "in_progress"}

    client.post("/rooms/4/submit", json={"answer": "reboot --force --patch=core"})

    assert client.get("/rooms/status/game").json() == {"status": "victory"}
