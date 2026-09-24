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


def test_get_room1_prompt_contains_encoded_key(client):
    assert "cm9vdF9vdmVycmlkZQ==" in client.get("/rooms/1").json()["enigme"]


def test_get_room2_prompt_contains_logs(client):
    assert "ADMIN_TOKEN_X987F" in client.get("/rooms/2").json()["enigme"]
