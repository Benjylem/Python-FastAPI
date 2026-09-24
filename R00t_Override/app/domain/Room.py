from app.domain.GameElement import GameElement

class Salle(GameElement):
	def __init__(self, id, name, bio):
		GameElement.__init__(self, id, name, bio)
		self.id = id
		self.name = name
		self.bio = bio
