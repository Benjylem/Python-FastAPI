from fastapi import FastAPI
# from app.domain.GameElement import GameElement

from app.routers import rooms

app = FastAPI(title="RootOverride API Test")

app.include_router(rooms.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Environnement Conda prêt pour l'Escape Game R00T override !"}

# salle_1 = GameElement(1, "pare-Feu", "Obtenez la Clé de Validation Externe")

salles = {
    1: {"name": "Pare-Feu", "bio": "Obtenez la Clé de Validation Externe"},
    2: {"name": "Proxy", "bio": "Décrochez les Privilèges Intermédiaires"}
}

@app.get("/rooms")
def get_rooms():
    return list(salles.keys())

@app.get("/rooms/{salle_id}")
def get_room(salle_id):
    return salle_id, salles.get(int(salle_id))
