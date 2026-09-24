import copy

import pytest
from fastapi.testclient import TestClient

from app.domain.game_state import game_state
from app.main import app
from app.routers.players import players
from app.routers.sessions import sessions


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_game_state():
    """game_state est un dict global partagé par toutes les routes : on le
    remet à zéro avant chaque test pour que l'ordre d'exécution n'influence
    pas les résultats (ex: un test qui gagne la salle 4 ne doit pas laisser
    le jeu en 'victory' pour les tests suivants)."""
    game_state["status"] = "in_progress"
    yield
    game_state["status"] = "in_progress"


@pytest.fixture(autouse=True)
def reset_players_and_sessions():
    """players et sessions sont aussi des globales en mémoire : on restaure
    les joueurs de départ et on vide les sessions pour qu'un DELETE ou un
    POST dans un test ne fausse pas les suivants."""
    players_initiaux = copy.deepcopy(players)
    sessions.clear()
    yield
    players[:] = players_initiaux
    sessions.clear()
