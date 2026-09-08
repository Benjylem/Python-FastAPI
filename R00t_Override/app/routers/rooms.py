from fastapi import APIRouter

router = APIRouter(prefix="/rooms", tags=["rooms"])


# @router.get("/1")
# def get_salle1():
#     return {"message": "Tu es bien dans la salle 1"}

# @router.get("/2")
# def get_salle2():
#     return {"message": "Tu es bien dans la salle 2"}

salles = {
    1: {"name": "Pare-Feu", "bio": "Obtenez la Clé de Validation Externe"},
    2: {"name": "Proxy", "bio": "Décrochez les Privilèges Intermédiaires"}
}

@router.get("/")
def get_rooms():
    return list(salles.keys())

@router.get("/{salle_id}")
def get_room(salle_id):
    return salle_id, salles.get(int(salle_id))
