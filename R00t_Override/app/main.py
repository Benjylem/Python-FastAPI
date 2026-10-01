import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging_config import setup_logging
from app.routers import players, rooms, sessions
from app.services.exceptions import ServiceError

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="RootOverride API Test")

app.include_router(rooms.router)
app.include_router(players.router)
app.include_router(sessions.router)


@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    """Traduit les erreurs métier des services en réponse HTTP (404, 403, 409)."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    """Filet de sécurité : toute exception imprévue est journalisée avec sa trace
    complète, et le client reçoit une 500 sans détail interne."""
    logger.exception("Erreur inattendue sur %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Erreur interne"})


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Environnement Conda prêt pour l'Escape Game R00T override !"}


@app.get("/health")
def health_check():
    return {"status": "online", "game_title": "R00T override", "engine_version": "1.0.0"}