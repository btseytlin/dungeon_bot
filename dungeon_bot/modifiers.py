from util import *
class Modifier(object): #Modifiers always affect only the host that carries them
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], name="", description=""):
		self.uid = get_uid()
		self.name = name
		self.description = description
		self.granted_by = granted_by
		self.host = host
		self.duration = duration # -1 means permanent, number above 0 means turns left
		self.characteristics_change = characteristics_change.copy()
		self.stats_change = stats_change.copy()
		self.abilities_granted = abilities_granted.copy()
		self.tags_granted = tags_granted.copy()

	def apply(self):
		self.host.modifiers.append(self)
		self.host.refresh_derived()
		return self.on_applied()

	@property
	def permanent(self):
		return self.duration == -1
	
	def on_applied(self):
		return "%s modifier applied to %s.\n"%(self.name, self.host.name)

	def on_lifted(self):
		return "%s modifier lifted from %s.\n"%(self.name, self.host.name)


	def on_combat_start(self):
		pass

	def after_turn(self):
		if not self.permanent:
			if self.duration <= 0:
				return self.lift()

			self.duration != 1

	def on_hit(self, target, attack_info=None):
		pass

	def on_miss(self, target, attack_info=None):
		pass

	def on_ability(self, target, ability_info=None):
		pass

	def on_kill(self, target):
		pass

	def on_death(self, killer=None):
		pass

	def on_exp_gain(self, exp_amount=None):
		pass

	def on_loot(self, loot):
		pass

	def on_modifier_applied(self, modifier):
		pass

	def lift(self):
		self.host.modifiers.remove(self)
		self.host.refresh_derived()
		return self.on_lifted()

class Shielded(Modifier): #simply adds defence, hinders evasion
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], name="shielded", description="grants defence"):
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted, name, description)
		self.defence = "3d6"
		self.evasion = "-1d6"

class Bonus(Modifier): #simply adds defence, hinders evasion
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], name="shielded", description="grants defence"):
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted, name, description)
		self.defence = "3d6"
		self.evasion = "-1d6"

def get_modifier_by_name(modifier_name, source, target, params={}):
	if not "duration" in params.keys():
		params["duration"] = -1
	if not "characteristics_change" in params.keys():
		params["characteristics_change"] = {}
	if not "stats_change" in params.keys():
		params["stats_change"] = {}
	if not "abilities_granted" in params.keys():
		params["abilities_granted"] = []
	if not "tags_granted" in params.keys():
		params["tags_granted"] = []
	return modifier_listing[modifier_name](source, target, params["duration"], params["characteristics_change"], params["stats_change"], params["abilities_granted"], params["tags_granted"])

modifier_listing = {
	"shielded" : Shielded,
	"bonus" : Bonus,
}