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
	living - Living creatures
	undead - Undead creatures
	armor - Armored, takes less damage
	heavy armor - Heavy armored, takes little damage
	quick - Harder to hit and dodge
	slow - Easier to hit and dodge
	physical ressitant - Resistant to physical damage
	magic ressitant - Resistant to magic damage

	animal - Animal creatures
	rodent - Rat creatures and similar


"""

class AbilityUseInfo(object):
	def __init__(self, inhibitor, ability_type, prototype_class, target):
		self.ability_type = ability_type
		self.prototype_class = prototype_class
		self.inhibitor = inhibitor
		self.target = target

class AttackInfo(object):
	def __init__(self, inhibitor, ability_type, prototype_class, target, use_info=None, description = ""):
		AbilityUseInfo.__init__(self, inhibitor, ability_type, prototype_class, target)
		self.description = description

		if not use_info:
			use_info = {
				"hit_chance" : 0,
				"damage_dealt" : 0,
				"experience_gained" : 0,
				"did_hit" : False,
				"did_kill" : False,
				"item_used": None,
				"energy_consumed": 0,
				"modifiers_applied": [],
				"loot_dropped": []
			}
		self.use_info = use_info

class BuffInfo(object):
	def __init__(self, inhibitor, ability_type, prototype_class, target, use_info=None, description=""):
		AbilityUseInfo.__init__(self, inhibitor, ability_type, prototype_class, target)
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
	def use(prototype, user, target, use_info):
		use_info.use_info["energy_change"] = -prototype.energy_required 
		user.energy = user.energy + use_info.use_info["energy_change"]		
		use_info.description += "%s has %d energy left.\n"%(user.name.title(), user.energy)
		return use_info

	@staticmethod
	def can_use(energy, energy_required):
		if not energy >= energy_required:
			return False, "Not enough energy"
		return True, ""

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
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user.energy, Smash.energy_required)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):

		dmg = clamp( weapon_dmg * strength - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon=None):
		attack_info = AttackInfo(user, "attack", Smash, target)
		if not weapon:
			weapon = user.primary_weapon

		attack_info.use_info["item_used"] = weapon

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*2
		is_slow = int("slow" in target.tags)*2
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = Smash.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)
		attack_info.use_info["hit_chance"] = chance_to_hit
		if random.randint(0, 100) > chance_to_hit:
			attack_info.description += "%s smashes %s at %s but misses.\n"%(user.name.title(), weapon.name, target.name)
		else:
			weapon_dmg = diceroll(weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence
			is_armored = int("armor" in target.tags) * 2
			is_heavy_armored = int("heavy armor" in target.tags) * 3

			dmg = Smash.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)
			attack_info.use_info["did_hit"] = True
			attack_info.use_info["damage_dealt"] = dmg
			attack_info = target.damage(dmg, attack_info)

			attack_info.description += = "%s smashes %s and deals %d damage to %s.\n"%(user.name.title(), weapon.name, dmg, target.name)

		return Ability.use(Smash, user, target, attack_info)

class Stab(Ability):

	"""
	Stabbing attack for swords, daggers, rapiers, pikes, anything pointy. 
	Effective against unarmoed oponents, very ineffective against armored oponents. 
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = accuracy * dexterity * 1.5 - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength + not_armored * 0.3 *(weapon_dmg * strength) - defence * 1.5 - is_armored * defence * 3 - is_heavy_armored * defence * 4

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "bleeding" = ?

	chance to cause "pain" = ?

	"""
	name = "stab"
	description = "Stab in the gut!"
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user.energy, Stab.energy_required)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):

		dmg = clamp( weapon_dmg * strength + not_armored * 0.3 *(weapon_dmg * strength) - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon=None):
		if not weapon:
			weapon = user.primary_weapon

		msg = ""
		user.energy = user.energy - Stab.energy_required

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"]) * 1.5
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = Stab.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s stabs %s at %s but misses.\n"%(user.name, weapon.name, target.name)
		else:
			weapon_dmg = diceroll(weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence * 1.5
			is_armored = int("armor" in target.tags) * 3
			is_heavy_armored = int("heavy armor" in target.tags) * 4
			not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

			dmg = Stab.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s stabs %s and deals %d damage to %s.\n"%(user.name, weapon.name, dmg, target.name)

		return msg + str(Ability.use(user, target))

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
	name = "quick stab"
	description = "Quick stab in the gut!"
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user.energy, QuickStab.energy_required)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):

		dmg = clamp( weapon_dmg * strength + not_armored * 0.2 *(weapon_dmg * strength) - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon=None):
		if not weapon:
			weapon = user.primary_weapon

		msg = ""
		user.energy = user.energy - QuickStab.energy_required

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"]) * 1.5
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = QuickStab.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s stabs %s at %s but misses.\n"%(user.name, weapon.name, target.name)
		else:
			weapon_dmg = diceroll(weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence * 1.5
			is_armored = int("armor" in target.tags) * 4
			is_heavy_armored = int("heavy armor" in target.tags) * 5
			not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

			dmg = QuickStab.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s stabs %s and deals %d damage to %s.\n"%(user.name, weapon.name, dmg, target.name)

		return msg + str(Ability.use(user, target))

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
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user.energy, Cut.energy_required)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):

		dmg = clamp( weapon_dmg * strength + not_armored * 0.1 *(weapon_dmg * strength) - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon=None):
		if not weapon:
			weapon = user.primary_weapon

		msg = ""
		user.energy = user.energy - Cut.energy_required

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"]) * 1.5
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = Cut.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s cuts %s at %s but misses.\n"%(user.name, weapon.name, target.name)
		else:
			weapon_dmg = diceroll(weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence
			is_armored = int("armor" in target.tags) * 2
			is_heavy_armored = int("heavy armor" in target.tags) * 3
			not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

			dmg = Cut.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s cuts %s and deals %d damage to %s.\n"%(user.name, weapon.name, dmg, target.name)

		return msg + str(Ability.use(user, target))

class QucikCut(Ability): #TODO test and adapt

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
	name = "quick cut"
	description = "Cut em up!"
	energy_required = 2
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user.energy, QucikCut.energy_required)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):

		dmg = clamp( weapon_dmg * strength + not_armored * 0.1 *(weapon_dmg * strength) - defence - is_armored * defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small * evasion - is_quick * evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon=None):
		if not weapon:
			weapon = user.primary_weapon

		msg = ""
		user.energy = user.energy - QucikCut.energy_required

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = QucikCut.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s cuts %s at %s but misses.\n"%(user.name, weapon.name, target.name)
		else:
			weapon_dmg = diceroll(weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence
			is_armored = int("armor" in target.tags) * 3
			is_heavy_armored = int("heavy armor" in target.tags) * 4
			not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

			dmg = QucikCut.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s cuts %s and deals %d damage to %s.\n"%(user.name, weapon.name, dmg, target.name)

		return msg + str(Ability.use(user, target))

class Bash(Ability): #TODO test and adapt

	"""
	A shield bash, does low damage, but has a chance to knockdown or stagger the enemy, causing them to have less energy next turn.
	High chance to hit.
	Higher chance to hit big and slow oponents.

	chance to hit = ?

	dmg = ?

	avg chance to hit = 55

	avg dmg = ?

	chance to cause "knockdown" = ?

	chance to cause "stagger" = ?

	"""
	name = "bash"
	description = "Bash em."
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required." 
		if not target.dead:
			return Ability.can_use(user.energy, Bash.energy_required)
		else:
			return False, "Target is already dead."

	@staticmethod
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):

		dmg = clamp( weapon_dmg * strength + not_armored * 0.1 *(weapon_dmg * strength) - defence - is_armored * defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small * evasion - is_quick * evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target, weapon=None):
		if not weapon:
			weapon = user.primary_weapon

		msg = ""
		user.energy = user.energy - Bash.energy_required

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*3
		is_slow = int("slow" in target.tags)*3
		evasion = target.evasion
		accuracy = diceroll(weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = Bash.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s cuts %s at %s but misses.\n"%(user.name, weapon.name, target.name)
		else:
			weapon_dmg = diceroll(weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence
			is_armored = int("armor" in target.tags) * 3
			is_heavy_armored = int("heavy armor" in target.tags) * 4
			not_armored = int(not "armor" in target.tags and not "heavy armor" in target.tags)

			dmg = Bash.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s cuts %s and deals %d damage to %s.\n"%(user.name, weapon.name, dmg, target.name)

		return msg + str(Ability.use(user, target))

class ShieldUp(Ability): #TODO test and adapt

	"""
	Raise the shield to protect yourself, gain a defence bonus and a pennalty to evasion for one turn.

	defence_gained = ?
	evasion_lost = ?

	"""
	name = "shield up"
	description = "Hide behind your steel."
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target=None):
		return Ability.can_use(user.energy, ShieldUp.energy_required)

	@staticmethod
	def use(user, target=None, weapon=None):
		if not weapon:
			weapon = user.secondary_weapon

		user.energy = user.energy - ShieldUp.energy_required
		defence_bonus = weapon.stats["defence"]
		modifier_params = {"stats_change": {"defence":defence_bonus}}
		modifier = get_modifier_by_name("shielded", weapon, user, modifier_params)
		modifier.apply()
		msg = "%s raises his shield up and gains a %s defence for the next turn.\n"%(user.name, defence_bonus)

		return msg + str(Ability.use(user, target))



class RodentBite(Ability):
	name = "rodent bite"
	description = "Rodents bite!"
	energy_required = 2
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
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):
		dmg = clamp( weapon_dmg* strength - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp( accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def can_use(user, target=None):
		if not target:
			return False, "Target required."
		if not target.dead:
			return Ability.can_use(user.energy, RodentBite.energy_required)
		else:
			return False, "Target is already dead"

	@staticmethod
	def use(user, target, weapon=None):
		if not weapon:
			weapon = user.primary_weapon

		user.energy = user.energy - RodentBite.energy_required
		msg = ""

		accuracy = diceroll(weapon.stats["accuracy"])
		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = RodentBite.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s tries to bite %s but misses.\n"%(user.name, target.name)
		else:

			rough_dmg = diceroll(weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence
			is_armored = int("armor" in target.tags) * 3
			is_heavy_armored = int("heavy armor" in target.tags) * 5

			dmg = RodentBite.get_damage(rough_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s bites %s and deals %d damage.\n"%(user.name, target.name, dmg)

		return msg + Ability.use(user, target)

abilities = {
	"smash": Smash,
	"rodent bite": RodentBite,
	"shield up": ShieldUp,
	"bash": Bash
}
