import pytest
from fastapi.testclient import TestClient

from app.domain.players import players
from app.domain.session import sessions
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    """Sessions et joueurs sont stockés dans des dicts globaux : on les remet à
    l'état initial après chaque test (joueurs de base sans équipe, joueurs
    créés pendant le test supprimés) pour que les tests restent indépendants."""
    joueurs_initiaux = set(players)
    sessions.clear()
    yield
    sessions.clear()
    for player_id in set(players) - joueurs_initiaux:
        del players[player_id]
    for player in players.values():
        player.session_id = None


@pytest.fixture
def lobby_id(client):
    """Crée une équipe (en lobby, sans joueur) et renvoie l'id de la session."""
    return client.post("/sessions/start", json={"team_name": "Hackers"}).json()["id"]


@pytest.fixture
def session_id(client, lobby_id):
    """Équipe avec Joe (id 1), partie lancée : prête à soumettre des réponses."""
    client.post(f"/sessions/{lobby_id}/players", json={"player_id": 1})
    client.post(f"/sessions/{lobby_id}/launch")
    return lobby_id
