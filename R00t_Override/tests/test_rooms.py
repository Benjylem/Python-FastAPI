def test_get_rooms_returns_all_ids(client):
    response = client.get("/rooms/")

    assert response.status_code == 200
    assert response.json() == [1, 2, 3, 4]


def test_get_room_shows_only_public_map(client):
    # l'énoncé n'est lisible que via /sessions/{id}/rooms/{n}/enigma
    response = client.get("/rooms/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Pare-Feu",
        "bio": "Obtenez la Clé de Validation Externe",
    }


def test_get_unknown_room_returns_404(client):
    response = client.get("/rooms/99")

    assert response.status_code == 404

