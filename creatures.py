import logging
import util
import json
import items
import abilities
default_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn qeue
	"intelligence": 5, #how likely you are to strike a critical
	"faith": 5, #how much energy you have
}

default_stats = {
	"health": 100,
	"energy": 100,
	"max_health": 100,
	"max_energy": 100,
	"defence": "1d2",
	"evasion": "1d2",
	"level": 1
}

"""
Tags:
	animate - Marks objects that are living biological creatures. For example gargolyes are not animate, golems are not animate.
	humanoid - Marks objects that have humanoid traits. Most sentinent creatures are humanoid.

"""

default_equipment = {
	"armor": None,
	"primary_weapon": None,
	"secondary_weapon": None,
	"ring": None,
	"talisman": None,
	"headwear": None
}

default_abilties = ["rest"]

class Creature(object):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, stats= default_stats, description=None, inventory=[], equipment=default_equipment, tags=[],abilities=[], modifiers = []):

		self.name = name
		self.race = race
		self.combat_class = combat_class
		self.description = description
		self.event = None
		#self.uid = util.get_uid()

		self.stats = stats


		self.modifiers = modifiers
		self.characteristics = characteristics
		
		self.base_stats = stats.copy()
		self.tags = tags
		self.abilities = abilities + default_abilties

		self.inventory = inventory
		self.equipment = equipment
		self.dead = False

	@property
	def health(self):
		return self.stats["health"]

	@health.setter
	def health(self, value):
		if value > self.stats["max_health"]:
			value = self.stats["max_health"]
		self.stats["health"] = value

	@property
	def energy(self):
		return self.stats["energy"]

	@energy.setter
	def energy(self, value):
		if value > self.stats["max_energy"]:
			value = self.stats["max_energy"]
		self.stats["energy"] = value

	@property
	def primary_weapon(self):
		return self.equipment["primary_weapon"]

	@primary_weapon.setter
	def primary_weapon(self, value):
		self.equipment["primary_weapon"] = value

	@property
	def armor(self):
		return self.equipment["armor"]

	@armor.setter
	def armor(self, value):
		self.equipment["armor"] = value

	@property
	def secondary_weapon(self):
		return self.equipment["secondary_weapon"]

	@secondary_weapon.setter
	def secondary_weapon(self, value):
		self.equipment["secondary_weapon"] = value

	@property
	def ring(self):
		return self.equipment["ring"]

	@ring.setter
	def ring(self, value):
		self.equipment["ring"] = value

	@property
	def talisman(self):
		return self.equipment["talisman"]

	@talisman.setter
	def talisman(self, value):
		self.equipment["talisman"] = value

	@property
	def headwear(self):
		return self.equipment["headwear"]

	@headwear.setter
	def headwear(self, value):
		self.equipment["headwear"] = value

	def kill_if_nececary(self):
		if self.health <= 0:
			return True, self.die()
		return False, None

	def die(self, killer=None):
		self.dead = True
		if killer:
			return "%s is killed by %s."%(self.name, killer.name)
		return "%s dies."%(self.name)

	def examine_equipment(self):
		desc = "%s's equipment:\n"%(self.name)
		for key in self.equipment.keys():
			item = self.equipment[key]
			if item:
				desc+="%s: %s.\n"%(key, item.name)
		return desc

	def examine_inventory(self):
		desc = "%s's inventory:\n"%(self.name)
		items = []
		for item in self.inventory:
			if item:
				items.append(item.name)
		return desc + ', '.join(items)

	def refresh_modifiers(self):
		pass

	def refresh_abilities(self):
		self.abilities = default_abilties
		for perk in self.level_perks:
			self.abilities = list(set(self.abilities + perk.abilities_granted))

		for modifier in self.modifiers:
			self.abilities = list(set(self.abilities + modifier.abilities_granted))

		for key in self.equipment.keys():
			if self.equipment[key]:
				self.abilities = list(set(self.abilities + self.equipment[key].abilities_granted))

	def examine_self(self):
		desc = ""
		if self.name:
			desc+="You see %s.\n"%(self.name)
		desc+="It's a %s %s.\n"%(self.combat_class, self.race)
		desc+="It has %d health and %d energy.\n"%(self.health, self.energy)
		desc += "It has the following abilities:\n"
		for ability in self.abilities:
			desc += "  %s\n"%(ability)
		if len(self.modifiers) > 0:
			desc += "It has the following modifiers:\n"
			for modifier in self.modifiers:
				desc += "  %s\n"%(modifier)
		if self.description:
			desc+="%s\n"%(self.description)
		return desc


	def to_json(self):
		big_dict = self.__dict__.copy()
		big_dict["characteristics"] = json.dumps(self.characteristics)
		big_dict["tags"] = json.dumps(self.tags)
		big_dict["abilities"] = json.dumps(self.abilities)
		big_dict["stats"] = json.dumps(self.stats)
		big_dict["modifiers"] = json.dumps(self.modifiers)

		big_dict["inventory"] = []
		for item in self.inventory:
			big_dict["inventory"].append(item.to_json())
		big_dict["inventory"] = json.dumps(big_dict["inventory"])
		big_dict["equipment"] = default_equipment
		for key in self.equipment:
			if self.equipment[key]:
				big_dict["equipment"]["key"] = self.equipment[key].to_json()
		big_dict["equipment"] = json.dumps(big_dict["equipment"])
		return json.dumps(big_dict)


default_player_stats = {
	"health": 100,
	"energy": 100,
	"max_health": 100,
	"max_energy": 100,
	"defence": "1d2",
	"evasion": "1d2",
	"level": 1,
	"experience": 0,
	"max_experience": 1000
}


class Player(Creature):
	def __init__(self, username, name, race, combat_class, characteristics = default_characteristics, stats=default_player_stats, description=None, inventory=[], equipment=default_equipment, tags=["animate", "humanoid"],abilities=[],modifiers=[], level_perks=[]):
		Creature.__init__(self, name, race, combat_class,characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)
		self.level_perks = level_perks
		self.username = username

	@property
	def experience(self):
		return self.stats["experience"]

	@experience.setter
	def experience(self, value):
		if value > self.stats["max_experience"]:
			over_cur_level = value - (self.stats["max_experience"] - self.experience)
			self.level = self.level +  1
			self.experience = over_cur_level
		self.stats["experience"] = value

	@property
	def level(self):
		return self.stats["level"]

	@level.setter
	def level(self, value):
		self.stats["level"] = value
		self.stats["max_experience"] = value * 1000

	def examine_self(self):
		desc = super(Player, self).examine_self()
		desc += "It is of level %d.\n"%(self.stats["level"])
		return desc

	@staticmethod
	def de_json(data):
		return Player(data.get("name"), data.get("race"), data.get("combat_class"), data.get("characteristics"), data.get("stats"), data.get("description"), data.get("inventory"), data.get("equipment"), data.get('tags'), data.get("abilities"), data.get("modifiers"), data.get("level_perks"))

	def __str__(self):
		return self.examine_self()

default_enemy_stats = {
	"health": 0,
	"energy": 0,
	"max_health": 0,
	"max_energy": 0,
	"defence": "1d2",
	"evasion": "1d2",
	"level": 1,
	"exp_value": 0
}

class Enemy(Creature):
	def __init__(self, name, race, combat_class, characteristics = default_characteristics, stats=default_enemy_stats, description=None, inventory=[], equipment=default_equipment, tags=[],abilities=["rest"],modifiers=[]):

		Creature.__init__(self, name, race, combat_class,characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)

	def act(self):
		ability = abilities.abilities["rest"]
		msg = ability.use(self)
		return msg

		return "%s skips turn"%(self.name)

	def die(self, killer=None):
		if killer:
			msg = "%s is killed by %s.\n"%(self.name, killer.name)
			if isinstance(killer, Player):
				killer.experience += self.stats["exp_value"]
				msg += "%s earns %d experience.\n"%(killer.name, self.stats["exp_value"])
			return msg
		return "%s dies."%(self.name)

	@staticmethod
	def de_json(data):
		inventory = []
		if data.get("inventory") and len(data.get("inventory"))!=0:
			for thing in data.get("inventory"):
				inventory.append(Item.de_json(thing))

		equipment = {
			"armor": None,
			"primary_weapon": None,
			"secondary_weapon": None,
			"ring": None,
			"talisman": None,
			"headwear": None
		}
		if data.get("equipment") and len(data.get("equipment"))!=0:
			for thing in len(data.get("equipment").keys()):
				equipment[thing] = Item.de_json(data.get("equipment")[thing])
					
		return Enemy(data.get("name"), data.get("race"), data.get("combat_class"), data.get("characteristics"), data.get("stats"), data.get("description"), inventory, equipment, data.get('tags'), data.get("abilities"), data.get("modifiers"))

		return desc