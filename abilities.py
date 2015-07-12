import util
class Ability(object):
	def __init__(self, name, description, energy_required=0, requirements=None):
		self.name = name
		self.description = description
		self.use = use
		self.requirements = requirements
		self.energy_required = energy_required

class Swing(object):
	base_energy_required = 30
	base_requirements = None
	def __init__(self, energy_required=30, requirements=None):
		Ability.__init__(self, "swing", "Swing your weapon and hope you hit something!", energy_required, requirements)

	def use(self, user, target):
		if not user.energy >= self.energy_required:
			return False, "Not enough energy to use %s"%(self.name)
		user.energy = user.energy - self.energy_required
		chance_to_hit = (util.diceroll(user.primary_weapon.stats["accuracy"]) * user.characteristics["dexterity"]) - target.stats["evasion"]

		if random.randint(0, 100) < chance_to_hit:
			return "%s swings %s and misses %s"%(user.name, user.primary_weapon.name, target.name)
		else:
			dmg = util.diceroll(user.primary_weapon.stats["damage"]) * user.characteristics["strength"]) - util.diceroll(target.stats["defence"])
			target.health = target.health - dmg
			return "%s swings %s and deals %d damage to %s"%(user.name, user.primary_weapon.name, dmg, target.name)

abilities = {
	"swing": Swing
}