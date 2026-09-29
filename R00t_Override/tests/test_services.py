"""Les services s'utilisent sans HTTP : ils lèvent des erreurs métier,
que main.py traduit ensuite en codes HTTP."""

import pytest

from app.services import player_service, room_service, session_service
from app.services.exceptions import Conflict, Forbidden, NotFound


def test_unknown_room_raises_not_found():
    with pytest.raises(NotFound):
        room_service.get_salle(99)


def test_unknown_player_raises_not_found():
    with pytest.raises(NotFound):
        player_service.get_player(999)


def test_launch_without_player_raises_conflict():
    session = session_service.create_session("Solo")

    with pytest.raises(Conflict):
        session_service.launch(session.id)


def test_locked_room_raises_forbidden():
    session = session_service.create_session("Hackers")
    session_service.join_team(session.id, 1)
    session_service.launch(session.id)

    with pytest.raises(Forbidden):
        session_service.submit(session.id, 2, "ADMIN_TOKEN_X987F")


def test_submit_through_service_advances_session():
    session = session_service.create_session("Hackers")
    session_service.join_team(session.id, 1)
    session_service.launch(session.id)

    resultat = session_service.submit(session.id, 1, "root_override")

    assert resultat["success"] is True
    assert session.current_room == 2
