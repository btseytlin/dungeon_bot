#!/usr/bin/env python3
import json
import random
from .util import *
from .modifiers import *


class LevelPerk(object): #LevelPerks always affect only the host that carries them
	name = "Unfinished perk"
	description = "Report this bug"
	requirements = {

	}
	characteristics_change = {}
	stats_change = {}
	abilities_granted = []
	modifiers_granted = []
	tags_granted = []
	priority = 0
	def __init__(self, host):
		self.uid = get_uid()
		self.host = host

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

	def on_level_up(self):
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

	def on_experience_gain(self, value):
		return "", value

	def on_energy_gained(self, amount=None):
		pass

	def on_energy_lost(self, amount=None):
		pass

	def on_health_gained(self, amount=None):
		pass

	def on_health_lost(self, amount=None):
		pass

	def on_loot(self, item_gained, source):
		return ""

	def on_modifier_applied(self, modifier):
		pass

	def on_modifier_lifted(self, modifier):
		pass


""" General tree """
class TeamTactics(LevelPerk):
	name = "Team tactics"
	description = "Get +1 energy regen for each player in lobby, but not more than 3."
	priority = 0
	requirements = {
		"level": 1,
		"has_perks": [],
		"characteristics": {
			"intelligence": 5
		}
	}

	def __init__(self, host):
		LevelPerk.__init__(self, host)

	def on_combat_start(self):
		combat_event = self.host.event
		players = combat_event.players
		other_players_num = clamp( len(players)-1, 0, 3)
		if other_players_num > 0:
			modifier = get_modifier_by_name("bonus", self, self.host, {"stats_change": {"energy_regen": other_players_num}, "duration": -1 })
			mod_added = self.host.add_modifier(modifier)
			if mod_added:
				return "!!\t%s gains %s max energy by using team tactics.\n"%(self.host.name.capitalize(), other_players_num)
		return ""

class Looter(LevelPerk):
	name = "Looter"
	description = "Get more loot."
	priority = 0
	requirements = {
		"level": 10,
		"has_perks": [],
		"characteristics": {
		}
	}

	def __init__(self, host):
		LevelPerk.__init__(self, host)

	def on_loot(self, item, source):
		description = ""
		chance = 40
		if random.randint(1, 100) < chance:
			new_items = source.drop_loot()
			if len(new_items)> 0:
				item = random.choice(new_items)
				self.host.add_to_inventory(item)

				if self.host.add_to_inventory(item):
					description += "!!\t%s got additional loot as a skilled looter: %s.\n"%(self.host.name.capitalize(), item.full_name)
				else:
					description += "!!\t%s got additional loot: %s, but didn't have enough space in inventory.\n"%(self.host.name.capitalize(), item.name)
		return description


""" Tank tree """
class Legionaire(LevelPerk):
	name = "Legionaire"
	description = "Get much more defense when putting your shield up. This is the first step to become an unbeatable soldier."
	priority = 0
	requirements = {
		"level": 5,
		"has_perks": [],
		"characteristics": {
			"vitality": 6,
		}
	}

	def on_modifier_applied(self, modifier):
		msg = ""
		if modifier.name == "shielded" and hasattr(modifier.granted_by, "tags_granted"):
			modifier.stats["stats_change"]["defense"] = str(int(modifier.stats["stats_change"]["defense"].split('d')[0])*2) + 'd' + str(int(modifier.stats["stats_change"]["defense"].split('d')[1]))
			msg = "!!\tThe defense bonus is stronger due to legionaire training!"
		return msg

class Knight(LevelPerk):
	name = "Knight"
	description = "Take only half the dexterity penalties when wearing armor."
	priority = 0
	requirements = {
		"level": 10,
		"has_perks": ["Legionaire"],
		"characteristics": {
			"vitality": 6,
		}
	}

	def __init__(self, host):
		LevelPerk.__init__(self, host)
		self.bonus = None
		self.item = None

	def on_combat_start(self):
		if not self.bonus and self.host.armor:
			self.on_item_equipped(self.host.armor)

	def on_item_equipped(self, item):
		if item.item_type == "armor":
			if "characteristics_change" in item.stats.keys() and "dexterity" in item.stats["characteristics_change"].keys() and item.stats["characteristics_change"]["dexterity"]<-1:
				modifier = get_modifier_by_name("bonus",self, self.host, {"duration":-1, "characteristics_change":{"dexterity": abs(int(item.stats["characteristics_change"]["dexterity"]/2))}})
				self.item = item
				mod_added = self.host.add_modifier(modifier)
				if mod_added:
					self.bonus = modifier

	def on_item_unequipped(self, item):
		if item == self.item:
			if self.bonus:
				self.bonus.lift()


class Berserk(LevelPerk):
	name = "Berserk"
	description = "Chance to get enraged when taking damage, gaining a bonus to strength and dexterity."
	priority = 0
	requirements = {
		"level": 10,
		"has_perks": ["Legionaire"],
		"characteristics": {
			"vitality": 6,
		}
	}

	def on_health_lost(self, value):
		
		msg = ""
		chance = clamp((value / self.host.stats["max_health"]) * 100, 0, 95)
		if random.randint(1, 100) < chance:
			modifier = get_modifier_by_name("bonus", self, self.host, {"duration":2, "characteristics_change":{"strength": 2, "dexterity": 2}})
			mod_added = self.host.add_modifier(modifier)
			if mod_added:
				msg = "!!\t%s is enraged!\n"%(self.host.name.capitalize())
		return msg


""" Damage Dealer tree """
class Sweeper(LevelPerk):
	name = "Sweeper"
	description = "Get an accuracy bonus when surrounded by 4 or more enemies. It's the first step to become a master killer."
	priority = 0
	requirements = {
		"level": 5,
		"has_perks": [],
		"characteristics": {
			"strength": 6,
		}
	}

	def on_round(self):
		msg = ""
		if self.host.event:
			combat_event = self.host.event
			if len([c for c in combat_event.turn_queue if c.__class__.__name__ != "Player" and not c.dead])>=4:
				modifier = get_modifier_by_name("bonus", self, self.host, {"duration":1, "stats_change":{"accuracy": "3d6"}})
				mod_added = self.host.add_modifier(modifier)
				if mod_added:
					msg = "!!\t%s gains a 4d4 accuracy bonus due to being surrounded by enemies.\n"%(self.host.name.capitalize())
		return msg

class Flow(LevelPerk):
	name = "Flow"
	description = "Get 35 percent chance to recover 2 energy on kill."
	priority = 0
	requirements = {
		"level": 10,
		"has_perks": ["Sweeper"],
		"characteristics": {
			"strength": 6
		}
	}

	def on_kill(self, ability_info):
		if ability_info.inhibitor == self.host and random.randint(0,100) < 35:
			ability_info.inhibitor.energy += 2
			ability_info.description += "!!\t%s recovers 2 energy!\n"%(self.host.name.capitalize())
		return ability_info

class Deft(LevelPerk):
	name = "Deft"
	description = "Get a 30 percent chance to recover 1 energy after a miss."
	priority = 0
	requirements = {
		"level": 10,
		"has_perks": ["Sweeper"],
		"characteristics": {
			"strength": 6,
		}
	}

	def on_miss(self, ability_info):
		if ability_info.use_info["energy_change"] < -1:
			if random.randint(0, 100) < 30:
				ability_info.inhibitor.energy += 1
				ability_info.description += "!!\t%s recovers 1 energy!\n"%(ability_info.inhibitor.name.capitalize())
				return ability_info
		return ability_info



""" Mage tree """
class Educated(LevelPerk):
	name = "Educated"
	description = "Get 10 percent additional experience. Being educated is the first step to mastering to magic arts."
	priority = 0
	requirements = {
		"level": 5,
		"has_perks": [],
		"characteristics": {
			"intelligence": 5
		}
	}

	def __init__(self, host):
		LevelPerk.__init__(self, host)

	def on_experience_gain(self, value):
		additional_gain =value * 0.10
		value = value + additional_gain
		desc = "!!\t%s earns %d additional experience due to being educated.\n"%(self.host.name.capitalize(), additional_gain)
		return desc, value

class Mage(LevelPerk):
	name = "Mage"
	description = "Get spells: heal, fireball, mass shield."
	priority = 0
	requirements = {
		"level": 10,
		"has_perks": ["Educated"],
		"characteristics": {
			"intelligence": 6,
		}
	}

	abilities_granted = [ "heal", "fireball", "mass shield"]

class Necromancer(LevelPerk):
	name = "Necromancer"
	description = "Get spells: vampirism aura, lightning, mass pain."
	priority = 0
	requirements = {
		"level": 10,
		"has_perks": ["Educated"],
		"characteristics": {
			"intelligence": 6,
		}
	}

	abilities_granted = [ "vampirism aura", "lightning", "mass pain" ]

level_perks_listing = {
	#mage tree
	"Educated":Educated,
	"Mage":Mage,
	"Necromancer":Necromancer,

	#damage tree
	"Sweeper": Sweeper,
	"Flow": Flow,
	"Deft": Deft,

	#tank tree
	"Legionaire": Legionaire,
	"Knight": Knight,
	"Berserk": Berserk,

	#general tree
	"Team tactics": TeamTactics,
	"Looter": Looter,

}
