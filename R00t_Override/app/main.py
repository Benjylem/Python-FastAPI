from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging_config import setup_logging
from app.routers import players, rooms, sessions
from app.services.exceptions import ServiceError

setup_logging()

app = FastAPI(title="RootOverride API Test")

app.include_router(rooms.router)
app.include_router(players.router)
app.include_router(sessions.router)


@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    """Traduit les erreurs métier des services en réponse HTTP (404, 403, 409)."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Environnement Conda prêt pour l'Escape Game R00T override Routes tested!"}
