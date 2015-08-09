#!/usr/bin/env python3
from .util import clamp, diceroll
import random
from .modifiers import *

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
	fire resistant - self explanatory
	electricity resistant - self explanatory
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

		if self.ability_type == "aoe_attack":
			#self = self.inhibitor.on_attack(self)
			#print(self.targets)
			for i in range(len(self.targets)):
				target = self.targets[i]
				attack_info = AttackInfo(self.inhibitor, self.prototype_class, target, self.combat_event)
				attack_info.use_info["item_used"] = self.use_info["item_used"]
				#print(i, self.use_info["damage_multipliers"])
				attack_info.use_info["damage_multiplier"] = self.use_info["damage_multipliers"][i]
				attack_info.use_info["hit_chance"] = self.use_info["hit_chances"][i]
				attack_info = attack_info.execute()
				self.attack_infos.append(attack_info)

			self.description += "\n".join([x.description for x in self.attack_infos])
		if self.ability_type == "attack":
			self = self.inhibitor.on_attack(self)
			self = self.target.on_attacked(self)
			if random.randint(1, 100) > use_info["hit_chance"]:
				self.description += self.prototype_class.get_miss_description(self) 
				self = self.inhibitor.on_miss(self)
			else:
				use_info["did_hit"] = True
				use_info["damage_dealt"] = self.prototype_class.get_damage(self.inhibitor, self.target, use_info["item_used"]) * use_info["damage_multiplier"]
				self.description += self.prototype_class.get_hit_description(self)
				self = self.inhibitor.on_hit(self)
				self = self.target.on_got_hit(self)

				for modifier in self.prototype_class.get_modifiers_applied(self):
					use_info["modifiers_applied"].append(modifier)

		if self.ability_type == "buff":
			self = self.inhibitor.on_buff(self)
			self = self.inhibitor.on_buffed(self)

		if "modifiers_applied" in self.use_info.keys():
			for modifier in use_info["modifiers_applied"]:
				self.description += modifier.apply() 

		#if "experience_gained" in use_info and use_info["experience_gained"] > 0:
		#	if not hasattr(self.inhibitor, "exp_value"):
		#		msg, value = self.inhibitor.on_experience_gain( use_info["experience_gained"] ) 
		#		self.description += msg
		#		self.description += self.inhibitor.add_experience(value)
		return self

	def __str__(self):
		inhibitor = self.inhibitor.name
		if hasattr(self.inhibitor, "userid"):
			inhibitor = inhibitor + "(%s)"%(self.inhibitor.userid)
		else:
			inhibitor = inhibitor + "(%s)"%(self.inhibitor.uid)

		target = self.target.name
		if hasattr(self.target, "userid"):
			target = target + "(%s)"%(self.target.userid)
		else:
			target = target + "(%s)"%(self.target.uid)

		msg_lines = []
		msg_lines.append("Inhibitor %s uses %s(%s) of item %s on target %s."%(inhibitor, self.ability_type, self.prototype_class, self.use_info["item_used"].name if self.use_info["item_used"] else str(None), target))
		msg_lines.append("Energy change: %d"%(self.use_info["energy_change"]))
		if self.ability_type == "aoe_attack":
			msg = "AOE attack %s by %s."%(self.prototype_class.name, self.inhibitor.name)
			return msg + "\n".join([str(attack) for attack in self.attack_infos])
		if self.ability_type == "attack":
			msg_lines.append("Hit chance: %d"%(self.use_info["hit_chance"]))
			msg_lines.append("Damage: %d"%(self.use_info["damage_dealt"]))
			msg_lines.append("Did hit, did kill: %s, %s."%(self.use_info['did_hit'], self.use_info['did_kill']))
			msg_lines.append("Loot loot_dropped: %s"%( ", ".join([item.name for item in self.use_info["loot_dropped"] ]) ) )
			msg_lines.append("Exp gained: %d"%( self.use_info["experience_gained"] ) )
		if "modifiers_applied" in self.use_info.keys():
			msg_lines.append("Modifiers applied: %s"%( ", ".join([modifier.name for modifier in self.use_info["modifiers_applied"] ]) ) )
		return "  \n".join(msg_lines)

class AttackInfo(AbilityUseInfo):
	def __init__(self, inhibitor, prototype_class, target, combat_event=None, use_info=None, description = "", ):
		AbilityUseInfo.__init__(self, inhibitor, "attack", prototype_class, target, combat_event)
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
				"loot_dropped": [],
				"damage_multiplier": 1
			}
		self.use_info = use_info

class AoeAttackInfo(AbilityUseInfo):
	def __init__(self, inhibitor,  prototype_class, target, combat_event=None, use_info=None, description = "", ):
		AbilityUseInfo.__init__(self, inhibitor, "aoe_attack", prototype_class, target, combat_event)
		self.targets = [target]
		max_targets = 5
		for i in range(max_targets):
			cr = None
			if hasattr(inhibitor, "exp_value"):
				cr = random.choice([ c for c in combat_event.turn_queue if not c.dead and not hasattr(c, "exp_value")])
			else:
				cr = random.choice([ c for c in combat_event.turn_queue if not c.dead and hasattr(c, "exp_value")])

			if cr and not cr in self.targets:
				self.targets.append( cr )

		self.description = description
		self.attack_infos = []
		if not use_info:
			use_info = {
				"energy_change": 0,
				"hit_chances": [],
				"item_used": None,
				"damage_multipliers": []
			}
		self.use_info = use_info

class BuffInfo(AbilityUseInfo):
	def __init__(self, inhibitor,  prototype_class, target, combat_event=None, use_info=None, description="" ):
		AbilityUseInfo.__init__(self, inhibitor, "buff", prototype_class, target, combat_event)
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
	def get_modifiers_applied(use_info):
		return []

	@staticmethod
	def use(use_info):
		if use_info.ability_type == "aoe_attack":
			use_info.use_info["hit_chances"] = [ clamp( use_info.prototype_class.get_chance_to_hit(use_info.inhibitor, use_info.targets[x], use_info.use_info["item_used"]), 5, int(95/(x+1))) for x in range(len(use_info.targets)) ]

			for x in range(len(use_info.targets)):
				use_info.use_info["damage_multipliers"].append(clamp(1 - 0.25*(x), 0.25, 1))

		elif use_info.ability_type == "attack":
			use_info.use_info["hit_chance"] = clamp( use_info.prototype_class.get_chance_to_hit(use_info.inhibitor, use_info.target, use_info.use_info["item_used"]), 5, 95)

		#	if random.randint(1, 100) > use_info.use_info["hit_chance"]:
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
			return False, "Not enough energy. Need %d more energy to use."%(ability_class.energy_required - user.energy)
		return True, ""


	@staticmethod
	def get_miss_description(attack_info):
		return "%s uses %s on %s with the %s, but misses.\n"%(attack_info.inhibitor.short_desc.capitalize(),attack_info.prototype_class.__name__, attack_info.target.short_desc.capitalize(), attack_info.use_info['item_used'].name)

	@staticmethod
	def get_hit_description(attack_info):
		return "%s uses %s on %s with the %s for %d damage.\n"%(attack_info.inhibitor.short_desc.capitalize(),attack_info.prototype_class.__name__, attack_info.target.short_desc.capitalize(), attack_info.use_info['item_used'].name, attack_info.use_info["damage_dealt"] )



class Smash(Ability):

	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength - is_armored * defense * 2 - is_heavy_armored * defense * 3

	avg chance to hit = 45

	avg dmg = 30

	chance to cause "knockdown" = intelligence*strength*dexterity - target_strength*target_dexterity-target_intelligence/2

	"""
	name = "smash"
	description = "Smash your weapon and hope you hit something!"
	energy_required = 2
	requirements = None
	requires_target = "enemy"

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not hasattr(target, "exp_value"):
			return False, "Can't attack a player."
		if not target.dead:
			return Ability.can_use(user, Smash)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_miss_description(attack_info):
		return "%s swings %s at %s but misses.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.use_info['item_used'].name, attack_info.target.short_desc)

	@staticmethod
	def get_hit_description(attack_info):
		return "%s swings %s and deals %d damage to %s.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.use_info['item_used'].name, attack_info.use_info["damage_dealt"], attack_info.target.short_desc.capitalize())

	@staticmethod
	def get_knockdown_chance(use_info):		
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["strength"] - use_info.target.characteristics["dexterity"]-use_info.target.characteristics["intelligence"]/2 + 5 * int("armor" in use_info.target.tags) + 10*("heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= Smash.get_knockdown_chance(use_info):
			modifier = get_modifier_by_name("knockdown", use_info.inhibitor, use_info.target)
			return [modifier]
		return []

	@staticmethod
	def get_damage(user, target, weapon):

		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense
		is_armored = int("armor" in target.tags) * 0.2
		is_heavy_armored = int("heavy armor" in target.tags) * 0.4
		dmg = clamp( weapon_dmg * strength , user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*2
		is_slow = int("slow" in target.tags)*2
		evasion = target.evasion
		accuracy = user.get_accuracy(weapon)
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user,  Smash, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class Stab(Ability):

	"""
	Stabbing attack for swords, daggers, rapiers, pikes, anything pointy. 
	Effective against unarmoed oponents, very ineffective against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength + not_armored * 0.3 *(weapon_dmg * strength)  * 1.5 - is_armored * defense * 3 - is_heavy_armored * defense * 4

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "pain" = ?

	"""
	name = "stab"
	description = "Stab in the gut!"
	energy_required = 2
	requirements = None
	requires_target = "enemy"

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not hasattr(target, "exp_value"):
			return False, "Can't attack a player."
		if not target.dead:
			return Ability.can_use(user, Stab)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense * 1.5
		is_armored = int("armor" in target.tags) * 0.5
		is_heavy_armored = int("heavy armor" in target.tags) * 0.8
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * strength + not_armored * 0.05 *(weapon_dmg * strength) , user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = user.get_accuracy(weapon)
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

		return chance_to_hit

	@staticmethod
	def get_pain_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"]-use_info.target.characteristics["intelligence"]/2 - 10 * int("armor" in use_info.target.tags or "heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= Stab.get_pain_chance(use_info):
			modifier = get_modifier_by_name("pain", use_info.inhibitor, use_info.target)
			return [modifier]
		return []

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user,  Stab, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class QuickStab(Ability):

	"""
	Exactly like stab, except takes less energy and suffers more penalties for armored opoentns.
	Stabbing attack for small pointy weapons like daggers.
	Effective against unarmoed oponents, very ineffective against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = ?

	dmg = ?

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	chance to cause "pain" = ?

	above average dex required to use 

	"""
	name = "quick stab"
	description = "Quick stab in the gut!"
	energy_required = 1
	requirements = None
	requires_target = "enemy"

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not hasattr(target, "exp_value"):
			return False, "Can't attack a player."
		if not target.dead:
			return Ability.can_use(user, QuickStab)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense * 1.5
		is_armored = int("armor" in target.tags) * 0.6
		is_heavy_armored = int("heavy armor" in target.tags) * 0.9
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * (strength/2)  *1.4, user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = user.get_accuracy(weapon)
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

		return chance_to_hit

	@staticmethod
	def get_pain_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"]-use_info.target.characteristics["intelligence"]/2 - 10 * int("armor" in use_info.target.tags or "heavy armor" in use_info.target.tags), 5, 95)
		return chance
	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= QuickStab.get_pain_chance(use_info):
			modifier = get_modifier_by_name("pain",use_info.inhibitor, use_info.target)
			return [modifier]
		return []


	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user,  QuickStab, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class Cut(Ability): 
	"""
	Cutting attack for swords, daggers, anything bladed.
	Effective against unarmored oponents, mediocore against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity  - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength * 1.5 - is_armored * defense * 2 - is_heavy_armored * defense * 3

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	"""
	name = "cut"
	description = "Cut em up!"
	energy_required = 2
	requirements = None
	requires_target = "enemy"

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not hasattr(target, "exp_value"):
			return False, "Can't attack a player."
		if not target.dead:
			return Ability.can_use(user, Cut)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense
		is_armored = int("armor" in target.tags) * 0.4
		is_heavy_armored = int("heavy armor" in target.tags) * 0.7
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * strength + not_armored * 0.05 *(weapon_dmg * strength)  *1.15, user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = user.get_accuracy(weapon)
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

		return chance_to_hit

	@staticmethod
	def get_bleeding_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"] - 15 * int("armor" in use_info.target.tags) - 20*("heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= Cut.get_bleeding_chance(use_info):
			modifier = get_modifier_by_name("bleeding",use_info.inhibitor, use_info.target)
			return [modifier]
		return []

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user,  Cut, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class QuickCut(Ability): 
	"""
	Exactly like cut, except takes less energy and suffers more penalties for armored opoentns.
	Cutting attack for small bladed weapons, like daggers.
	Effective against unarmoed oponents, weak against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity  - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength - is_armored * defense * 3 - is_heavy_armored * defense * 4

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	above average dex required to use 

	"""
	name = "quick cut"
	description = "Cut em up!"
	energy_required = 1
	requirements = None
	requires_target = "enemy"

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not hasattr(target, "exp_value"):
			return False, "Can't attack a player."
		if not target.dead:
			return Ability.can_use(user, QuickCut)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense
		is_armored = int("armor" in target.tags) * 0.6
		is_heavy_armored = int("heavy armor" in target.tags) * 0.9
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * (strength/2), user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = user.get_accuracy(weapon)
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

		return chance_to_hit

	@staticmethod
	def get_bleeding_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"] - 15 * int("armor" in use_info.target.tags) - 20*("heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= QuickCut.get_bleeding_chance(use_info):
			modifier = get_modifier_by_name("bleeding", use_info.inhibitor, use_info.target)
			return [modifier]
		return []

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user,  QuickCut, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class ShieldUp(Ability): 
	"""
	Raise the shield to protect yourself, gain a defense bonus and a pennalty to evasion for one turn.

	defense_gained = ?
	evasion_lost = ?

	"""
	name = "shield up"
	description = "Hide behind your steel."
	energy_required = 3
	requirements = None
	requires_target = None

	@staticmethod
	def can_use(user, target=None):
		return Ability.can_use(user, ShieldUp)

	@staticmethod
	def get_buff_modifiers(use_info):
		defense_bonus = use_info.use_info["item_used"].stats["defense"]
		modifier_params = {"stats_change": {"defense":defense_bonus}}
		modifier = get_modifier_by_name("shielded", use_info.use_info["item_used"], use_info.target, modifier_params)
		return [modifier]

	@staticmethod
	def get_buff_description(use_info):
		return ""

	@staticmethod
	def use(user, target, weapon, combat_event):
		target = user
		buff_info = BuffInfo(user, ShieldUp, target, combat_event)
		buff_info.use_info["item_used"] = weapon
		return Ability.use(buff_info)


class Revive(Ability): 
	"""
	Revive a creature

	"""
	name = "revive"
	description = "Revive a creature."
	energy_required = 5
	requirements = None
	requires_target = "friendly"

	@staticmethod
	def can_use(user, target=None):
		return Ability.can_use(user, Revive)

	@staticmethod
	def get_buff_modifiers(use_info):
		#defense_bonus = use_info.use_info["item_used"].stats["defense"]
		#modifier_params = {"stats_change": {"defense":defense_bonus}}
		#modifier = get_modifier_by_name("shielded", use_info.use_info["item_used"], use_info.target, modifier_params)
		return []
		#return [modifier]

	@staticmethod
	def get_buff_description(use_info):
		return ""

	@staticmethod
	def use(user, target, weapon, combat_event):
		buff_info = BuffInfo(user, Revive, target, combat_event)
		buff_info.use_info["item_used"] = None

		if buff_info.target.dead:
			buff_info.target.dead = False
			buff_info.target.health = buff_info.target.stats["max_health"] 
			buff_info.target.refresh_derived()

		buff_info.description += "%s revives %s.\n"%(user.short_desc.capitalize(),target.short_desc.capitalize())
		return Ability.use(buff_info)


class Sweep(Ability): 
	"""
	Sweeping attack for bladed weapons.
	Hits multiple targets, first target gets the msot damage, each next target suffers less damage than previous. 

	avg chance to hit = ?
	avg dmg = ?
	chance to cause "bleeding" = ?
	"""
	name = "sweep"
	description = "Swippity sweep."
	energy_required = 4
	requirements = None
	requires_target = "enemy"


	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not hasattr(target, "exp_value"):
			return False, "Can't attack a player."
		if not target.dead:
			return Ability.can_use(user, Sweep)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_dmg = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense
		is_armored = int("armor" in target.tags) * 0.4
		is_heavy_armored = int("heavy armor" in target.tags) * 0.7
		not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

		dmg = clamp( weapon_dmg * strength, user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = user.get_accuracy(weapon)
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

		return chance_to_hit

	@staticmethod
	def get_bleeding_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"] - 15 * int("armor" in use_info.target.tags) - 20*("heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= Sweep.get_bleeding_chance(use_info):
			modifier = get_modifier_by_name("bleeding", use_info.inhibitor, use_info.target)
			return [modifier]
		return []

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AoeAttackInfo(user, Sweep, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

""" Enemy abilities below """
class RodentBite(Ability):
	name = "rodent bite"
	description = "Rodents bite!"
	energy_required = 1
	requirements = None
	requires_target = "enemy"


	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion - is_quick * target_evasion

	dmg = base_damage * strength  - is_armored * defense * 3 - is_heavy_armored * defense * 5

	avg chance to hit = 55

	avg damage = 5

	chance to cause "pain" = ?

	"""

	@staticmethod
	def get_damage(user, target, weapon):
		weapon_damage = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense
		is_armored = int("armor" in target.tags) * 0.5
		is_heavy_armored = int("heavy armor" in target.tags) * 0.8

		dmg = clamp( weapon_damage* strength , user.characteristics["strength"], 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):

		accuracy = user.get_accuracy(weapon)
		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

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
	def get_pain_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"]-use_info.target.characteristics["intelligence"]/2 - 10 * int("armor" in use_info.target.tags or "heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= RodentBite.get_pain_chance(use_info):
			modifier = get_modifier_by_name("pain", use_info.inhibitor, use_info.target)
			return [modifier]
		return []


	@staticmethod
	def get_miss_description(attack_info):
		return "%s tries to bite %s but misses.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.target.short_desc.capitalize())

	@staticmethod
	def get_hit_description(attack_info):
		return "%s bites %s and deals %d damage.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.target.short_desc.capitalize(), attack_info.use_info["damage_dealt"])

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user, RodentBite, target, combat_event)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)


class AnimalBite(Ability):
	name = "animal bite"
	description = "Animals bite, bad!"
	energy_required = 3
	requirements = None
	requires_target = "enemy"
	"""
	chance to hit = ?
	avg chance to hit = ?
	avg damage = ?
	chance to cause "pain" = ?
	"""
	@staticmethod
	def get_damage(user, target, weapon):
		weapon_damage = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense
		is_armored = int("armor" in target.tags) * 0.2
		is_heavy_armored = int("heavy armor" in target.tags) * 0.4

		dmg = clamp( weapon_damage*strength , user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		accuracy = user.get_accuracy(weapon)
		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

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
		return "%s tries to bite %s but misses.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.target.short_desc.capitalize())

	@staticmethod
	def get_hit_description(attack_info):
		return "%s bites %s and deals %d damage.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.target.short_desc.capitalize(), attack_info.use_info["damage_dealt"])

	@staticmethod
	def get_pain_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"]-use_info.target.characteristics["intelligence"]/2 - 10 * int("armor" in use_info.target.tags or "heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= AnimalBite.get_pain_chance(use_info):
			modifier = get_modifier_by_name("pain", use_info.inhibitor, use_info.target)
			return [modifier]
		return []


	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user,  AnimalBite, target)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

class AnimalClaw(Ability):
	name = "animal claw"
	description = "Animals claw, bad!"
	energy_required = 2
	requirements = None
	requires_target = "enemy"
	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion - is_quick * target_evasion
	dmg = base_damage * strength  - is_armored * defense * 4 - is_heavy_armored * defense * 5
	avg chance to hit = 55
	avg damage = 5
	chance to cause "bleeding" = ?
	"""
	@staticmethod
	def get_damage(user, target, weapon):
		weapon_damage = diceroll(weapon.stats["damage"])
		strength = user.characteristics["strength"]
		defense = target.defense
		is_armored = int("armor" in target.tags) * 0.2
		is_heavy_armored = int("heavy armor" in target.tags) * 0.5

		dmg = clamp( weapon_damage* strength , user.characteristics["strength"]/2, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(user, target, weapon):
		accuracy = user.get_accuracy(weapon)
		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = clamp(accuracy - evasion, 5, 95 )

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
		return "%s tries to claw %s but misses.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.target.short_desc.capitalize())

	@staticmethod
	def get_hit_description(attack_info):
		return "%s claws %s and deals %d damage.\n"%(attack_info.inhibitor.short_desc.capitalize(), attack_info.target.short_desc.capitalize(), attack_info.use_info["damage_dealt"])

	@staticmethod
	def get_bleeding_chance(use_info):
		chance = clamp(use_info.inhibitor.characteristics["intelligence"]*use_info.inhibitor.characteristics["dexterity"] - use_info.target.characteristics["vitality"] - 15 * int("armor" in use_info.target.tags) - 20*("heavy armor" in use_info.target.tags), 5, 95)
		return chance

	@staticmethod
	def get_modifiers_applied(use_info):
		if random.randint(1, 100) <= AnimalClaw.get_bleeding_chance(use_info):
			modifier = get_modifier_by_name("bleeding", use_info.inhibitor, use_info.target)
			return [modifier]
		return []

	@staticmethod
	def use(user, target, weapon, combat_event):
		attack_info = AttackInfo(user,  AnimalClaw, target)
		attack_info.use_info["item_used"] = weapon
		return Ability.use(attack_info)

abilities = {
	"smash": Smash,
	"shield up": ShieldUp,
	"cut": Cut,
	"stab": Stab,
	"quick cut": QuickCut,
	"quick stab": QuickStab,
	"sweep": Sweep,

	#strict non player abilities below
	"revive": Revive,

	# animal abilities below
	"rodent bite": RodentBite,
	"animal bite": AnimalBite,
	"animal claw": AnimalClaw,


}
