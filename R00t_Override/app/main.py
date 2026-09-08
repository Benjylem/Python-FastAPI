from fastapi import FastAPI

app = FastAPI(title="RootOverride API Test")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Environnement Conda prêt pour l'Escape Game R00T override !"}