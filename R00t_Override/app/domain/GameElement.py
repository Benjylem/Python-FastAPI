class GameElement:

    def __init__(self, id: int, name: str, bio: str):
        self.id = id
        self.name = name
        self.bio = bio
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "bio": self.bio}