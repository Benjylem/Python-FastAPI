def test_get_players_returns_seed_data(client):
    response = client.get("/players/")

    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert "Joe" in names
    assert "Jasmine" in names


def test_get_player_by_id(client):
    response = client.get("/players/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Joe"


def test_get_unknown_player_returns_404(client):
    response = client.get("/players/999")

    assert response.status_code == 404


def test_create_player_assigns_incremental_id(client):
    payload = {"name": "Alice"}

    response = client.post("/players/", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice"
    assert isinstance(body["id"], int)

    # le joueur cree doit ensuite etre lisible via GET /players/{id}
    follow_up = client.get(f"/players/{body['id']}")
    assert follow_up.status_code == 200


def test_create_player_rejects_short_name(client):
    payload = {"name": "Al"}

    response = client.post("/players/", json=payload)

    assert response.status_code == 422
