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
	def __init__(self, granted_by, host, stats = {},  name="", description=""):
		self.uid = get_uid()
		self.name = name
		self.description = description
		self.granted_by = granted_by
		self.host = host
		#duration: -1 means permanent, number above 0 means turns left
		self.stats = stats.copy()

	def apply(self):
		added = self.host.add_modifier(self)
		if not added == False:
			msg = self.on_applied() + self.host.on_modifier_applied(self)
			return msg
		return ""


	def get_randomized_params_for_coolity(mod_class, stats, coolity):
		if not "characteristics_change" in stats:
			stats["characteristics_change"] = mod_class.characteristics_change
		if not "stats_change" in stats:
			stats["stats_change"] = mod_class.stats_change
		if not "duration" in stats:
			stats["duration"] = mod_class.duration
		if not "priority" in stats:
			stats["priority"] = mod_class.priority
		if not "abilities_granted" in stats:
			stats["abilities_granted"] = mod_class.abilities_granted
		if not "tags_granted" in stats:
			stats["tags_granted"] = mod_class.tags_granted

		real_stats = stats.copy()
		for key in list(stats.keys()):
			if not key in ["tags_granted", "modifiers_granted", "abilities_granted"]:
				if isinstance(stats[key], list) and len(stats[key])>0: #is a dice range
					if isinstance( stats[key][0], str):
						real_stats[key] = get_dice_in_range(stats[key], coolity)
					if isinstance( stats[key][0], int):
						real_stats[key] = get_number_in_range(stats[key], coolity)
				if isinstance(stats[key], dict):
					for stat in stats[key]:
						if isinstance(stats[key][stat], list) and len(stats[key][stat])>0:
							if isinstance( stats[key][stat][0], str):
								real_stats[key][stat] = get_dice_in_range(stats[key][stat], coolity)
							if isinstance( stats[key][stat][0], int):
								real_stats[key][stat] = get_number_in_range(stats[key][stat], coolity)
		return real_stats


	def can_apply(self):
		return True

	@property
	def permanent(self):
		return self.stats["duration"] == -1
	
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
			if self.stats["duration"] <= 0:
				return self.lift()
			self.stats["duration"] -= 1
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

	def on_loot(self, item_gained, source):
		pass

	def on_modifier_applied(self, modifier):
		pass

	def on_modifier_lifted(self, modifier):
		pass

	def lift(self):
		if self in self.host.modifiers:
			self.host.modifiers.remove(self)
		return self.on_lifted() + self.host.on_modifier_lifted(self)


class KnockedDown(Modifier):
	priority = 0
	duration = 0
	characteristics_change = {}
	stats_change = {}
	abilities_granted = []
	tags_granted = []

	def __init__(self, granted_by, host, stats = {}, name="knockdown", description="Loose 5d6 evasion, 2d6 your defense, and half your dexterity.") :
		Modifier.__init__(self, granted_by, host,  stats, name, description )
		self.stats["characteristics_change"] = {"dexterity": -host.base_characteristics["dexterity"]}
		self.stats["duration"] = clamp( 10 - host.characteristics["dexterity"], 1, 2)
		self.stats["stats_change"] = {"defense": "-2d6"}
	
	def can_apply(self):
		return "animate" in self.host.tags

	def on_round(self):
		msg = "%s struggles to get up from the ground.\n"%(self.host.short_desc.capitalize())
		msg += super(KnockedDown, self).on_round()
		msg = "!!\t" + msg
		return msg

	def on_lifted(self):
		return "%s gets up from the ground!\n"%(self.host.short_desc.capitalize())

	def on_applied(self):
		msg = super(KnockedDown, self).on_applied()
		msg += "%s is knocked down!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

class Vunerable(Modifier): #simply adds defense, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {}
	stats_change =  {"defense": "-3d6"}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="vunerable", description="Loose 3d6 defense for a turn."):
		Modifier.__init__(self, granted_by, host,  stats, name, description )

	def can_apply(self):
		return "animate" in self.host.tags

	def on_applied(self):
		msg = super(Vunerable, self).on_applied()
		msg += "%s is exposed and vunerable!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

	def on_lifted(self):
		msg = "%s is no longer vunerable!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

class Pain(Modifier): #simply adds defense, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {"dexterity":-3, "strength":-3, "intelligence":-3}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="pain", description="Loose 3 dexterity, strength and intelligence for a turn.") :
		Modifier.__init__(self, granted_by, host,  stats, name, description )
		self.stats["characteristics_change"] = {"dexterity":-1, "strength":-2, "intelligence":-3}
		self.stats["duration"] = Pain.duration


	def can_apply(self):
		return "animate" in self.host.tags

	def on_applied(self):
		msg = super(Pain, self).on_applied()
		msg += "%s is wrecked with pain!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

	def on_lifted(self):
		msg = "%s is no longer in pain!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

class Fear(Modifier):
	priority = 0
	duration = 2
	characteristics_change = {"dexterity":-1, "intelligence":-2}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="fear", description="Loose 2 dexterity and intelligence."):
		Modifier.__init__(self, granted_by, host,  stats, name, description )
		self.stats["characteristics_change"] = {"dexterity":-1, "intelligence":-2}
		self.stats["duration"] = clamp( 10 - host.characteristics["intelligence"], 1, 3)

	def can_apply(self):
		return "animate" in self.host.tags and "living" in self.host.tags

	def on_applied(self):
		msg = super(Fear, self).on_applied()
		msg += "%s's blood runs cold of fear!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

	def on_lifted(self):
		msg = "%s regains control over his emotions and is no longer in fear.\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

class Bleeding(Modifier): #simply adds defense, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host,stats = {}, name="bleeding", description="loose 1d3 hp every turn for 6 rounds"):
		Modifier.__init__(self, granted_by, host,  stats, name, description )
		self.stats["duration"] = clamp( 10 - host.characteristics["vitality"], 3, 8)

	def can_apply(self):
		return "living" in self.host.tags

	def on_round(self):
		msg = ""
		if not self.host.dead:
			dmg = diceroll(str(int(self.host.characteristics["vitality"]/2))+"d"+str(self.host.characteristics["vitality"]))
			msg += "!!\t%s looses %d hp due to bleeding.\n"%(self.host.short_desc.capitalize(), dmg)
			msg += self.host.damage(dmg, self.granted_by, True)
		msg += super(Bleeding, self).on_round()
		
		return msg

	def on_applied(self):
		msg = super(Bleeding, self).on_applied()
		msg += "%s has a major bleeding!.\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

	def on_lifted(self):
		msg = "%s is no longer bleeding!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg


class Burning(Modifier): #simply adds defense, hinders evasion
	priority = 0
	duration = 2
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = ["on fire"]
	def __init__(self, granted_by, host, stats = {}, name="burning", description="Loose 1d9 hp every turn for 2-4 rounds and suffer an intelligence penalty."):
		Modifier.__init__(self, granted_by, host,  stats, name, description )
		self.stats["duration"] = clamp( 10 - host.characteristics["vitality"]*2, 2, 4)

	def on_round(self):
		msg = ""
		if not self.host.dead and not "fire resistant" in self.host.tags:
			dmg = diceroll("1d9")
			msg += "!!\t%s looses %d hp due to burning!\n"%(self.host.short_desc.capitalize(), dmg)
			msg += self.host.damage(dmg, self.granted_by, True)
		msg += super(Burning, self).on_round()
		return msg

	def can_apply(self):
		return not "fire resistant" in self.host.tags

	def on_applied(self):
		msg = super(Burning, self).on_applied()
		msg += "%s is set on fire!.\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

	def on_lifted(self):
		msg = "%s is no longer on fire!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg



class Shielded(Modifier): #simply adds defense, hinders evasion
	priority = 0
	duration = 1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="shielded", description="grants defense") :
		Modifier.__init__(self, granted_by, host, stats, name, description)
		if not "defense" in self.stats["stats_change"]:
			self.stats["stats_change"]["defense"] = self.granted_by.stats["defense"]
		if not "evasion" in self.stats["stats_change"]:
			self.stats["stats_change"]["evasion"] = self.granted_by.stats["evasion"]

	def on_applied(self):
		msg = super(Shielded, self).on_applied()
		msg += "%s gains a %s defense and %s evasion penalty for the next %d rounds.\n"%(self.host.short_desc, self.stats["stats_change"]["defense"], self.stats["stats_change"]["evasion"], self.stats["duration"])
		msg = "!!\t" + msg
		return msg

	def on_lifted(self):
		msg = "%s is no longer shielded!\n"%(self.host.short_desc.capitalize())
		msg = "!!\t" + msg
		return msg

class Bonus(Modifier): #simply adds defense, hinders evasion
	def __init__(self, granted_by, host, stats = {}, name="bonus", description="???"):
		Modifier.__init__(self, granted_by, host, stats, name, description)

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		name = ""
		self_class = Bonus

		possible_chars = ["strength", "dexterity", "vitality", "intelligence"]
		possible_stats = ["max_health", "max_energy", "defense", "evasion"]
		pool = possible_chars
		stats = {}

		chars_or_stats = "characteristics_change"
		if random.randint(0, 1) == 1:
			chars_or_stats = "stats_change"
			pool = possible_stats

		stat_range = [1, 4]
		stat = random.choice(pool)
		if stat == "max_health":
			stat_range = [10, 100]
		if stat == "max_energy":
			stat_range = [1, 2]
		if stat == "defense":
			stat_range = ["1d3", "2d6"]
		if stat == "evasion":
			stat_range = ["1d3", "2d6"]

		stats[chars_or_stats] = { stat: stat_range }
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		name = " ".join(stat.split("_"))
		return {"name": "bonus", "stats":stats} 

class Nerf(Modifier): #simply adds defense, hinders evasion
	def __init__(self, granted_by, host, stats = {}, name="nerf", description="???"):
		Modifier.__init__(self, granted_by, host, stats, name, description)

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		name = ""
		self_class = Nerf

		possible_chars = ["strength", "dexterity", "vitality", "intelligence"]
		possible_stats = ["max_health", "max_energy"]
		pool = possible_chars
		stats = {}

		chars_or_stats = "characteristics_change"
		if random.randint(0, 1) == 1:
			chars_or_stats = "stats_change"
			pool = possible_stats

		stat_range = [-4, -1]

		stat = random.choice(pool)
		if stat == "max_health":
			stat_range = [-100, -10]
		if stat == "max_energy":
			stat_range = [-2, 1]
		if stat == "defense":
			stat_range = ["-2d6", "-1d3"]
		if stat == "evasion":
			stat_range = ["-2d6", "-1d3"]

		stats[chars_or_stats] = { stat: stat_range }
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		name = " ".join(stat.split("_"))
		return {"name": "nerf", "stats":stats} 

class Regeneration(Modifier): #simply adds defense, hinders evasion
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host,  stats= {}, name="regeneration", description="Regenerate health.") :
		Modifier.__init__(self, granted_by, host,  stats, name, description )

	def on_round(self):
		chance = diceroll(self.stats["healing chance"])
		msg = ""
		print(chance)
		if random.randint(0, 100) < chance:
			heal = diceroll(self.stats["healing amount"])
			if self.host.health < self.host.stats["max_health"]: 
				self.host.health += heal
				msg += "!!\t%s regenerates %d hp due to %s.\n"%(self.host.short_desc.capitalize(), heal, self.granted_by.name)
		msg += super(Regeneration, self).on_round()
		return msg

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Regeneration
		stats = {}
		stats["healing amount"] = ["1d4", "4d6"]
		stats["healing chance"] = ["1d4", "4d6"]

		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"regeneration", "stats":stats} 

class Sickness(Modifier): #simply adds defense, hinders evasion
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host,  stats= {}, name="sickness", description="Sometimes takes away health.") :
		Modifier.__init__(self, granted_by, host,  stats, name, description )

	def on_round(self):
		chance = diceroll(self.stats["sickness chance"])
		msg = ""
		if random.randint(0, 100) < chance:
			loss = diceroll(self.stats["sickness amount"])

			self.host.damage(loss, self, True)
			msg += "!!\t%s looses %d hp due to %s.\n"%(self.host.short_desc.capitalize(), loss, self.granted_by.name)
		msg += super(Regeneration, self).on_round()
		return msg

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Regeneration
		stats = {}
		stats["sickness amount"] = ["4d6", "1d4"]
		stats["sickness chance"] = ["4d6", "1d4"]

		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"sickness", "stats":stats} 

class FireAttack(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="fire attack",  description="Has a chance to cause fire  damage every attack by host."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_hit(self, attack_info):
		if attack_info.inhibitor == self.host:
			fire_chance = self.stats["fire chance"]
			fire_damage = self.stats["fire damage"]
			if attack_info.use_info["did_hit"] and not attack_info.target.dead and not "fire resistant" in attack_info.target.tags:
				chance = diceroll( fire_chance )
				if random.randint(0, 100) < chance:
					dmg = diceroll(fire_damage)
					attack_info.target.damage(dmg, self.host, True)
					attack_info.description += "!!\t%s causes %d fire damage to %s.\n"%(self.granted_by.name.capitalize(), dmg, attack_info.target.short_desc.capitalize())

					chance_to_cause_burning = 1/2 * chance
					if random.randint(0, 100) < chance_to_cause_burning:
						modifier = get_modifier_by_name("burning", self.granted_by, attack_info.target)
						attack_info.use_info["modifiers_applied"].append(modifier)
		return attack_info

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Regeneration
		stats = {}
		stats["fire damage"] = ["1d3", "2d6"]
		stats["fire chance"] = ["1d3", "2d6"]

		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"fire attack", "stats":stats} 

class ElectricityAttack(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="electricity attack",  description="Has a chance to cause electrical damage every attack by host."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_hit(self, attack_info):
		if attack_info.inhibitor == self.host:
			electricity_chance = self.stats["electricity chance"]
			electricity_damage = self.stats["electricity damage"]
			if attack_info.use_info["did_hit"] and not attack_info.target.dead and not "electricity resistant" in attack_info.target.tags:
				chance = diceroll( electricity_chance )
				if random.randint(0, 100) < chance:
					dmg = diceroll( electricity_damage )
					attack_info.target.damage(dmg, self.host, True)
					attack_info.description += "!!\t%s causes %d electricity damage to %s.\n"%(self.granted_by.name.capitalize(), dmg, attack_info.target.short_desc.capitalize())

					chance_to_cause_pain = 1/2 * chance
					if random.randint(0, 100) < chance_to_cause_pain:
						modifier = get_modifier_by_name("pain", self.granted_by, attack_info.target)
						attack_info.use_info["modifiers_applied"].append(modifier)
		return attack_info

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Regeneration
		stats = {}
		stats["electricity damage"] = ["1d3", "2d6"]
		stats["electricity chance"] = ["1d3", "2d6"]

		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"electricity attack", "stats":stats} 



class Energy(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="energy",  description="Sometimes gives additional energy."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_round(self):
		chance = diceroll(self.stats["energy chance"])
		amount = diceroll(self.stats["energy amount"])
		msg = ""
		if random.randint(0, 100) < chance:
			self.host.energy += amount
			msg += "!!\t%s provides %s with %d energy.\n"%(self.granted_by.name.capitalize(), self.host.name.capitalize(), amount)

		msg += super(Energy, self).on_round()
		return msg

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Energy
		stats = {}
		stats["energy chance"] = ["1d3", "4d6"]
		stats["energy amount"] = ["1d1", "1d3"]
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"energy", "stats":stats} 

class Weakness(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="weakness",  description="Sometimes drains energy of host."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)
	def on_round(self):
		chance = diceroll(self.stats["weakness chance"])
		amount = diceroll(self.stats["weakness amount"])
		msg = ""
		if random.randint(0, 100) < chance:
			self.host.energy += amount
			msg += "!!\t%s drains %d energy from %s.\n"%(self.granted_by.name.capitalize(), amount, self.host.name.capitalize())

		msg += super(Weakness, self).on_round()
		return msg

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Weakness
		stats = {}
		stats["weakness chance"] = ["4d6", "1d3"]
		stats["weakness amount"] = ["1d3", "1d1"]
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"weakness", "stats":stats} 

class Wisdom(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="wisdom",  description="Sometimes gives additional experience."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_experience_gain(self, value):
		chance = diceroll(self.stats["wisdom chance"])
		desc = ""
		if random.randint(0, 100) < chance:
			additional_gain = int(value * diceroll(self.stats["wisdom amount"] )/100)
			value = value + additional_gain
			desc = "!!\t%s earns %d additional experience due to %s.\n"%(self.host.name.capitalize(), additional_gain, self.granted_by.name)
		return desc, value

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Wisdom
		stats = {}
		stats["wisdom chance"] = ["1d3", "3d6"]
		stats["wisdom amount"] = ["1d5", "1d15"] #percentage
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"wisdom", "stats":stats} 

class Stupidity(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="stupidity",  description="Sometimes takes away experience."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_experience_gain(self, value):
		chance = diceroll(self.stats["stupidity chance"])
		desc = ""
		if random.randint(0, 100) < chance:
			exp_loss = int(value * diceroll(self.stats["stupidity amount"] )/100)
			value = value - exp_loss
			desc = "!!\t%s looses %d experience due to %s.\n"%(self.host.name.capitalize(), exp_loss, self.granted_by.name)
		return desc, value

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Stupidity
		stats = {}
		stats["stupidity chance"] = ["3d6", "1d3"]
		stats["stupidity amount"] = ["1d15", "1d5"] #percentage
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"stupidity", "stats":stats} 

class Suffering(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="suffering",  description="Has a chance to inflict pain to host any time."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_round(self):
		chance = diceroll(self.stats["pain chance"])
		msg = ""
		if random.randint(0, 100) < chance:
			modifier = get_modifier_by_name("pain", self.granted_by, self.host)
			self.host.add_modifier(modifier)
			msg += "!!\t%s causes extreme pain to %s.\n"%(self.granted_by.name.capitalize(), self.host.name.capitalize())

		msg += super(Suffering, self).on_round()
		return msg

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Suffering
		stats = {}
		stats["pain chance"] = ["8d6", "1d2"]
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"suffering", "stats":stats} 

class Judgement(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="judgement",  description="Has a chance to cause a lot of damage to any creature in the battle at the beginning of a round. It's not clear what judgement is behind the choice of who gets hurt, but there should be some, right?"):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_round(self):
		msg = ""
		chance = diceroll(self.stats["judgement chance"])
		judgement_damage = self.stats["judgement damage"]
		if random.randint(0, 100) < chance:
			if self.host.event and hasattr(self.host.event, "turn_queue") and len(self.host.event.turn_queue)>1:
				alive_creatues = [c for c in self.host.event.turn_queue if not c.dead]
				if len(alive_creatues)>0:
					target = random.choice(alive_creatues)
					dmg = diceroll( judgement_damage )
					msg += "!!\tA lightning erupts from %s and hits %s for %d damage.\nThe judgement has been made.\n"%(self.granted_by.name.capitalize(), target.short_desc.capitalize(), dmg)
					msg += target.damage( dmg, self )

		msg += super(Judgement, self).on_round()
		return msg

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Judgement
		stats = {}
		stats["judgement chance"] = ["8d6", "1d6"]
		stats["judgement damage"] = ["10d6", "2d6"]
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"judgement", "stats":stats} 

class Greed(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="greed",  description="Sometimes destroys dropped loot."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	
	def on_loot(self, item_gained, source):
		msg = ""
		chance = diceroll(self.stats["greed chance"])
		if random.randint(0, 100) < chance:
			if item_gained in self.host.inventory:
				self.host.inventory.remove(item_gained)
				msg = "!!\t%s destroys %s.\n"%(self.granted_by.name.capitalize(), item_gained.name)
		return msg

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Greed
		stats = {}
		stats["greed chance"] = ["8d6", "1d6"]
		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"greed", "stats":stats} 

# class Demons(Modifier):
# 	priority = 0
# 	duration = -1
# 	characteristics_change = {}
# 	stats_change =  {}
# 	abilities_granted = []
# 	tags_granted = []
# 	def __init__(self, granted_by, host, stats = {}, name="demons",  description="Causes demons to invade the world at unpredictable times."):
# 		Modifier.__init__(self, granted_by, host,  stats, name, description)

# 	def on_round(self):
# 		msg = ""
# 		chance = diceroll(self.stats["demons chance"])
# 		demons_amount = diceroll(self.stats["demons amount"])
# 		possible_demons = ["lesser demon"]
# 		if random.randint(0, 100) < chance:
# 			demon = enemy_list[random.choice(possible_demons)]
# 			demons = []
# 			for x in range(1, demons_amount):
# 				lvl = random.randint(1, clamp(int(self.host.lvl/3), 1, 20))
# 				demons.append(demon(lvl))
# 			msg += "%d demons invade the world.\n"%(demons_amount)
# 		self.host.event.enemies = self.host.event.enemies + demons
# 		self.host.event.update_turn_queue()
# 		msg += super(Demons, self).on_round()
# 		return msg

	# @staticmethod
	# def get_randomized_params_for_coolity(coolity):
	# 	self_class = Demons
	# 	stats = {}
	# 	stats["demons chance"] = ["1d6", "1d2"]
	# 	stats["demons amount"] = ["1d3", "1d1"]
	# 	stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
	# 	return {"name":"demons", "stats":stats} 


class HurtUndead(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="hurt undead",  description="More damage against undead."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_hit(self, attack_info):
		if attack_info.inhibitor == self.host:
			additional_damage =int(attack_info.use_info["damage_dealt"] * diceroll(self.stats["additional damage to undead"])/100)
			if attack_info.use_info["did_hit"] and not attack_info.target.dead and "undead" in attack_info.target.tags:
				attack_info.target.damage(additional_damage, self.host, True)
				attack_info.description += "!!\t%s takes additional %d damage because of %s.\n"%(attack_info.target.short_desc.capitalize(), additional_damage, self.granted_by.name)
		return attack_info

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = HurtUndead
		stats = {}
		stats["additional damage to undead"] = ["1d5", "10d5"]

		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"hurt undead", "stats":stats} 

class HurtDemons(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="hurt demons",  description="More damage against demons."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_hit(self, attack_info):
		if attack_info.inhibitor == self.host:
			additional_damage = int(attack_info.use_info["damage_dealt"] * diceroll(self.stats["additional damage to demons"])/100)
			if attack_info.use_info["did_hit"] and not attack_info.target.dead and "demon" in attack_info.target.tags:
				attack_info.target.damage(additional_damage, self.host, True)
				attack_info.description += "!!\t%s takes additional %d damage because of %s.\n"%(attack_info.target.short_desc.capitalize(), additional_damage, self.granted_by.name)
		return attack_info

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = HurtDemons
		stats = {}
		stats["additional damage to demons"] = ["1d5", "10d5"]

		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"hurt demons", "stats":stats} 

class Vampirism(Modifier):
	priority = 0
	duration = -1
	characteristics_change = {}
	stats_change =  {}
	abilities_granted = []
	tags_granted = []
	def __init__(self, granted_by, host, stats = {}, name="vampirism",  description="Returns some of the damage dealt as health."):
		Modifier.__init__(self, granted_by, host,  stats, name, description)

	def on_hit(self, attack_info):
		if attack_info.inhibitor == self.host and self.host.health < self.host.stats["max_health"]:
			regen = int(attack_info.use_info["damage_dealt"] * diceroll(self.stats["vampirism amount"])/100)
			if attack_info.use_info["did_hit"] and not attack_info.target.dead and "living" in attack_info.target.tags:
				attack_info.description += "!!\t%s regenerates %d healh because of %s.\n"%(self.host.name.capitalize(), regen, self.name)
				self.host.health += regen
		return attack_info

	@staticmethod
	def get_randomized_params_for_coolity(coolity):
		self_class = Vampirism
		stats = {}
		stats["vampirism amount"] = ["1d5", "10d5"]

		stats = Modifier.get_randomized_params_for_coolity(self_class, stats, coolity)
		return {"name":"vampirism", "stats":stats} 


def get_modifier_by_name(modifier_name, source, target, stats={}):
	prototype = modifier_listing[modifier_name]

	if not "duration" in stats.keys():
		stats["duration"] = prototype.duration
	if not "characteristics_change" in stats.keys():
		stats["characteristics_change"] = prototype.characteristics_change.copy()
	if not "stats_change" in stats.keys():
		stats["stats_change"] = prototype.stats_change.copy()
	if not "abilities_granted" in stats.keys():
		stats["abilities_granted"] = prototype.abilities_granted.copy()
	if not "tags_granted" in stats.keys():
		stats["tags_granted"] = prototype.tags_granted.copy()
	if not "priority" in stats.keys():
		stats["priority"] = prototype.priority
	
	mod = prototype(source, target, stats)
	return mod

def get_random_modifiers_for_coolity(coolity):

	granted_modifiers = []

	got_modifier = get_number_in_range([0, 100], coolity)
	chance_for_modifier = clamp(coolity*100, 25, 100)

	if got_modifier < chance_for_modifier:
		modifiers_type = None
		drop_type = get_number_in_range([0, 100], coolity)
		bad_limit = 20
		average_limit = 80

		max_modifiers = 3
		if drop_type <= bad_limit:
			modifiers_type = "bad"
			#got bad
		elif drop_type > average_limit:
			modifiers_type = "good"
			#got only good

		amount_of_modifiers = get_number_in_range([1, max_modifiers], 0)
		if modifiers_type == "good":
			modifier_pool = good_item_modifiers.copy()
		elif modifiers_type == "bad":
			modifier_pool = bad_item_modifiers.copy()
		else:
			modifier_pool = good_item_modifiers.copy() + bad_item_modifiers.copy()
		for x in range(amount_of_modifiers):
			if len(modifier_pool) < 1:
				break

			modifier_name = random.choice(modifier_pool)
			modifier_pool.remove(modifier_name)
			modifier = modifier_listing[modifier_name]
			modifier_object = modifier.get_randomized_params_for_coolity(coolity)
			granted_modifiers.append(modifier_object)
	return granted_modifiers

modifier_listing = {
	"shielded" : Shielded,
	"bonus" : Bonus,
	"nerf" : Nerf,
	
	
	"vunerable": Vunerable,
	"knockdown": KnockedDown,
	"bleeding": Bleeding,
	"pain": Pain, 
	"burning": Burning,
	"fear": Fear,

	"suffering": Suffering,
	"judgement": Judgement,
	"fire attack" : FireAttack,
	"electricity attack": ElectricityAttack,
	"regeneration": Regeneration,
	"sickness":Sickness,
	# "demons": Demons,
	"greed": Greed,
	"wisdom": Wisdom,
	"stupidity": Stupidity,
	"energy": Energy,
	"weakness": Weakness,
	"hurt undead": HurtUndead,
	"hurt demons": HurtDemons,
	"vampirism": Vampirism,

}

good_item_modifiers = ["fire attack", "electricity attack", "regeneration", "wisdom", "energy", "hurt undead", "hurt demons", "vampirism", "bonus"]
bad_item_modifiers = ["judgement", "suffering", "greed", "stupidity", "weakness", "nerf"]