from fastapi import FastAPI
# from app.domain.GameElement import GameElement

from app.routers import rooms

app = FastAPI(title="RootOverride API Test")

app.include_router(rooms.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Environnement Conda prêt pour l'Escape Game R00T override Routes tested!"}

# salle_1 = GameElement(1, "pare-Feu", "Obtenez la Clé de Validation Externe")

