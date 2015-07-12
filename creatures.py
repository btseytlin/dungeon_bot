import logging
import util

default_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn qeue
	"intelligence": 5, #how likely you are to strike a critical
	"faith": 5, #how much energy you have
}

"""
Tags:
	animate - Marks objects that are living biological creatures. For example gargolyes are not animate, golems are not animate.
	humanoid - Marks objects that have humanoid traits. Most sentinent creatures are humanoid.

"""

class Creature(object):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, description=None, tags=[],abilities=[], max_health=0, max_energy=0, health=0, energy=0):
		self.name = name
		self.race = race
		self.combat_class = combat_class
		self.description = description
		self.event = None
		self.uid = util.get_uid()
		self.tags = []
		self.abilities = []
		self.max_health = 0
		self.health = 0

		self.max_energy = 0
		self.energy = 0

	def __str__(self):
		desc = ""
		if self.name:
			desc+="You see %s.\n"%(self.name)
		desc+="It's a %s %s.\n"%(self.combat_class, self.race)
		desc+="It has %d health and %d energy.\n"%(self.health, self.energy)
		if self.description:
			desc+="%s"%(self.description)
		return desc

	def __repr__(self):
		return self.__str__()

class Player(Creature):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, description=None, inventory=[], tags=["animate", "humanoid"],abilities=[], max_health=0, max_energy=0, health=0, energy=0, level=1):
		Creature.__init__(self, name, race, combat_class, description, max_health, max_energy, health, energy)
		self.level = level
		self.inventory = inventory

	def __str__(self):
		desc = super(Player, self).__str__()
		desc += "It is of level %d.\n"%(self.level)
		return desc

class Enemy(Creature):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, description=None, tags=[],abilities=[], max_health=0, max_energy=0, health=0, energy=0, level=1, exp_earned=0):
		Creature.__init__(self, name, race, combat_class, description, max_health, max_energy, health, energy)
		self.level = level


	def __str__(self):
		desc = super(Player, self).__str__()
		desc += "It is of level %d.\n"%(self.level)
		return desc