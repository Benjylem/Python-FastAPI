from app.domain.session import Session

# Sessions en mémoire pour tester ; remplacé plus tard par une vraie table DB.
sessions: dict[int, Session] = {}


def create_session(team_name: str) -> Session:
    new_id = max(sessions.keys(), default=0) + 1
    session = Session(new_id, team_name)
    sessions[new_id] = session
    return session
