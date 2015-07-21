import util
import random
import creatures
class Ability(object):
	@staticmethod
	def can_use(energy, energy_required):
		if not energy >= energy_required:
			return False
		return True

	def examine_self(self):
		help_text = "%s\n"%(self.name)
		help_text += "%s\n"%(self.description)
		help_text += "Requires %s energy\n"%(self.energy_required)
		help_text += "Requirements to use:\n %s\n"%( str(self.requirements) )
		return help_text

class Swing(Ability):
	name = "swing"
	description = "Swing your weapon and hope you hit something!"
	energy_required = 30
	requirements = None

	@staticmethod
	def can_use(user):
		return Ability.can_use(user.energy, Swing.energy_required)

	@staticmethod
	def use(user, target):
		user.energy = user.energy - Swing.energy_required

		chance_to_hit = (util.diceroll(user.primary_weapon.stats["accuracy"]) * user.characteristics["dexterity"]) - util.diceroll(target.stats["evasion"])

		if random.randint(0, 100) < chance_to_hit:
			return "%s swings %s and misses %s.\n"%(user.name, user.primary_weapon.name, target.name)
		else:
			dmg = (util.diceroll(user.primary_weapon.stats["damage"]) * user.characteristics["strength"]) - util.diceroll(target.stats["defence"])
			target.health = target.health - dmg
			return "%s swings %s and deals %d damage to %s.\n"%(user.name, user.primary_weapon.name, dmg, target.name)

class RodentBite(Ability):
	name = "rodent_bite"
	description = "Rodents bite!"
	energy_required = 10
	requirements = None
	base_damage = "1d" #  + str


	@staticmethod
	def can_use(user):
		return Ability.can_use(user.energy, RodentBite.energy_required)

	@staticmethod
	def use(user, target):
		user.energy = user.energy - RodentBite.energy_required
		
		chance_to_hit = (user.characteristics["dexterity"] * 10) - util.diceroll(target.stats["evasion"])

		if random.randint(0, 100) < chance_to_hit:
			return "%s tries to bite and misses %s.\n"%(user.name, target.name)
		else:
			dmg = (util.diceroll(self.base_damage + user.characteristics["strength"]) * user.characteristics["strength"]) - util.diceroll(target.stats["defence"])
			target.health = target.health - dmg
			return "%s bites %s and deals %d damage.\n"%(user.name, target.name, dmg)

class Rest(Ability):
	name = "Rest a turn."
	description = "Regenerate energy based on strength."
	energy_required = 0
	requirements = None

	@staticmethod
	def can_use(user):
		return True

	@staticmethod
	def use(user):

		energy_regenerated = user.characteristics["strength"] * 10
		user.energy = user.energy + energy_regenerated
	
		return "%s waits and regenerates %d energy.\n"%(user.name, energy_regenerated)

abilities = {
	"swing": Swing,
	"rodent_bite": RodentBite,
	"rest": Rest

}
