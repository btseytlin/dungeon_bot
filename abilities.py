import util
import random

class Ability(object):
	@staticmethod
	def use(user, target):
		killed, kill_message = target.kill_if_nececary(user)
		if killed == True:
			return kill_message +"\n"
		return ""

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

class Swing(Ability):
	name = "swing"
	description = "Swing your weapon and hope you hit something!"
	energy_required = 30
	requirements = None

	@staticmethod
	def can_use(user, target):
		if not target.dead:
			return Ability.can_use(user.energy, Swing.energy_required)
		else:
			return False, "Target is already dead"

	@staticmethod
	def use(user, target):
		msg = ""
		user.energy = user.energy - Swing.energy_required

		chance_to_hit = util.clamp( (util.diceroll(user.primary_weapon.stats["accuracy"]) * user.characteristics["dexterity"]*10) - util.diceroll(target.stats["evasion"]), 0, 100 )
		if random.randint(0, 100) > chance_to_hit:
			msg = "%s swings %s at %s but misses .\n"%(user.name, user.primary_weapon.name, target.name)
		else:
			dmg = util.clamp( (util.diceroll(user.primary_weapon.stats["damage"]) * user.characteristics["strength"]) - util.diceroll(target.stats["defence"]), 0, 99999999 )
			target.health = target.health - dmg
			msg = "%s swings %s and deals %d damage to %s.\n"%(user.name, user.primary_weapon.name, dmg, target.name)

		msg += "%s has %d energy left.\n"%(user.name, user.energy)
		return msg + str(Ability.use(user, target))

class RodentBite(Ability):
	name = "rodent_bite"
	description = "Rodents bite!"
	energy_required = 15
	requirements = None
	base_damage = "2d" #  + str


	@staticmethod
	def can_use(user, target):
		if not target.dead:
			return Ability.can_use(user.energy, Swing.energy_required)
		else:
			return False, "Target is already dead"

	@staticmethod
	def use(user, target):
		user.energy = user.energy - RodentBite.energy_required
		msg = ""
		chance_to_hit = util.clamp( (user.characteristics["dexterity"] * 20) - util.diceroll(target.stats["evasion"]), 0, 100 )

		if random.randint(0, 100) > chance_to_hit:
			msg = "%s tries to bite %s and misses.\n"%(user.name, target.name)
		else:
			dmg = util.clamp( (util.diceroll(RodentBite.base_damage + str(user.characteristics["strength"])*2) * user.characteristics["strength"]) - util.diceroll(target.stats["defence"]), 0, 99999999 )
			target.health = target.health - dmg
			msg = "%s bites %s and deals %d damage.\n"%(user.name, target.name, dmg)

		msg += "%s has %d energy left.\n"%(user.name, user.energy)
		return msg + Ability.use(user, target)

abilities = {
	"swing": Swing,
	"rodent_bite": RodentBite
}
