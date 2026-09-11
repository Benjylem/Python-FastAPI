from fastapi import FastAPI

from pydantic import BaseModel, Field

router = FastAPI()

class Salle(BaseModel):
    name: str
    bio: str
    reward: str

class Player(BaseModel):
    name: str = Field(min_length=3)
    reward1: bool
    reward2: bool
    reward3: bool
    reward4: bool

salles = {
    1: {"name": "Pare-Feu", "bio": "Obtenez la Clé de Validation Externe"},
    2: {"name": "Proxy", "bio": "Décrochez les Privilèges Intermédiaires"},
    3: {"name": "Matrice des Contre-Mesures", "bio": "Désamorcer le piège et récupérez le Module de Déchiffrement du Cœur"},
    4: {"name": "Noyau Central", "bio": "Identifiez la ligne critique défectueuse, injectez le patch et valider la commande de reboot du système"}
}

@router.get("/rooms")
def get_rooms():
    return list(salles.keys())

@router.get("/rooms/{salle_id}")
def get_room(salle_id):
    return salle_id, salles.get(int(salle_id))
