class Creature(object):
	def __init__(self, name, race, combat_class, description=None):
		self.name = name
		self.race = race
		self.combat_class = combat_class
		self.description = description
		self.event = None

class Player(Creature):
	def __init__(self, name, race, combat_class, description=None):
		Creature.__init__(self, name, race, combat_class, description)