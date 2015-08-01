from util import *
import random
class Modifier(object): #Modifiers always affect only the host that carries them
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [],  priority=0, name="", description=""):
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
		self.priority = priority

	def apply(self):
		self.host.add_modifier(self)
		msg = self.on_applied() + self.host.on_modifier_applied(self)
		return msg

	@property
	def permanent(self):
		return self.duration == -1
	
	def on_applied(self):
		return "%s modifier applied to %s.\n"%(self.name.title(), self.host.name.title())

	def on_lifted(self):
		return "%s modifier lifted from %s.\n"%(self.name.title(), self.host.name.title())

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
		if not self.permanent:
			if self.duration <= 0:
				return self.lift()

			self.duration != 1

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

	def lift(self):
		self.host.modifiers.remove(self)
		self.host.refresh_derived()
		return self.on_lifted()

class Shielded(Modifier): #simply adds defence, hinders evasion
	def __init__(self, granted_by, host, duration=2, characteristics_change = {}, stats_change = {"defence":"3d6"}, abilities_granted = [], tags_granted = [], priority=0, name="shielded", description="grants defence") :
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description, )

	def on_applied(self):
		msg = super(Shielded, self).on_applied()
		msg += "%s raises his shieldup and gains a %s defence for the next turn.\n"%(self.host.name, self.stats_change["defence"])
		return msg

class Bonus(Modifier): #simply adds defence, hinders evasion
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="bonus", description="???"):
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted, priority, name, description, )


class FireAttack(Modifier):
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="fire attack",  description="Has a chance to cause fire additional damage every attack by host.",):
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description)

	def on_hit(self, attack_info):
		fire_chance = self.granted_by.stats["fire_chance"]
		fire_damage = self.granted_by.stats["fire_damage"]
		if attack_info.use_info["did_hit"] and not attack_info.target.dead and not "fire resistant" in attack_info.target.tags:
			chance = diceroll( fire_chance )
			if random.randint(0, 100) < chance:
				dmg = diceroll( fire_damage )
				attack_info.target.damage( dmg )
				attack_info.description += "%s causes %d fire damage to %s.\n"%(self.granted_by.name.title(), dmg, attack_info.target.name.title())
				attack_info.use_info["damage_dealt"] += dmg

		return attack_info

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
	if not "priority" in params.keys():
		params["priority"] = 0

	mod = modifier_listing[modifier_name](source, target, params["duration"], params["characteristics_change"], params["stats_change"], params["abilities_granted"], params["tags_granted"], params["priority"])
	return mod

modifier_listing = {
	"shielded" : Shielded,
	"bonus" : Bonus,
	"fire_attack" : FireAttack
}