import logging
import util
class Creature(object):
	def __init__(self, name, race, combat_class, description=None, max_health=0, max_energy=0, health=0, energy=0):
		self.name = name
		self.race = race
		self.combat_class = combat_class
		self.description = description
		self.event = None
		self.uid = util.get_uid()

		#
		self.max_health = 0
		self.health = 0

		self.max_energy = 0
		self.energy = 0

	def __str__(self):
		desc = ""
		if name:
			desc+="You see %s\n."%(self.name)
		desc+="It's a %s %s\n."%(self.combat_class, self.race)
		desc+="It has %d health and %d energy\n."%(self.health, self.energy)
		desc+="%s"%(self.description)
		return desc

	def __repr__(self):
		return self.__str__()

class Player(Creature):
	def __init__(self, name, race, combat_class, description=None, max_health=0, max_energy=0, health=0, energy=0, level=1):
		Creature.__init__(self, name, race, combat_class, description, max_health, max_energy, health, energy)
		self.level = level

	def __str__(self):
		desc = super().__str__()
		desc += "It is of level %d\n."%(self.level)