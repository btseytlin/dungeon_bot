import json
from pprint import pformat
from items import *
from util import *
from modifiers import *
import random
default_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how much energy you have, your position in turn qeue
	"intelligence": 5, #how likely you are to cause critical effects when attacking
	"faith": 5, #how much energy you have
}

default_equipment = {
	"armor": None,
	"primary_weapon": None,
	"secondary_weapon": None,
	"ring": None,
	"talisman": None,
	"headwear": None
}

default_abilties = []

class Creature(object):
	def __init__(self, name, race, combat_class, level=1, characteristics = default_characteristics, stats=None, description=None, inventory=[], equipment=default_equipment, tags=[],abilities=[], modifiers = []):

		self.uid = get_uid()
		self.name = name
		self.race = race
		self.combat_class = combat_class
		self.description = description
		self.event = None
		self._level = level


		self.modifiers = modifiers.copy()
		#self.characteristics = characteristics.copy()
		self.base_characteristics = characteristics.copy()
		
		self.base_tags = tags.copy()
		self.base_abilities = abilities + default_abilties.copy()

		self.inventory = inventory.copy()
		self.equipment = equipment.copy()

		self.base_stats = self.get_base_stats_from_characteristics(self.characteristics)

		#if stats:
		#	self.stats = stats.copy()
		#else:
		#	self.stats = self.base_stats

		self.dead = False

		self.refresh_derived()

	def get_base_stats_from_characteristics(self, characteristics): #stats are completely derived from characteristics
		stats =  {
			"health": 0,
			"energy": 0,
			"max_health": 0,
			"max_energy": 0,
			"energy_regen": 0
		}

		stats["max_health"] = characteristics["vitality"]* 10
		stats["max_energy"] = characteristics["dexterity"]
		stats["energy_regen"] = clamp(int(characteristics["dexterity"] / 3), 2, 10)
		stats["health"] = stats["max_health"]
		stats["energy"] = stats["max_energy"]
		return stats

	@property
	def health(self):
		return self.stats["health"]

	@health.setter
	def health(self, value):
		if value > self.stats["max_health"]:
			value = self.stats["max_health"]
		if value < 0:
			value = 0
		self.stats["health"] = value

	@property
	def energy(self):
		return self.stats["energy"]

	@energy.setter
	def energy(self, value):
		if value > self.stats["max_energy"]:
			value = self.stats["max_energy"]
		if value < 0:
			value = 0
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

	@property
	def defence(self):
		base_def = diceroll("1d1")
		defence = base_def
		for key in list(self.equipment.keys()):
			if self.equipment[key] and "defence" in list(self.equipment[key].stats.keys()):
				defence += diceroll(self.equipment[key].stats["defence"])

		for modifier in self.modifiers:
			if hasattr(modifier, "defence"):
				defence += diceroll(modifier.defence)

		#todo defence from level perks

		return defence

	@property
	def evasion(self):
		base_ev = diceroll(str(self.characteristics["dexterity"])+"d6")
		evasion = base_ev
		for key in list(self.equipment.keys()):
			if self.equipment[key] and "evasion" in list(self.equipment[key].stats.keys()):
				evasion += diceroll(self.equipment[key].stats["evasion"])

		for modifier in self.modifiers:
			if hasattr(modifier, "evasion"):
				evasion += diceroll(modifier.evasion)

		#todo evasion from level perks
		return evasion


	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, value):
		self._level = value

	def equip(self, target_item):
		if target_item.item_type == "consumable":
			return "Can't equip %s."%(target_item.name)

		if self.equipment[target_item.item_type] == target_item:
			return "Already equipped %s."%(target_item.name)

		if self.equipment[target_item.item_type]:
			temp = self.equipment[target_item.item_type]
			self.unequip(temp)

		self.equipment[target_item.item_type] = target_item
		for item in self.inventory:
			if item == target_item:
				target_item.inventory.remove(item)

		self.refresh_abilities()
		self.refresh_modifiers()
		self.refresh_tags()
		return "Succesfully equipped %s."%(target_item.name)

	def unequip(self, target_item):
		if target_item.item_type == "consumable":
			return "Can't unequip %s."%(target_item.name)
		if self.equipment[self.item_type] == self:
			self.equipment[self.item_type] = None
			self.inventory.append(self)
			self.refresh_abilities()
			self.refresh_modifiers()
			self.refresh_tags()
			return "Succesfully unequipped %s."%(target_item.name)
		return "Not equipped!"

	def destroy(self, target_item):
		self.unequip(target_item)
		for item in self.inventory:
			if item == self:
				self.inventory.remove(item)
		return "Succesfully destroyed %s."%(target_item.name)

	def use(self, item, target):
		if item in self.inventory:
			return item.use(self, target)

	def apply_combat_start_effects(self):
		pass

	def apply_combat_over_effects(self):
		self.energy = self.stats["max_energy"]

	def apply_turn_effects(self):
		#regenerate energy
		self.energy += self.stats["energy_regen"]
		#apply the effects of all modifiers

	def kill_if_nececary(self, killer=None):
		if self.health <= 0:
			return True, self.die(killer)
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
		for i in range(len(self.inventory)):
			item = self.inventory[i]
			if item:
				items.append(str(i+1)+"."+item.name)
		return desc + ', '.join(items)

	def refresh_tags(self):
		self.tags = self.base_abilities.copy()
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for tag in perk.tags_granted:
					self.tags.append(tag)

		for modifier in self.modifiers:
			for tag in modifier.tags_granted:
				self.tags.append(tag)

		for key in self.equipment.keys():
			if self.equipment[key]:
				for tag in self.equipment[key].tags_granted:
					self.tags.append(tag)

	def refresh_modifiers(self):
		self.modifiers = []
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for modifier in perk.modifiers_granted:
					modifier_object = get_modifier_by_name( modifier["name"], perk, self, modifier["params"] )
					self.modifiers.append(modifier_object)
					modifier_object.apply()

		for key in self.equipment.keys():
			if self.equipment[key]:
				for modifier in self.equipment[key].modifiers_granted:
					modifier_object = get_modifier_by_name( modifier["name"], perk, self, modifier["params"] )
					modifier_object.apply()

	def refresh_abilities(self):
		self.abilities = self.base_abilities.copy()
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for ability in perk.abilities_granted:
					self.abilities.append({"granted_by":perk, "ability_name": ability})

		for modifier in self.modifiers:
			for ability in modifier.abilities_granted:
				self.abilities.append({"granted_by":modifier, "ability_name": ability})

		for key in self.equipment.keys():
			if self.equipment[key]:
				for ability in self.equipment[key].abilities_granted:
					self.abilities.append({"granted_by":self.equipment[key], "ability_name": ability})

	def refresh_derived(self):
		self.refresh_modifiers()
		self.refresh_abilities()
		self.refresh_tags()
		self.characteristics = self.base_characteristics.copy()
		#refresh characteristics
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for characteristic in list(perk.characteristics_change.keys()):
					self.characteristics[characteristic] += perk.characteristics_change[characteristic]

		for modifier in self.modifiers:
			for characteristic in list(modifier.characteristics_change.keys()):
					self.characteristics[characteristic] += modifier.characteristics_change[characteristic]
		
		for item in list(self.equipment.keys()):
			if self.equipment[item] and "characteristics_change" in list(self.equipment[item].stats.keys()):
				for characteristic in list(self.equipment[item].stats["characteristics_change"].keys()):
					self.characteristics[characteristic] += self.equipment[item].stats["characteristics_change"][characteristic]

		self.stats = self.base_stats.copy()
		#refresh stats
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for stat in list(perk.stats_change.keys()):
					self.stats[stat] += perk.stats_change[stat]

		for modifier in self.modifiers:
			for stat in list(modifier.stats_change.keys()):
					self.stats[stat] += modifier.stats_change[stat]
		
		for item in list(self.equipment.keys()):
			if self.equipment[item] and "stats_change" in list(self.equipment[item].stats.keys()):
				for stat in list(self.equipment[item].stats["stats_change"].keys()):
					self.stats[stat] += self.equipment[item].stats["stats_change"][stat]

	def examine_self(self):
		desc = "\n".join(
		[
			"%s. lvl %d"%(self.name.title(), self.level),
			"%s"%(self.description or "----"),
			"Race: %s, class: %s."%(self.race, self.combat_class),
			"Characteristics:\n%s"%(pformat(self.characteristics, width=1)),
			"Stats:\n%s"%(pformat(self.stats, width=1)),
			"Tags:\n%s"%(", ".join(self.tags)),
			"Modifiers:\n%s"%(", ".join(["%s(%s)"%(modifier.name, modifier.granted_by) for modifier in self.modifiers])),
			"Abilities:\n%s"%(", ".join(["%s(%s)"%(ab["ability_name"], ab["granted_by"].name) for ab in self.abilities]))
		])
		return desc

	def to_json(self):
		big_dict = self.__dict__.copy()
		del big_dict["uid"]
		big_dict["characteristics"] = json.dumps(self.characteristics)
		# big_dict["tags"] = json.dumps(self.tags)
		del big_dict["abilities"] #abilities are not serializable
		del big_dict["modifiers"] #modifiers are derived so no point in serializing them
		big_dict["inventory"] = []
		for item in self.inventory:
			big_dict["inventory"].append(item.to_json())
		big_dict["equipment"] = default_equipment.copy()
		for key in self.equipment:
			if self.equipment[key]:
				big_dict["equipment"][key] = self.equipment[key].to_json()
		#big_dict["equipment"] = json.dumps(big_dict["equipment"])
		return big_dict

class Player(Creature):
	def __init__(self, username, name, race, combat_class, level=1, characteristics = default_characteristics, stats=None, description=None, inventory=[], equipment=default_equipment, tags=["animate", "humanoid"],abilities=[],modifiers=[], level_perks=[], experience=0, max_experience=1000):
		self.level_perks = level_perks.copy()
		self._experience = experience
		self.max_experience = max_experience
		self.username = username

		Creature.__init__(self, name, race, combat_class, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)

	@property
	def experience(self):
		return self._experience

	@experience.setter
	def experience(self, value):
		if value > self.max_experience:
			over_cur_level = value - (self.max_experience - self.experience)
			self.level = self.level +  1
			self.experience = over_cur_level
		else:
			self._experience = value

	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, value):
		self._level = value
		self.max_experience = value * 1000

	def examine_self(self):
		desc = super(Player, self).examine_self()
		return desc

	@staticmethod
	def de_json(data):
		if isinstance(data, str):
			data = json.loads(data)
		data["characteristics"] = json.loads(data["characteristics"])
		stats = None
		if "stats" in list(data.keys()):
			stats = data["stats"]
			if isinstance(data["stats"], str):
				data["stats"] = json.loads(data["stats"])
				stats = data["stats"]

		for i in range(len(data["inventory"])):
			data["inventory"][i] = Item.de_json(data["inventory"][i])

		equipment = default_equipment.copy()
		eq = data["equipment"]
		for key in list(eq.keys()):
			if eq[key]:
				equipment[key] = Item.de_json(eq[key])

		data["equipment"] = equipment
		ply = Player(data.get("username"), data.get("name"), data.get("race"), data.get("combat_class"), data.get("_level"), data.get("characteristics"), stats, data.get("description"), data.get("inventory"), data.get("equipment"), data.get('tags'), [], [], data.get("level_perks"), data.get("_experience"), data.get("max_experience"))
		return ply

	def to_json(self):
		big_dict = super(Player, self).to_json()
		big_dict["username"] = self.username
		big_dict["event"] = None
		return big_dict

	def __str__(self):
		return self.examine_self()

class Enemy(Creature):

	loot_coolity = 0

	drop_table = {

	}

	def __init__(self, name, race, combat_class, level=1, characteristics = default_characteristics, stats=None, description=None, inventory=[], equipment=default_equipment, tags=[],abilities=[],modifiers=[], exp_value=0):
		Creature.__init__(self, name, race, combat_class, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)
		self.exp_value = exp_value

	def act(self):
		return "Base enemy has no AI"

	def die(self, killer=None):
		self.dead = True
		if killer:
			msg = "%s is killed by %s.\n"%(self.name, killer.name)
			if isinstance(killer, Player):
				killer.experience += self.exp_value
				msg += "%s earns %d experience.\n"%(killer.name, self.exp_value)

				drop_table = self.__class__.drop_table
				for item in list(drop_table.keys()):
					prob = int(drop_table[item])
					got_item = random.randint(0, 100) <= prob 
					if got_item:
						item = get_item_by_name(item, self.__class__.loot_coolity)
						killer.inventory.append(item)
						msg += "%s got loot: %s."%(killer.name.title(), item.name)
			return msg
		return "%s dies."%(self.name.title())

	@staticmethod
	def de_json(data):
		data["characteristics"] = json.loads(data["characteristics"])

		stats = None
		if "stats" in list(data.keys()):
			data["stats"] = json.loads(data["stats"])
			stats = data["stats"]
					
		for i in range(len(data["inventory"])):
			data["inventory"][i] = Item.de_json(data["inventory"][i])

		equipment = default_equipment.copy()
		eq = data["equipment"]
		for key in list(eq.keys()):
			if eq[key]:
				equipment[key] = Item.de_json(eq[key])
		data["equipment"] = equipment

		en =  Enemy(data.get("name"), data.get("race"), data.get("combat_class"), data.get("level"), data.get("characteristics"), stats, data.get("description"), inventory, equipment, data.get('tags'), [], [])
		return en

