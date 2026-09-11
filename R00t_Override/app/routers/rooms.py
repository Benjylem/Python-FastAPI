from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

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

players = {
    1: {"name": "Joe", "reward1": False, "reward2": False, "reward3": False, "reward4": False },
    2: {"name": "Jasmine", "reward1": False, "reward2": False, "reward3": False, "reward4": False },
}

@router.get("/rooms")
def get_rooms():
    return list(salles.keys())

@router.get("/rooms/{salle_id}")
def get_room(salle_id):
    return salle_id, salles.get(int(salle_id))

@router.get("/players")
def get_players():
    return players

@router.get("/players/{player_id}")
def get_player(player_id: int):
    return players.get(player_id)

@router.post("/players")
def create_player(player: Player):
    new_id = max(p["id"] for p in players) + 1
    new_player = {"id": new_id, **player.model_dump()}
    players.append(new_player)
    return new_player
