import copy

import pytest
from fastapi.testclient import TestClient

from app.data.players import players
from app.data.sessions import sessions
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    """Joueurs et sessions sont stockés dans des dicts globaux : on restaure les
    joueurs de départ (après un POST, PUT, DELETE ou un changement d'équipe) et
    on vide les sessions, pour que les tests restent indépendants."""
    players_initiaux = copy.deepcopy(players)
    sessions.clear()
    yield
    players.clear()
    players.update(players_initiaux)
    sessions.clear()


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
