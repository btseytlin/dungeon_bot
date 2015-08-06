#!/usr/bin/env python3
from .util import *
import random
class Modifier(object): #Modifiers always affect only the host that carries them
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change = {}
	abilities_granted = []
	tags_granted = []
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
		added = self.host.add_modifier(self)
		if not added == False:
			msg = self.on_applied() + self.host.on_modifier_applied(self)
			return msg
		return ""

	def can_apply(self):
		return True

	@property
	def permanent(self):
		return self.duration == -1
	
	def on_applied(self):
		return ""
		#return "%s modifier applied to %s.\n"%(self.name.capitalize(), self.host.short_desc.capitalize())

	def on_lifted(self):
		return ""
		#return "%s modifier lifted from %s.\n"%(self.name.capitalize(), self.host.short_desc.capitalize())

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
		return ""

	def on_round(self):
		if not self.permanent:
			if self.duration <= 0:
				return self.lift()
			self.duration -= 1
		return ""

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

	def on_experience_gain(self, value):
		return "", value

	def on_level_up(self):
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

	def on_modifier_lifted(self, modifier):
		pass

	def lift(self):
		self.host.modifiers.remove(self)
		return self.on_lifted() + self.host.on_modifier_lifted(self)

class KnockedDown(Modifier): #simply adds defence, hinders evasion
	priority = 0
	duration = 0
	characteristics_change = {"dexterity": 2}
	stats_change = {"evasion": "-5d6", "defence": "-2d6"}
	abilities_granted = []
	tags_granted = []

	def __init__(self, granted_by, host, duration=2, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="knockdown", description="Loose 5d6 evasion, 2d6 your defence, and half your dexterity.") :
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description )
		self.characteristics_change = {"dexterity": -host.characteristics["dexterity"]}
		self.duration = clamp( 10 - host.characteristics["dexterity"], 2, 4)
		self.stats_change = {"evasion": "-5d6", "defence": "-2d6"}
		
	def on_round(self):
		msg = "%s struggles to get up from the ground.\n"%(self.host.short_desc.capitalize())
		msg += super(KnockedDown, self).on_round()
		return msg

	def on_lifted(self):
		return "%s gets up from the ground!\n"%(self.host.short_desc.capitalize())

	def on_applied(self):
		msg = super(KnockedDown, self).on_applied()
		msg += "%s is knocked down!\n"%(self.host.short_desc.capitalize())
		return msg

class Vunerable(Modifier): #simply adds defence, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {}
	stats_change =  {"defence": "-3d6"}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, duration=2, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="vunerable", description="Loose 3d6 defence for a turn."):
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description )

	def on_applied(self):
		msg = super(Vunerable, self).on_applied()
		msg += "%s is exposed and vunerable!\n"%(self.host.short_desc.capitalize())
		return msg

	def on_lifted(self):
		return "%s is no longer vunerable!\n"%(self.host.short_desc.capitalize())

class Pain(Modifier): #simply adds defence, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {"dexterity":-3, "strength":-3, "intelligence":-3}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, duration=2, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="pain", description="Loose 3 dexterity, strength and intelligence for a turn.") :
		characteristics_change = {"dexterity":-3, "strength":-3, "intelligence":-3}
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description )
		self.duration = Pain.duration


	def can_apply(self):
		return "animate" in self.host.tags

	def on_applied(self):
		msg = super(Pain, self).on_applied()
		msg += "%s is wrecked with pain!\n"%(self.host.short_desc.capitalize())
		return msg

	def on_lifted(self):
		return "%s is no longer in pain!\n"%(self.host.short_desc.capitalize())


class Bleeding(Modifier): #simply adds defence, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, duration=6, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="bleeding", description="loose 1d3 hp every turn for 6 rounds"):
		duration = clamp( 10 - host.characteristics["vitality"], 3, 8)
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description )

	def can_apply(self):
		return "living" in self.host.tags

	def on_round(self):
		msg = ""
		if not self.host.dead:
			dmg = diceroll("1d3")
			msg += "%s looses %d hp due to bleeding.\n"%(self.host.short_desc.capitalize(), dmg)
			msg += self.host.damage(dmg, self.granted_by)
		msg += super(Bleeding, self).on_round()
		return msg

	def on_applied(self):
		msg = super(Bleeding, self).on_applied()
		msg += "%s has a major bleeding!.\n"%(self.host.short_desc.capitalize())
		return msg

	def on_lifted(self):
		return "%s is no longer bleeding!\n"%(self.host.short_desc.capitalize())


class Burning(Modifier): #simply adds defence, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = ["on fire"]
	def __init__(self, granted_by, host, duration=6, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="burning", description="Loose 1d9 hp every turn for 2-4 rounds and suffer an intelligence penalty."):
		duration = clamp( 10 - host.characteristics["vitality"]*2, 2, 4)
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description )

	def on_round(self):
		msg = ""
		if not self.host.dead and not "fire resistant" in self.host.tags:
			dmg = diceroll("1d9")
			msg += "%s looses %d hp due to burning!\n"%(self.host.short_desc.capitalize(), dmg)
			msg += self.host.damage(dmg, self.granted_by)
		msg += super(Burning, self).on_round()
		return msg

	def can_apply(self):
		return not "fire resistant" in self.host.tags

	def on_applied(self):
		msg = super(Burning, self).on_applied()
		msg += "%s is set on fire!.\n"%(self.host.short_desc.capitalize())
		return msg

	def on_lifted(self):
		return "%s is no longer on fire!\n"%(self.host.short_desc.capitalize())



class Shielded(Modifier): #simply adds defence, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {}
	stats_change =  {"defence":"3d6"}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, duration=2, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="shielded", description="grants defence") :
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description)

	def on_applied(self):
		msg = super(Shielded, self).on_applied()
		msg += "%s raises his shieldup and gains a %s defence for the next turn.\n"%(self.host.short_desc, self.stats_change["defence"])
		return msg

	def on_lifted(self):
		return "%s is no longer protected by his shield!\n"%(self.host.short_desc.capitalize())

class Bonus(Modifier): #simply adds defence, hinders evasion
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="bonus", description="???"):
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted, priority, name, description)

class Regeneration(Modifier): #simply adds defence, hinders evasion
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="regeneration", description="Regenerate health.") :
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description )
		self.healing_amount = self.granted_by.stats["healing_amount"]
		self.healing_chance = self.granted_by.stats["healing_chance"]

	def on_round(self):
		chance = diceroll(self.healing_chance)
		msg = ""
		if random.randint(0, 100) < chance:
			heal = diceroll(self.healing_amount)
			if self.host.health < self.host.stats["max_health"]: 
				self.host.health += heal
				msg += "%s regenerates %d hp due to %s.\n"%(self.host.short_desc.capitalize(), heal, self.granted_by.name)
		msg += super(Regeneration, self).on_round()
		return msg

class FireAttack(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, duration=-1, characteristics_change = {}, stats_change = {}, abilities_granted = [], tags_granted = [], priority=0, name="fire attack",  description="Has a chance to cause fire additional damage every attack by host."):
		Modifier.__init__(self, granted_by, host, duration, characteristics_change, stats_change, abilities_granted, tags_granted,priority, name, description)

	def on_hit(self, attack_info):
		if attack_info.inhibitor == self.host:
			fire_chance = self.granted_by.stats["fire_chance"]
			fire_damage = self.granted_by.stats["fire_damage"]
			if attack_info.use_info["did_hit"] and not attack_info.target.dead and not "fire resistant" in attack_info.target.tags:
				chance = diceroll( fire_chance )
				if random.randint(0, 100) < chance:
					dmg = diceroll( fire_damage )
					attack_info.target.damage( dmg, self.host )
					attack_info.description += "%s causes %d fire damage to %s.\n"%(self.granted_by.name.capitalize(), dmg, attack_info.target.short_desc.capitalize())
					attack_info.use_info["damage_dealt"] += dmg

					chance_to_cause_burning = 1/2 * chance
					if random.randint(0, 100) < chance_to_cause_burning:
						modifier = get_modifier_by_name("burning", self.granted_by, attack_info.target)
						attack_info.use_info["modifiers_applied"].append(get_modifier_by_name("burning", self.granted_by, attack_info.target))
		return attack_info

def get_modifier_by_name(modifier_name, source, target, params={}):
	prototype = modifier_listing[modifier_name]
	if not "duration" in params.keys():
		params["duration"] = prototype.duration
	if not "characteristics_change" in params.keys():
		params["characteristics_change"] = prototype.characteristics_change
	if not "stats_change" in params.keys():
		params["stats_change"] = prototype.stats_change
	if not "abilities_granted" in params.keys():
		params["abilities_granted"] = prototype.abilities_granted
	if not "tags_granted" in params.keys():
		params["tags_granted"] = prototype.tags_granted
	if not "priority" in params.keys():
		params["priority"] = prototype.priority
	mod = prototype(source, target, params["duration"], params["characteristics_change"], params["stats_change"], params["abilities_granted"], params["tags_granted"], params["priority"])
	return mod

modifier_listing = {
	"shielded" : Shielded,
	"bonus" : Bonus,
	"regeneration": Regeneration,
	"fire_attack" : FireAttack,
	"vunerable": Vunerable,
	"knockdown": KnockedDown,
	"bleeding": Bleeding,
	"pain": Pain, 
	"burning": Burning,
}

item_modifiers = [] # modifiers that can be used in items.