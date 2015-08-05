#!/usr/bin/env python3
import json
from .items import *
from .util import *
from .modifiers import *
from .abilities import *
from .level_perks import *
from . import settings
import random
default_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how much energy you have, your position in turn qeue
	"intelligence": 5, #how likely you are to cause critical effects when attacking
}

default_equipment = {
	"armor": None,
	"primary_weapon": None,
	"secondary_weapon": None,
	"ring": None,
	"talisman": None,
	"headwear": None
}


class Creature(object):
	def __init__(self, name, level=1, characteristics = default_characteristics, stats=None, description=None, inventory=[], equipment=default_equipment, tags=[],abilities=[], modifiers = []):

		self.uid = get_uid()
		self.name = name
		self.description = description
		self.event = None
		self._level = level


		self.modifiers = modifiers.copy()
		self.base_characteristics = characteristics.copy()
		
		self.base_tags = tags.copy()
		self.base_abilities = abilities

		self.inventory = inventory.copy()
		self.equipment = equipment.copy()

		self.refresh_derived()
		self.dead = False

		

	def get_stats_from_characteristics(self, characteristics): #stats are completely derived from characteristics
		stats =  {
			"health": 0,
			"energy": 0,
			"max_health": 0,
			"max_energy": 0,
			"energy_regen": 0
		}

		stats["max_health"] = characteristics["vitality"]*10 + characteristics["vitality"]*self.level*4
		stats["max_energy"] = characteristics["dexterity"] + int(self.level / 10)
		stats["energy_regen"] = clamp(int(characteristics["dexterity"] / 3) + int(self.level / 10), 2, 10)
		stats["health"] = stats["max_health"]
		stats["energy"] = stats["max_energy"]
		return stats

	@property
	def short_desc(self):
	    return self.name+"(%d)"%(self.health)
	
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

	def get_accuracy(self, weapon = None):
		base_accuracy = diceroll( str(int(2*self.characteristics["intelligence"])) + "d" + str(2*self.characteristics["dexterity"] ))
		accuracy = base_accuracy
		for key in list(self.equipment.keys()):
			if key != "primary_weapon" and key != "secondary_weapon" and self.equipment[key] and "accuracy" in list(self.equipment[key].stats.keys()):
				accuracy += diceroll(self.equipment[key].stats["accuracy"])

		if weapon and "accuracy" in weapon.stats.keys():
			accuracy += diceroll(weapon.stats["accuracy"])

		for modifier in self.modifiers:
			if "accuracy" in modifier.stats_change.keys():
				accuracy += diceroll(modifier.stats_change["accuracy"])

		if hasattr(self, "level_perks"):
			for level_perk in self.level_perks:
				if "accuracy" in level_perk.stats_change.keys():
					accuracy += diceroll(level_perk.stats_change["accuracy"])

		#todo accuracy from level perks
		return clamp(accuracy, 0, 9999)

	@property
	def defence(self):
		base_def = diceroll("1d1")
		defence = base_def
		for key in list(self.equipment.keys()):
			if self.equipment[key] and "defence" in list(self.equipment[key].stats.keys()):
				defence += diceroll(self.equipment[key].stats["defence"])

		if hasattr(self, "level_perks"):
			for level_perk in self.level_perks:
				if "defence" in level_perk.stats_change.keys():
					defence += diceroll(level_perk.stats_change["defence"])

		for modifier in self.modifiers:
			if "defence" in modifier.stats_change:
				defence += diceroll(modifier.stats_change["defence"])

		#todo defence from level perks

		return clamp(defence, 0, 9999)

	@property
	def evasion(self):
		base_ev = diceroll(str(self.characteristics["dexterity"])+"d6")
		evasion = base_ev
		for key in list(self.equipment.keys()):
			if self.equipment[key] and "evasion" in list(self.equipment[key].stats.keys()):
				evasion += diceroll(self.equipment[key].stats["evasion"])

		if hasattr(self, "level_perks"):
			for level_perk in self.level_perks:
				if "defence" in level_perk.stats_change.keys():
					defence += diceroll(level_perk.stats_change["defence"])


		for modifier in self.modifiers:
			if "evasion" in modifier.stats_change:
				evasion += diceroll(modifier.stats_change["evasion"])

		#todo evasion from level perks
		return clamp(evasion, 0, 9999)


	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, value):
		self._level = value

	def damage(self, value):
		msg = ""
		if not self.dead:
			self.health = self.health - value
			msg += self.on_health_lost(value)

		killed = self.kill_if_nececary()
		return msg 

	def equip(self, target_item):
		if target_item.item_type == "consumable":
			return "Can't equip %s."%(target_item.name)

		if target_item.requirements:
			for key in list(target_item.requirements.keys()):
				if self.characteristics[key] < target_item.requirements[key]:
					return "%d %s required to use this item."%(target_item.requirements[key], key)

		if self.equipment[target_item.item_type] == target_item:
			return "Already equipped %s."%(target_item.name)

		if self.equipment[target_item.item_type]:
			temp = self.equipment[target_item.item_type]
			self.unequip(temp)


		self.equipment[target_item.item_type] = target_item
		for item in self.inventory:
			if item == target_item:
				self.inventory.remove(item)
		self.refresh_derived()
		self.sort_inventory()
		msg = self.on_item_equipped(target_item)
		return msg + "Succesfully equipped %s."%(target_item.name)

	def unequip(self, target_item):
		if target_item.item_type == "consumable":
			return "Can't unequip %s."%(target_item.name)
		if self.equipment[target_item.item_type] == target_item:
			self.equipment[target_item.item_type] = None
			self.inventory.append(target_item)
			self.sort_inventory()
			self.refresh_derived()
			msg = self.on_item_unequipped(target_item)
			return msg + "Succesfully unequipped %s."%(target_item.name)
		return "Not equipped!"

	def strip(self):
		for key in list(self.equipment.keys()):
			if self.equipment[key]:
				self.unequip(self.equipment[key])

	def destroy(self, target_item):
		if target_item in self.inventory:
			self.unequip(target_item)
			self.inventory.remove(target_item)
			self.sort_inventory()
			return "Succesfully destroyed %s."%(target_item.name)
		return "No such item."

	def clear_inventory(self):
		for item in self.inventory:
			self.destroy(item)

	def use(self, item):
		if item in self.inventory:
			use_effect = item.use(self)
			msg = self.on_consumable_used(item)
			self.sort_inventory()
			return use_effect + msg

	def add_modifier(self, modifier):
		for mod in self.modifiers:
			if mod.name == modifier.name and mod.granted_by == modifier.granted_by:
				return False
		self.modifiers.append(modifier)
		self.modifiers = sorted(self.modifiers, key=lambda x: x.priority, reverse=False)

	""" EVENTS """
	def on_combat_start(self):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_combat_start()
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_combat_start()
				if at_info:
					attack_info = at_info

		return msg

	def on_combat_over(self):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_combat_over()
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_combat_over()
				if at_info:
					attack_info = at_info

		self.energy = self.stats["max_energy"]
		return msg

	def on_round(self):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_round()
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_round()
				if at_info:
					attack_info = at_info


		if not self.dead:
			self.energy += self.stats["energy_regen"]
			msg += self.on_energy_gained(self.stats["energy_regen"])
		return msg

	def on_turn(self):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_turn()
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_turn()
				if at_info:
					attack_info = at_info

		return msg

	def on_modifier_applied(self, modifier):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_modifier_applied(modifier)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_modifier_applied(modifier)
				if at_info:
					attack_info = at_info

		self.refresh_characteristics()
		self.refresh_abilities()
		self.refresh_tags()

		return msg

	def on_modifier_lifted(self, modifier):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_modifier_lifted(modifier)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_modifier_lifted(modifier)
				if at_info:
					attack_info = at_info

		self.refresh_characteristics()
		self.refresh_abilities()
		self.refresh_tags()

		return msg

	def on_experience_gained(self, ability_info): #Immediately after gaining experience
		msg = ""
		for modifier in self.modifiers:
			ab_info = modifier.on_experience_gained(ability_info)
			if ab_info:
				ability_info = ab_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				ab_info = perk.on_experience_gained(ability_info)
				if ab_info:
					ability_info = ab_info

		return ability_info

	def on_item_equipped(self, item):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_item_equipped(item)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				ab_info = perk.on_item_equipped(item)
				if ab_info:
					ability_info = ab_info

		return msg

	def on_item_unequipped(self, item):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_item_unequipped(item)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				ab_info = perk.on_item_unequipped(item)
				if ab_info:
					ability_info = ab_info

		return msg

	def on_consumable_used(self, item):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_consumable_used(item)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				ab_info = perk.on_consumable_used(item)
				if ab_info:
					ability_info = ab_info
				
		return msg


	def on_health_lost(self, value):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_health_lost(value)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				effect = perk.on_health_lost(value)
				if effect:
					msg += effect

		return msg

	def on_health_gained(self, value):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_health_gained(value)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				effect = perk.on_health_gained(value)
				if effect:
					msg += effect

		return msg

	def on_energy_gained(self, value):
		#msg = "%s gains %d energy.\n"%(self.name.title(), value)
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_energy_gained(value)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				effect = perk.on_energy_gained(value)
				if effect:
					msg += effect

		return msg

	def on_level_up(self):
		#msg = "%s gains %d energy.\n"%(self.name.title(), value)
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_level_up()
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				effect = perk.on_level_up()
				if effect:
					msg += effect

		return msg

	def on_energy_lost(self, value):
		msg = ""
		for modifier in self.modifiers:
			effect = modifier.on_energy_lost(value)
			if effect:
				msg += effect

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				effect = perk.on_energy_lost(value)
				if effect:
					msg += effect

		return msg

	def on_attacked(self, attack_info): #immediately before attack is launched at self
		msg = ""
		for modifier in self.modifiers:
			at_info = modifier.on_attacked(attack_info)
			if at_info:
				attack_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_attacked(attack_info)
				if at_info:
					attack_info = at_info
		return attack_info

	def on_got_hit(self, attack_info): #attack in process of landing at self
		msg = ""
		if attack_info.use_info["damage_dealt"] > 0:
			attack_info.description += self.damage(attack_info.use_info["damage_dealt"])

		for modifier in self.modifiers:
			at_info = modifier.on_hit(attack_info)
			if at_info:
				attack_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_got_hit(attack_info)
				if at_info:
					attack_info = at_info

		if self.dead:
			attack_info.use_info["did_kill"] = True
			attack_info.description += "%s is killed by %s.\n"%(attack_info.target.name.title(), attack_info.inhibitor.name.title())
			attack_info = attack_info.inhibitor.on_kill(attack_info)
			attack_info = attack_info.target.on_death(attack_info)

		return attack_info

	def on_hit(self, attack_info): #immediately after succesfully hitting target
		for modifier in self.modifiers:
			at_info = modifier.on_hit(attack_info)
			if at_info:
				attack_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_hit(attack_info)
				if at_info:
					attack_info = at_info

		return attack_info

	def on_attack(self, attack_info): #immediately before attack is launched at target
		msg = ""
		for modifier in self.modifiers:
			at_info = modifier.on_attack(attack_info)
			if at_info:
				attack_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_attack(attack_info)
				if at_info:
					attack_info = at_info

		return attack_info

	def on_kill(self, attack_info):
		msg = ""
		for modifier in self.modifiers:
			at_info = modifier.on_kill(attack_info)
			if at_info:
				attack_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_kill(attack_info)
				if at_info:
					attack_info = at_info
		
		return attack_info

	def on_death(self, attack_info):
		msg = ""
		for modifier in self.modifiers:
			at_info = modifier.on_death(attack_info)
			if at_info:
				attack_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_death(attack_info)
				if at_info:
					attack_info = at_info

		return attack_info

	def on_miss(self, attack_info):
		msg = ""
		for modifier in self.modifiers:
			at_info = modifier.on_miss(attack_info)
			if at_info:
				attack_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_miss(attack_info)
				if at_info:
					attack_info = at_info

		return attack_info

	def on_buffed(self, ability_info):
		msg = ""
		for modifier in self.modifiers:
			at_info = modifier.on_buffed(ability_info)
			if at_info:
				ability_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_buffed(attack_info)
				if at_info:
					attack_info = at_info

		return ability_info

	def on_buff(self, ability_info):
		msg = ""
		for modifier in self.modifiers:
			at_info = modifier.on_buff(ability_info)
			if at_info:
				ability_info = at_info

		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				at_info = perk.on_buff(attack_info)
				if at_info:
					attack_info = at_info

		return ability_info


	""" /EVENTS """
	def kill_if_nececary(self):
		if self.health <= 0:
			self.die()
			return True
		return False

	def die(self):
		self.dead = True

	def examine_equipment(self):
		#desc = "%s's equipment:\n"%(self.name)
		desc = ""

		if self.primary_weapon:
			desc+="|\t%s: %s.\n"%("Primary weapon", self.primary_weapon.short_desc)
		if self.secondary_weapon:
			desc+="|\t%s: %s.\n"%("Secondary weapon", self.secondary_weapon.short_desc)
		if self.armor:
			desc+="|\t%s: %s.\n"%("Armor", self.armor.short_desc)
		if self.headwear:
			desc+="|\t%s: %s.\n"%("Headwear", self.headwear.short_desc)
		if self.ring:
			desc+="|\t%s: %s.\n"%("Ring", self.ring.short_desc)
		if self.talisman:
			desc+="|\t%s: %s.\n"%("Talisman", self.talisman.short_desc)

		return desc

	def sort_inventory(self):
		inv = {
			"primary_weapon" :[],
			"secondary_weapon" :[],
			"armor" :[],
			"headwear" :[],
			"talisman" :[],
			"ring" :[],
			"consumable" :[],
		}
		for item in self.inventory:
			inv[item.item_type].append(item)

		for key in list(inv.keys()):
			inv[key] = sorted(inv[key], key=lambda item: item.name)

		self.inventory = inv["primary_weapon"] + inv["secondary_weapon"] + inv["armor"] + inv["headwear"] + inv["talisman"] + inv["ring"] + inv["consumable"]

	def examine_inventory(self):
		#desc = "%s's inventory:\n"%(self.name)
		self.sort_inventory()
		desc = ""
		items = []
		for i in range(len(self.inventory)):
			item = self.inventory[i]
			if item:
				items.append(str(i+1)+"."+item.short_desc)
		return desc + ', '.join(items)

	def refresh_tags(self):
		self.tags = self.base_tags.copy()
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for tag in perk.__class__.tags_granted:
					self.tags.append(tag)

		for modifier in self.modifiers:
			for tag in modifier.tags_granted:
				self.tags.append(tag)

		for key in list(self.equipment.keys()):
			if self.equipment[key]:
				for tag in self.equipment[key].tags_granted:
					self.tags.append(tag)

	def refresh_modifiers(self):
		self.modifiers = []
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for modifier in perk.__class__.modifiers_granted:
					modifier_object = get_modifier_by_name( modifier["name"], perk, self, modifier["params"] )
					modifier_object.apply()

		for key in self.equipment.keys():
			if self.equipment[key]:
				for modifier in self.equipment[key].modifiers_granted:
					modifier_object = get_modifier_by_name( modifier["name"], self.equipment[key], self, modifier["params"] )
					modifier_object.apply()

	def refresh_abilities(self):
		self.abilities = self.base_abilities.copy()
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for ability in perk.__class__.abilities_granted:
					prototype = abilities[ability]
					self.abilities.append(prototype(ability, perk))

		for modifier in self.modifiers:
			for ability in modifier.abilities_granted:
				prototype = abilities[ability]
				self.abilities.append(prototype(ability, modifier))

		for key in self.equipment.keys():
			if self.equipment[key]:
				for ability in self.equipment[key].abilities_granted:
					prototype = abilities[ability]
					self.abilities.append(prototype(ability, self.equipment[key]))

	def refresh_characteristics(self):
		self.characteristics = self.base_characteristics.copy()
		#refresh characteristics
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for characteristic in list(perk.__class__.characteristics_change.keys()):
					self.characteristics[characteristic] = clamp( self.characteristics[characteristic] + perk.__class__.characteristics_change[characteristic], 1, 20)

		for modifier in self.modifiers:
			for characteristic in list(modifier.characteristics_change.keys()):
					self.characteristics[characteristic] = clamp ( self.characteristics[characteristic] +modifier.characteristics_change[characteristic], 1, 20)
		
		for item in list(self.equipment.keys()):
			if self.equipment[item] and "characteristics_change" in list(self.equipment[item].stats.keys()):
				for characteristic in list(self.equipment[item].stats["characteristics_change"].keys()):
					self.characteristics[characteristic] = clamp ( self.characteristics[characteristic] + self.equipment[item].stats["characteristics_change"][characteristic], 1, 20)

		
	def refresh_stats(self):
		self.stats = self.get_stats_from_characteristics(self.characteristics)
		#refresh stats
		if hasattr(self, "level_perks"):
			for perk in self.level_perks:
				for stat in list(perk.__class__.stats_change.keys()):
					self.stats[stat] = clamp( self.stats[stat]+ perk.__class__.stats_change[stat], 0, 9999)

		for modifier in self.modifiers:
			for stat in list(modifier.stats_change.keys()):
				if stat != "defence" and stat != "evasion":
					self.stats[stat] = clamp( self.stats[stat] + modifier.stats_change[stat], 0, 9999)
		
		for item in list(self.equipment.keys()):
			if self.equipment[item] and "stats_change" in list(self.equipment[item].stats.keys()):
				for stat in list(self.equipment[item].stats["stats_change"].keys()):
					if stat != "defence" and stat != "evasion":
						self.stats[stat] = clamp( self.stats[stat] +self.equipment[item].stats["stats_change"][stat], 0, 9999)

	def refresh_derived(self):
		self.refresh_modifiers()
		self.refresh_abilities()
		self.refresh_tags()
		self.refresh_characteristics()
		self.refresh_stats()

	def examine_self(self):

		characteristics = []
		characteristics.append("|\t"+"Strength"+":" +str(self.characteristics["strength"]) +" ("+str(self.base_characteristics["strength"])+")" +"\n")
		characteristics.append("|\t"+"Dexterity"+":" +str(self.characteristics["dexterity"]) +" ("+str(self.base_characteristics["dexterity"])+")" +"\n")
		characteristics.append("|\t"+"Vitality"+":" +str(self.characteristics["vitality"]) +" ("+str(self.base_characteristics["vitality"])+")" +"\n")
		characteristics.append("|\t"+"Intelligence"+":" +str(self.characteristics["intelligence"]) +" ("+str(self.base_characteristics["intelligence"])+")" +"\n")
		
		avg_defence = sum([self.defence for x in range(501)])/500
		avg_evasion = sum([self.evasion for x in range(501)])/500
		avg_accuracy = sum([self.get_accuracy() for x in range(501)])/500

		desc = "\n".join(
		[
			"%s. lvl %d"%(self.name.title(), self.level),
			"%s"%(self.description or "----"),
			"Characteristics:\n%s"%("".join(characteristics)),
			"Health:\n|\t%d/%d"%(self.health, self.stats["max_health"]),
			"Energy:\n|\t%d/%d, regen per turn: %d"%(self.energy, self.stats["max_energy"],self.stats["energy_regen"]) + "\nExp:\n|\t%d/%d"%(self.experience, self.max_experience) if hasattr(self, "experience") else "",
			"Average defence, evasion:\n|\t%d, %d"%(avg_defence, avg_evasion),
			"Average accuracy:\n|\t%d"%(avg_accuracy),
			"Tags:\n|\t%s"%(", ".join(self.tags)),
			"Modifiers:\n|\t%s"%(", ".join(["%s(%s)"%(modifier.name, modifier.granted_by.name) for modifier in self.modifiers])),
			"Abilities:\n|\t%s"%(", ".join(["%s(%s)"%(abiility.name, abiility.granted_by.name) for abiility in self.abilities])),
			"Equipment:\n%s"%(self.examine_equipment()),
		])
		return desc

	def to_json(self):
		big_dict = self.__dict__.copy()
		del big_dict["uid"]
		big_dict["characteristics"] = self.base_characteristics.copy()
		# big_dict["tags"] = json.dumps(self.tags)
		big_dict["tags"] = self.base_tags
		del big_dict["base_tags"]
		del big_dict["abilities"] #abilities are not serializable
		del big_dict["modifiers"] #modifiers are derived so no point in serializing them
		big_dict["inventory"] = []
		for item in self.inventory:
			big_dict["inventory"].append(item.to_json())
		big_dict["equipment"] = default_equipment.copy()
		for key in self.equipment:
			if self.equipment[key]:
				big_dict["equipment"][key] = self.equipment[key].to_json()

		big_dict["level_perks"] = []
		for perk in self.level_perks:
			big_dict["level_perks"].append(perk.__class__.name)

		#big_dict["equipment"] = json.dumps(big_dict["equipment"])
		return big_dict

class Player(Creature):
	def __init__(self, userid, name, level=1, characteristics = default_characteristics, stats=None, description=None, inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "human"],abilities=[],modifiers=[], level_perks=[], experience=0, level_up_points=0, perk_points=0):
		self.level_perks = level_perks.copy()
		self._experience = experience
		self.level_up_points = level_up_points
		self.perk_points = perk_points
		self.userid = userid

		Creature.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)

	@property
	def experience(self):
		return self._experience

	@experience.setter
	def experience(self, value):
		if value >= self.max_experience:
			over_cur_level = value - self.max_experience
			self.level_up()
			self.experience = over_cur_level
		else:
			self._experience = value

	@property
	def max_experience(self):
	    return max_exp_for_level(self.level)
	
	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, value):
		self._level = value

	def add_experience(self, value):
		cur_level = self.level
		self.experience += value
		if self.level > cur_level:
			return "%s has leveled up to level %d!\n"%(self.name.title(), self.level)
		return ""

	def fits_perk_requirements(self, perk_requirements):
		own_perk_names= [perk.__class__.name for perk in self.level_perks]

		if perk_requirements["level"] > self.level:
			return False
		for perk in perk_requirements["has_perks"]:
			if not perk.__class__.name in own_perk_names:
				return False
		for characteristic in list(perk_requirements["characteristics"].keys()):
			if self.characteristics[characteristic] < perk_requirements["characteristics"][characteristic]:
				return False
		return True

	def examine_self(self):
		desc = super(Player, self).examine_self()
		desc += "Level perks:\n|\t%s"%(", ".join([perk.__class__.name for perk in self.level_perks]))
		return desc

	def level_up(self):
		self.level = self.level + 1
		self.level_up_points += ( int(self.level % 5) == 0 ) * 1 
		self.perk_points += ( int(self.level % 3) == 0 ) * 1 
		msg = self.on_level_up()
		return msg

	@staticmethod
	def de_json(data):
		if isinstance(data, str):
			data = json.loads(data)
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

		ply = Player(data.get("userid"), data.get("name"), data.get("_level"), data.get("characteristics"), stats, data.get("description"), data.get("inventory"), data.get("equipment"), data.get('tags'), [], [], [], data.get("_experience"), data.get("level_up_points"), data.get("perk_points"))
		level_perks = [level_perks_listing[name](ply) for name in data["level_perks"]]
		ply.level_perks = level_perks
		ply.refresh_derived()
		return ply

	def on_kill(self, attack_info):
		target = attack_info.target
		if isinstance(target, Enemy):
			attack_info.use_info["experience_gained"] = target.exp_value
			attack_info.description += "%s earns %d experience.\n"%(attack_info.inhibitor.name, target.exp_value)
			attack_info = attack_info.inhibitor.on_experience_gained(attack_info)
			drop_table = target.__class__.drop_table
			for item in list(drop_table.keys()):
				prob = int(int(drop_table[item]) * settings.loot_probability_multiplier)
				got_item = random.randint(0, 100) <= prob 
				if got_item:
					item = get_item_by_name(item, target.__class__.loot_coolity)
					attack_info.use_info["loot_dropped"].append(item)
					if isinstance(attack_info.inhibitor, Player):
						attack_info.inhibitor.inventory.append(item)
					attack_info.use_info["loot_dropped"].append(item)
					attack_info.description += "%s got loot: %s.\n"%(attack_info.inhibitor.name.title(), item.name)
		return super(Player, self).on_kill(attack_info)
			
	def to_json(self):
		big_dict = super(Player, self).to_json()
		big_dict["userid"] = self.userid
		big_dict["event"] = None
		return big_dict

	def __str__(self):
		return self.examine_self()

class Enemy(Creature):

	loot_coolity = 0

	drop_table = {

	}

	def __init__(self, name, level=1, characteristics = default_characteristics, stats=None, description=None, inventory=[], equipment=default_equipment, tags=[],abilities=[],modifiers=[], exp_value=0):
		Creature.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)
		self.target = None
		self.exp_value = exp_value

	def select_target(self, combat_event):
		self.target = random.choice([x for x in combat_event.turn_qeue if isinstance(x, Player)])

	def act(self):
		return "Base enemy has no AI"

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

		en =  Enemy(data.get("name"), data.get("level"), data.get("characteristics"), stats, data.get("description"), inventory, equipment, data.get('tags'), [], [])
		return en

