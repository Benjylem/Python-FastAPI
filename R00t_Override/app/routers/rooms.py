from fastapi import APIRouter

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/1")
def get_salle1():
    return {"message": "Tu es bien dans la salle 1"}

@router.get("/2")
def get_salle2():
    return {"message": "Tu es bien dans la salle 2"}
