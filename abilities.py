import util
class Ability(object):
	def __init__(self, name, description, energy_required=0, requirements=None):
		self.name = name
		self.description = description
		self.use = use
		self.requirements = requirements
		self.energy_required = energy_required
	def use(self, user, target):
		if not user.energy >= self.energy_required:
			return False, "Not enough energy to use %s"%(self.name)
		user.energy = user.energy - self.energy_required
		return True

class Swing(object):
	base_energy_required = 30
	base_requirements = None
	def __init__(self, energy_required=30, requirements=None):
		Ability.__init__(self, "swing", "Swing your weapon and hope you hit something!", energy_required, requirements)

	def use(self, user, target):
		enough_energy, message = super(Ability, self).use(user, target)
		if not energy_required:
			return message
		
		chance_to_hit = (util.diceroll(user.primary_weapon.stats["accuracy"]) * user.characteristics["dexterity"]) - util.diceroll(target.stats["evasion"])

		if random.randint(0, 100) < chance_to_hit:
			return "%s swings %s and misses %s"%(user.name, user.primary_weapon.name, target.name)
		else:
			dmg = util.diceroll(user.primary_weapon.stats["damage"]) * user.characteristics["strength"]) - util.diceroll(target.stats["defence"])
			target.health = target.health - dmg
			return "%s swings %s and deals %d damage to %s"%(user.name, user.primary_weapon.name, dmg, target.name)

class RodentBite(objet):
	base_damage = "1d" #  + str
	base_energy_required = 10
	base_requirements = None
	def __init__(self, energy_required=10, requirements=None):
		Ability.__init__(self, "rodent_bite", "Rodents bite!", energy_required, requirements)

	def use(self, user, target):
		enough_energy, message = super(Ability, self).use(user, target)
		if not energy_required:
			return message
		
		chance_to_hit = ((user.characteristics["dexterity"] * 10) - util.diceroll(target.stats["evasion"])

		if random.randint(0, 100) < chance_to_hit:
			return "%s tries to bite and misses %s."%(user.name, target.name)
		else:
			dmg = util.diceroll(self.base_damage + user.characteristics["strength"]) * user.characteristics["strength"]) - util.diceroll(target.stats["defence"])
			target.health = target.health - dmg
			return "%s bites %s and deals %d damage."%(user.name, target.name, dmg)

abilities = {
	"swing": Swing,
	"rodent_bite": RodentBite
}