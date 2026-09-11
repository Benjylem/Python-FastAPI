from app.domain.GameElement import GameElement

class Salle(GameElement):
	def __int__(self, id, name, bio):
		GameElement.__init__(self, id, name, bio)
		self.salle.id = id
		self.salle.name = name
		self.salle.bio = bio
