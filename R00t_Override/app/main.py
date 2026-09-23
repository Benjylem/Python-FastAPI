from fastapi import FastAPI

from app.routers import players, rooms, sessions

app = FastAPI(title="RootOverride API Test")

app.include_router(rooms.router)
app.include_router(players.router)
app.include_router(sessions.router)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Environnement Conda prêt pour l'Escape Game R00T override Routes tested!"}

