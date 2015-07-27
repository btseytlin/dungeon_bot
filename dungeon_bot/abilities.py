from util import clamp, diceroll
import random

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


class Ability(object):
	@staticmethod
	def use(user, target):
		msg = "%s has %d energy left.\n"%(user.name.title(), user.energy)
		killed, kill_message = target.kill_if_nececary(user)
		if killed == True:
			return kill_message +"\n" + msg
		return msg

	@staticmethod
	def can_use(energy, energy_required):
		if not energy >= energy_required:
			return False, "Not enough energy"
		return True, ""

	def examine_self(ability):
		help_text = "%s\n"%(ability.name)
		help_text += "%s\n"%(ability.description)
		help_text += "Requires %s energy\n"%(ability.energy_required)
		help_text += "Requirements to use:\n %s\n"%( str(ability.requirements) )
		return help_text

class Smash(Ability):

	"""
	chance to hit = accuracy * dexterity - target_evasion - is_small * target_evasion * 2 - is_quick * target_evasion * 2 + is_big * target_evasion * 2 + is_slow * target_evasion * 2

	dmg = weapon_dmg * strength - defence - is_armored * defence * 2 - is_heavy_armored * defence * 3

	avg chance to hit = 45

	chance to cause "knockdown" = ?

	chance to cause "concussion" = ?

	"""
	name = "smash"
	description = "Smash your weapon and hope you hit something!"
	energy_required = 3
	requirements = None

	@staticmethod
	def can_use(user, target):
		if not target.dead:
			return Ability.can_use(user.energy, Smash.energy_required)
		else:
			return False, "Target is already dead"

	@staticmethod
	def get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored):

		dmg = clamp( weapon_dmg * strength - defence - is_armored*defence - is_heavy_armored * defence, 0, 99999999 )
		return dmg

	@staticmethod
	def get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow):
		chance_to_hit = clamp(accuracy*dexterity - evasion - is_small*evasion - is_quick *evasion + is_big * evasion + is_slow * evasion , 0, 100 )

		return chance_to_hit

	@staticmethod
	def use(user, target):
		msg = ""
		user.energy = user.energy - Smash.energy_required

		is_small = int("small" in target.tags)*2
		is_quick = int("quick" in target.tags)*2
		is_big = int("big" in target.tags)*2
		is_slow = int("slow" in target.tags)*2
		evasion = target.evasion
		accuracy = diceroll(user.primary_weapon.stats["accuracy"])
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = Smash.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s smashes %s at %s but misses.\n"%(user.name, user.primary_weapon.name, target.name)
		else:
			weapon_dmg = diceroll(user.primary_weapon.stats["damage"])
			strength = user.characteristics["strength"]
			defence = target.defence
			is_armored = int("armor" in target.tags) * 2
			is_heavy_armored = int("heavy armor" in target.tags) * 3

			dmg = Smash.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s smashes %s and deals %d damage to %s.\n"%(user.name, user.primary_weapon.name, dmg, target.name)

		return msg + str(Ability.use(user, target))

class RodentBite(Ability):
	name = "rodent_bite"
	description = "Rodents bite!"
	energy_required = 4
	requirements = None
	base_accuracy = "4d6"
	base_damage = "2d6"

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
	def can_use(user, target):
		if not target.dead:
			return Ability.can_use(user.energy, RodentBite.energy_required)
		else:
			return False, "Target is already dead"

	@staticmethod
	def use(user, target):
		user.energy = user.energy - RodentBite.energy_required
		msg = ""

		is_small = int("small" in target.tags)
		is_quick = int("quick" in target.tags)
		is_big = int("big" in target.tags)
		is_slow = int("slow" in target.tags)
		evasion = target.evasion
		accuracy = diceroll(RodentBite.base_accuracy)
		dexterity = user.characteristics["dexterity"]

		chance_to_hit = RodentBite.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s tries to bite %s but misses.\n"%(user.name, target.name)
		else:

			dmg = diceroll(RodentBite.base_damage)
			strength = user.characteristics["strength"]
			defence = target.defence
			is_armored = int("armor" in target.tags) * 3
			is_heavy_armored = int("heavy armor" in target.tags) * 5

			dmg = RodentBite.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)

			target.health = target.health - dmg
			msg = "%s bites %s and deals %d damage.\n"%(user.name, target.name, dmg)

		return msg + Ability.use(user, target)

abilities = {
	"smash": Smash,
	"rodent_bite": RodentBite
}
