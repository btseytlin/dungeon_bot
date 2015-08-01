from util import clamp, diceroll
import random
from modifiers import *

"""
Tags:
	animate - Marks objects that are living biological creatures. For example gargolyes are not animate, golems are not animate.
	inaminate - self explanatory
	humanoid - Marks objects that have humanoid traits. Most sentinent creatures are humanoid.
	small - Small targets, harder to hit
	big - Big targets, easier to hit
	
	armor - Armored, takes less damage
	heavy armor - Heavy armored, takes little damage
	quick - Harder to hit and dodge
	slow - Easier to hit and dodge
	physical ressitant - Resistant to physical damage
	magic ressitant - Resistant to magic damage

	undead - Undead creatures
	animal - Animal creatures
	rodent - Rat creatures and similar
	demon - Demon creatures 


"""

class AbilityUseInfo(object):
	def __init__(self, inhibitor, ability_type, prototype_class, target, combat_event=None):
		self.ability_type = ability_type
		self.prototype_class = prototype_class
		self.inhibitor = inhibitor
		self.target = target
		self.combat_event = combat_event

	def execute(self):	
		use_info = self.use_info	
		self.inhibitor.energy = self.inhibitor.energy + use_info["energy_change"]		
		if use_info["energy_change"] > 0:
			self.description += self.inhibitor.on_energy_gained(use_info["energy_change"])
		else:
			self.description += self.inhibitor.on_energy_lost(use_info["energy_change"])

		for modifier in use_info["modifiers_applied"]:
			self.description += modifier.apply() 
		if self.ability_type == "attack":
			self = self.inhibitor.on_attack(self)
			self = self.target.on_attacked(self)
			if random.randint(0, 100) > use_info["hit_chance"]:
				self.description += self.prototype_class.get_miss_description(self) 
				self = self.inhibitor.on_miss(self)
			else:
				use_info["did_hit"] = True
				use_info["damage_dealt"] = self.prototype_class.get_damage(self.inhibitor, self.target, use_info["item_used"])
				self.description += self.prototype_class.get_hit_description(self)
				self = self.inhibitor.on_hit(self)
				self = self.target.on_got_hit(self)

		if self.ability_type == "buff":
			self = self.inhibitor.on_buff(self)
			self = self.inhibitor.on_buffed(self)
		if self.use_info["experience_gained"] > 0:
			self.inhibitor.experience += use_info["experience_gained"]
		return self

	def __str__(self):
		inhibitor = self.inhibitor.name
		if hasattr(self.inhibitor, "username"):
			inhibitor = inhibitor + "(%s)"%(self.inhibitor.username)
		else:
			inhibitor = inhibitor + "(%s)"%(self.inhibitor.uid)

		target = self.target.name
		if hasattr(self.target, "username"):
			target = target + "(%s)"%(self.target.username)
		else:
			target = target + "(%s)"%(self.target.uid)

		msg_lines = []
		msg_lines.append("Inhibitor %s uses %s(%s) of item %s on target %s."%(inhibitor, self.ability_type, self.prototype_class, self.use_info["item_used"].name, target))
		msg_lines.append("Energy change: %d"%(self.use_info["energy_change"]))
		if self.ability_type == "attack":
			msg_lines.append("Hit chance: %d"%(self.use_info["hit_chance"]))
			msg_lines.append("Damage: %d"%(self.use_info["damage_dealt"]))
			msg_lines.append("Did hit, did kill: %s, %s."%(self.use_info['did_hit'], self.use_info['did_kill']))
			msg_lines.append("Loot loot_dropped: %s"%( ", ".join([item.name for item in self.use_info["loot_dropped"] ]) ) )
			msg_lines.append("Exp gained: %d"%( self.use_info["experience_gained"] ) )

		msg_lines.append("Modifiers applied: %s"%( ", ".join([modifier.name for modifier in self.use_info["modifiers_applied"] ]) ) )
		return "  \n".join(msg_lines)

class AttackInfo(AbilityUseInfo):
	def __init__(self, inhibitor, ability_type, prototype_class, target, combat_event=None, use_info=None, description = "", ):
		AbilityUseInfo.__init__(self, inhibitor, ability_type, prototype_class, target, combat_event)
		self.description = description

		if not use_info:
			use_info = {
				"hit_chance" : 0,
				"damage_dealt" : 0,
				"experience_gained" : 0,
				"did_hit" : False,
				"did_kill" : False,
				"item_used": None,
				"energy_change": 0,
				"modifiers_applied": [],
				"loot_dropped": []
			}
		self.use_info = use_info

class BuffInfo(AbilityUseInfo):
	def __init__(self, inhibitor, ability_type, prototype_class, target, combat_event=None, use_info=None, description="" ):
		AbilityUseInfo.__init__(self, inhibitor, ability_type, prototype_class, target, combat_event)
		self.description = description

		if not use_info:
			use_info = {
				"hp_change" : 0,
				"energy_change" : 0,
				"experience_gained" : 0,
				"item_used": None,
				"modifiers_applied": []
			}
		self.use_info = use_info

class Ability(object):
	def __init__(self, name, granted_by):
		self.name = name
		self.granted_by = granted_by

	@staticmethod
	def use(use_info):
		if use_info.ability_type == "attack":
			use_info.use_info["hit_chance"] = use_info.prototype_class.get_chance_to_hit(use_info.inhibitor, use_info.target, use_info.use_info["item_used"])
		#	if random.randint(0, 100) > use_info.use_info["hit_chance"]:
				#use_info.description += use_info.prototype_class.get_miss_description(use_info) 
			#else:
			#	use_info.use_info["did_hit"] = True
			#use_info.use_info["damage_dealt"] = use_info.prototype_class.get_damage(use_info.inhibitor, use_info.target, use_info.use_info["item_used"])
				#use_info.description += use_info.prototype_class.get_hit_description(use_info)
		else:
			modifiers = use_info.prototype_class.get_buff_modifiers(use_info)
			use_info.use_info["modifiers_applied"] += modifiers
			use_info.description += use_info.prototype_class.get_buff_description(use_info)

		use_info.use_info["energy_change"] = -use_info.prototype_class.energy_required
		use_info = use_info.execute()
		return use_info

	@staticmethod
	def can_use(user, ability_class):
		if ability_class.requirements:
			for key in list(ability_class.requirements.keys()):
				if user.characteristics[key] < ability_class.requirements[key]:
					return False, "%d %s required to use this ability."%(ability_class.requirements[key], key)

		if user.energy < ability_class.energy_required:
			return False, "Not enough energy. Need %d energy to use."%(ability_class.energy_required - user.energy)
		return True, ""


	@staticmethod
	def get_miss_description(attack_info):
		return "%s uses ability %s with %s on %s, but misses.\n"%(attack_info.inhibitor.name.title(),attack_info.prototype_class.__name__, attack_info.use_info['item_used'].name, attack_info.target.name)

	@staticmethod
	def get_hit_description(attack_info):
		return "%s uses ability %s with %s and deals %d damage to %s.\n"%(attack_info.inhibitor.name.title(),attack_info.prototype_class.__name__, attack_info.use_info['item_used'].name, attack_info.use_info["damage_dealt"], attack_info.target.name.title())

class Smash(Ability):

	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength - defence - is_armored * defence * 2 - is_heavy_armored * defence * 3

	avg chance to hit = 45

	avg dmg = 15

	chance to cause "knockdown" = ?

	chance to cause "concussion" = ?

	"""
	name = "smash"
	description = "Smash your weapon and hope you hit something!"
	energy_required = 2
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user, Smash)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_miss_description(attack_info):
		return "%s smashes %s at %s but misses.\n"%(attack_info.inhibitor.name.title(), attack_info.use_info['item_used'].name, attack_info.target.name)

	@staticmethod
	def get_hit_description(attack_info):
		return "%s smashes %s and deals %d damage to %s.\n"%(attack_info.inhibitor.name.title(), attack_info.use_info['item_used'].name, attack_info.use_info["damage_dealt"], attack_info.target.name.title())

	@staticmethod
	def get_damage(user, target, weapon):

		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence
		is_armored = int("armor" in target.tags) * 0.2
		is_heavy_armored = int("heavy armor" in target.tags) * 0.4

		dmg = clamp( weapon_dmg * strength - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*2
		is_slow = int("slow" in target.tags)*2
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", Smash, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class Stab(Ability):

	"""
	Stabbing attack for swords, daggers, rapiers, pikes, anything pointy. 
	Effective against unarmoed oponents, very ineffective against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength + not_armored * 0.3 *(weapon_dmg * strength) - defence * 1.5 - is_armored * defence * 3 - is_heavy_armored * defence * 4

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	chance to cause "pain" = ?

	"""
	name = "stab"
	description = "Stab in the gut!"
	energy_required = 2
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user, Stab)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence * 1.5
		is_armored = int("armor" in target.tags) * 0.5
		is_heavy_armored = int("heavy armor" in target.tags) * 0.8
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * strength + not_armored * 0.3 *(weapon_dmg * strength) - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", Stab, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class QuickStab(Ability):

	"""
	Exactly like stab, except takes less energy and suffers more penalties for armored opoentns.
	Stabbing attack for small pointy weapons like daggers.
	Effective against unarmoed oponents, very ineffective against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity * 1.5 - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength + not_armored * 0.3 *(weapon_dmg * strength) - defence * 1.5 - is_armored * defence * 3 - is_heavy_armored * defence * 4

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	chance to cause "pain" = ?

	above average dex required to use 

	"""
	name = "quickstab"
	description = "Quick stab in the gut!"
	energy_required = 2
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user, QuickStab)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence * 1.5
		is_armored = int("armor" in target.tags) * 0.6
		is_heavy_armored = int("heavy armor" in target.tags) * 0.9
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * strength + not_armored * 0.2 *(weapon_dmg * strength) - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", QuickStab, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class Cut(Ability): #TODO test and adapt

	"""
	Cutting attack for swords, daggers, anything bladed.
	Effective against unarmoed oponents, mediocore against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity  - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength - defence * 1.5 - is_armored * defence * 2 - is_heavy_armored * defence * 3

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	chance to cause "pain" = ?

	"""
	name = "cut"
	description = "Cut em up!"
	energy_required = 2
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user, Cut)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence
		is_armored = int("armor" in target.tags) * 0.4
		is_heavy_armored = int("heavy armor" in target.tags) * 0.7
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * strength + not_armored * 0.1 *(weapon_dmg * strength) - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"]) * 1.5
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", Cut, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class QuickCut(Ability): #TODO test and adapt

	"""
	Exactly like cut, except takes less energy and suffers more penalties for armored opoentns.
	Cutting attack for small bladed weapons, like daggers.
	Effective against unarmoed oponents, weak against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity  - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength - defence - is_armored * defence * 3 - is_heavy_armored * defence * 4

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	chance to cause "pain" = ?

	above average dex required to use 

	"""
	name = "quickcut"
	description = "Cut em up!"
	energy_required = 2
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user, QuickCut)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence
		is_armored = int("armor" in target.tags) * 0.6
		is_heavy_armored = int("heavy armor" in target.tags) * 0.9
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * strength + not_armored * 0.1 *(weapon_dmg * strength) - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", QuickCut, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class ShieldUp(Ability): #TODO test and adapt

	"""
	Raise the shield to protect yourself, gain a defence bonus and a pennalty to evasion for one turn.

	defence_gained = ?
	evasion_lost = ?

	"""
	name = "shieldup"
	description = "Hide behind your steel."
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		return Ability.can_use(user, ShieldUp)

	@staticmethod
	def get_buff_modifiers(use_info):
		defence_bonus = use_info.use_info["item_used"].stats["defence"]
		modifier_params = {"stats_change": {"defence":defence_bonus}}
		modifier = get_modifier_by_name("shielded", use_info.use_info["item_used"], use_info.target, modifier_params)
		return [modifier]

	@staticmethod
	def get_buff_description(use_info):
		return "%s put his shieldup and gained a defence bonus.\n"%(use_info.inhibitor.name.title())

	@staticmethod
	def use(user, target=None, weapon=None):
		target = user
		buff_info = AttackInfo(user, "buff", ShieldUp, target, combat_event)
		buff_info.use_info["item_used"] = weapon
		return Ability.use(buff_info)

""" Enemy abilities below """
class RodentBite(Ability):
	name = "rodent bite"
	description = "Rodents bite!"
	energy_required = 1
	requirements = None


	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion - is_quick * target_evasion

	dmg = base_damage * strength - defence - is_armored * defence * 3 - is_heavy_armored * defence * 5

	avg chance to hit = 55

	avg damage = 5

	chance to cause "poisoned" = ?

	chance to cause "bleeding" = ?

	"""

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_damage = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence
		is_armored = int("armor" in target.tags) * 0.5
		is_heavy_armored = int("heavy armor" in target.tags) * 0.8

		dmg = clamp( weapon_damage* strength - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		accuracy = diceroll(weapon.stats["accuracy"])
		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp( accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required."
		if not target.dead:
			return Ability.can_use(user, RodentBite)
		else:
			return False, "Target is already dead"

	@staticmethod
	def get_miss_description(attack_info):
		return "%s tries to bite %s but misses.\n"%(attack_info.inhibitor.name.title(), attack_info.target.name.title())

	@staticmethod
	def get_hit_description(attack_info):
		return "%s bites %s and deals %d damage.\n"%(attack_info.inhibitor.name.title(), attack_info.target.name.title(), attack_info.use_info["damage_dealt"])

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", RodentBite, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)


class AnimalBite(Ability):
	name = "animal bite"
	description = "Animals bite, bad!"
	energy_required = 2
	requirements = None
	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion - is_quick * target_evasion
	dmg = base_damage * strength - defence - is_armored * defence * 2 - is_heavy_armored * defence * 3
	avg chance to hit = 55
	avg damage = 5
	chance to cause "injured" = ?
	chance to cause "bleeding" = ?
	"""
	@staticmethod
	def get_damage(user, target, weapon):
		weapon_damage = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence
		is_armored = int("armor" in target.tags) * 0.4
		is_heavy_armored = int("heavy armor" in target.tags) * 0.8

		dmg = clamp( weapon_damage* strength - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		accuracy = diceroll(weapon.stats["accuracy"])
		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp( accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required."
		if not target.dead:
			return Ability.can_use(user, AnimalBite)
		else:
			return False, "Target is already dead"

	@staticmethod
	def get_miss_description(attack_info):
		return "%s tries to bite %s but misses.\n"%(attack_info.inhibitor.name.title(), attack_info.target.name.title())

	@staticmethod
	def get_hit_description(attack_info):
		return "%s bites %s and deals %d damage.\n"%(attack_info.inhibitor.name.title(), attack_info.target.name.title(), attack_info.use_info["damage_dealt"])

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", AnimalBite, target)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class AnimalClaw(Ability):
	name = "animal claw"
	description = "Animals claw, bad!"
	energy_required = 2
	requirements = None
	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion - is_quick * target_evasion
	dmg = base_damage * strength - defence - is_armored * defence * 4 - is_heavy_armored * defence * 5
	avg chance to hit = 55
	avg damage = 5
	chance to cause "injured" = ?
	chance to cause "bleeding" = ?
	"""
	@staticmethod
	def get_damage(user, target, weapon):
		weapon_damage = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defence = target.defence
		is_armored = int("armor" in target.tags) * 0.2
		is_heavy_armored = int("heavy armor" in target.tags) * 0.5

		dmg = clamp( weapon_damage* strength - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		accuracy = diceroll(weapon.stats["accuracy"])
		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp( accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required."
		if not target.dead:
			return Ability.can_use(user, AnimalClaw)
		else:
			return False, "Target is already dead"

	@staticmethod
	def get_miss_description(attack_info):
		return "%s tries to claw %s but misses.\n"%(attack_info.inhibitor.name.title(), attack_info.target.name.title())

	@staticmethod
	def get_hit_description(attack_info):
		return "%s claws %s and deals %d damage.\n"%(attack_info.inhibitor.name.title(), attack_info.target.name.title(), attack_info.use_info["damage_dealt"])

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, "attack", AnimalClaw, target)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

abilities = {
	"smash": Smash,
	"shieldup": ShieldUp,
	"cut": Cut,
	"stab": Stab,
	"quickcut": QuickCut,
	"quickstab": QuickStab,

	# animal abilities below
	"rodent bite": RodentBite,
	"animal bite": AnimalBite,
	"animal claw": AnimalClaw,
}
