import json
from util import *
import random

class LevelPerk(object): #LevelPerks always affect only the host that carries them
	def __init__(self, host, requirements, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [],  priority=0, name="", description=""):
		self.uid = get_uid()
		self.name = name
		self.description = description
		self.host = host
		self.characteristics_change = characteristics_change.copy()
		self.stats_change = stats_change.copy()
		self.abilities_granted = abilities_granted.copy()
		self.tags_granted = tags_granted.copy()
		self.priority = priority

	def on_combat_start(self):
		pass

	def on_combat_over(self):
		pass

	def on_item_equipped(self, item):
		pass

	def on_item_unequipped(self, item):
		pass

	def on_consumable_used(self, item):
		pass

	def on_turn(self):
		pass

	def on_round(self):
		pass

	def on_attack(self, ability_info=None):
		pass

	def on_hit(self, ability_info=None):
		pass

	def on_got_hit(self, ability_info=None):
		pass

	def on_attacked(self, ability_info=None):
		pass

	def on_miss(self, ability_info=None):
		pass

	def on_buff(self, ability_info=None):
		pass

	def on_buffed(self, ability_info=None):
		pass

	def on_kill(self, ability_info=None):
		pass

	def on_death(self, ability_info=None):
		pass
		
	def on_experience_gained(self, ability_info=None):
		pass

	def on_energy_gained(self, amount=None):
		pass

	def on_energy_lost(self, amount=None):
		pass

	def on_health_gained(self, amount=None):
		pass

	def on_health_lost(self, amount=None):
		pass

	def on_loot(self, item_gained):
		pass

	def on_modifier_applied(self, modifier):
		pass

class Educated(LevelPerk):
	requirements = {
		"has_perks": [],
		"characteristics": {
			"intelligence": 5
		}
	}

	def __init__(self, host, requirements, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [],  priority=1, name="edcated", description="Get 10 percent additional experience."):
		LevelPerk.__init__(self, host, characteristics_change, stats_change, abilities_granted, tags_granted,  priority, name, description)

	def on_experience_gained(self, ability_info):
		additional_gain = ability_info.use_info["experience_gained"] * 0.10
		ability_info["experience_gained"] += additional_gain
		ability_info.description +=  "%s gains %d additional experience due to being educated"%(self.host.name.title(), additional_gain)
		return ability_info

level_perks = {
	"educated":Educated, 
}
