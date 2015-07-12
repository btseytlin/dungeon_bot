import logging
import util


default_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn qeue
	"intelligence": 5, #how likely you are to strike a critical
	"faith": 5, #how much energy you have
}

default_stats = {
	"health": 0,
	"energy": 0
	"max_health": 0,
	"max_energy": 0,
	"defence": 0,
	"evasion": 0,
	"level": 1
}

"""
Tags:
	animate - Marks objects that are living biological creatures. For example gargolyes are not animate, golems are not animate.
	humanoid - Marks objects that have humanoid traits. Most sentinent creatures are humanoid.

"""

class Creature(object):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, stats= default_stats, description=None, tags=[],abilities=[], modifiers = []):
		self.name = name
		self.race = race
		self.combat_class = combat_class
		self.description = description
		self.event = None
		self.uid = util.get_uid()

		self.max_health = 0
		self.health = 0
		self.max_energy = 0
		self.energy = 0

		self.modifiers = []
		self.characteristics = characteristics
		self.stats = default_stats
		self.base_stats = default_stats.copy()
		self.tags = []
		self.abilities = []



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

default_equipment = {
	"armor": None,
	"primary_weapon": None,
	"secondary_weapon": None,
	"ring": None,
	"talisman": None,
	"headwear": None
}

class Player(Creature):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, stats=default_stats, description=None, inventory=[], equipment=default_equipment, tags=["animate", "humanoid"],abilities=[], level_perks=[]):
		Creature.__init__(self, name, race, combat_class,characteristics, stats, description, tags, abilities, modifiers)
		self.level = level
		self.inventory = inventory
		self.equipment = equipment
		self.level_perks = level_perks

	def examine_inventory(self):
		pass

	def examine_self(self):
		desc = super(Player, self).__str__()
		desc += "It is of level %d.\n"%(self.level)
		return desc

	def refresh_modifiers(self):
		pass

	def refresh_abilities(self):
		self.abilities = []
		for perk in level_perks:
			self.abilities = list(set(self.abilities + perk.abilities_granted))

		for modifier in self.modifiers:
			self.abilities = list(set(self.abilities + modifier.abilities_granted))

		for item in self.equipment:
			if item:
				self.abilities = list(set(self.abilities + item.abilities_granted))

	def __str__(self):
		return self.examine_self()

default_enemy_stats = {
	"health": 0,
	"energy": 0
	"max_health": 0,
	"max_energy": 0,
	"defence": 0,
	"evasion": 0,
	"level": 1,
	"exp_value": 0
}

class Enemy(Creature):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, stats = default_enemy_stats, description=None, tags=[],abilities=[]):
		Creature.__init__(self, name, race, combat_class,characteristics, stats, description, tags, abilities, modifiers)
		self.level = level

	def __str__(self):
		desc = super(Player, self).__str__()
		desc += "It is of level %d.\n"%(self.level)
		return desc