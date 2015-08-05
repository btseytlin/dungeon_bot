#!/usr/bin/env python3
from .util import *
class Item(object):
	def __init__(self, name, description, item_type,  stats = {},  abilities_granted = [], modifiers_granted = [], requirements = None, tags_granted = []):
		self.name = name
		self.description = description
		self.requirements = requirements.copy()
		self.item_type = item_type
		self.uid = get_uid()
		self.abilities_granted = abilities_granted.copy()
		self.stats = stats.copy()
		self.modifiers_granted = modifiers_granted.copy()
		self.tags_granted = tags_granted.copy()

	@property
	def short_desc(self):
	    return self.name
	

	def use(self, user, target ):
		return "Can't use %s."%(self.name)

	def examine_self(self):
		requirements = []
		for x in list(self.requirements.keys()):
				requirements.append("|\t"+x+":" +str(self.requirements[x])) 

		stats = []

		for x in list(self.stats.keys()):
			if isinstance(self.stats[x], dict):
				for stat in list(self.stats[x].keys()):
					stats.append("|\t"+str(stat)+":" +str(self.stats[x][stat])) 
			else:
				stats.append("|\t"+x+":" +str(self.stats[x])) 


		desc = "\n".join([
				"%s, %s."%(self.name.title(), self.item_type),
				"%s"%(self.description or ""),
				"Requirements:\n%s"%(", ".join(requirements)),
				"Stats:\n%s"%(", ".join(stats)),
				"Abilities granted:\n|\t%s"%(", ".join(self.abilities_granted)),
				"Modifiers granted:\n|\t%s"%(", ".join([modifier["name"] for modifier in self.modifiers_granted])),
				"Tags granted:\n|\t%s"%(", ".join(self.tags_granted)),
			])
		return desc

	def to_json(self):
		big_dict = self.__dict__.copy()
		big_dict["requirements"] = self.requirements
		big_dict["abilities_granted"] = self.abilities_granted
		big_dict["stats"] = self.stats
		big_dict["modifiers_granted"] = self.modifiers_granted
		return big_dict

	@staticmethod
	def de_json(data):
		if data.get("item_type") == "primary_weapon":
			return PrimaryWeapon.de_json(data)
		if data.get("item_type") == "secondary_weapon":
			return SecondaryWeapon.de_json(data)
		if data.get("item_type") == "armor":
			return Armor.de_json(data)
		if data.get("item_type") == "talisman":
			return Talisman.de_json(data)
		if data.get("item_type") == "ring":
			return Ring.de_json(data)
		if data.get("item_type") == "headwear":
			return Headwear.de_json(data)
		if data.get("item_type") == "consumable":
			return None#Headwear.de_json(data)
		print('wrong item type')

default_weapon_stats= {
	"damage" : "1d1",
	"accuracy" : "1d1",
}

default_weapon_requirements = {
	"strength": 0, 
	"vitality": 0, 
	"dexterity": 0,
	"intelligence": 0, 
}	

default_weapon_abilities = []
class PrimaryWeapon(Item):
	def __init__(self, name, description, item_type="primary_weapon", stats=default_weapon_stats, abilities_granted = default_weapon_abilities, modifiers_granted = [], requirements = default_weapon_requirements, tags_granted = []):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)
	@property
	def short_desc(self):
		return self.name+" |acc:%s/dmg:%s|"%(self.stats["accuracy"], self.stats["damage"]) + ("!" if len(self.modifiers_granted)>0 else "")


	@staticmethod
	def de_json(data):
		return PrimaryWeapon(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))


class SecondaryWeapon(Item):
	def __init__(self, name, description, item_type="secondary_weapon", stats=default_weapon_stats, abilities_granted = default_weapon_abilities, modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		if "accuracy" in list(self.stats.keys()):
			return self.name+" |acc:%s/dmg:%s|"%(self.stats["accuracy"], self.stats["damage"]) + ("!" if len(self.modifiers_granted)>0 else "")
		else:
			return self.name+" |def:%s/ev:%s|"%(self.stats["defence"], self.stats["evasion"]) + ("!" if len(self.modifiers_granted)>0 else "")
		

	@staticmethod
	def de_json(data):
		return SecondaryWeapon(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))


class Armor(Item):
	def __init__(self, name, description, item_type="armor", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		return self.name+" |def:%s/ev:%s|"%(self.stats["defence"], self.stats["evasion"]) + ("!" if len(self.modifiers_granted)>0 else "")

	@staticmethod
	def de_json(data):
		return Armor(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))

class Talisman(Item):
	def __init__(self, name, description, item_type="talisman", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		return self.name+("!" if len(self.modifiers_granted)>0 else "")

	@staticmethod
	def de_json(data):
		return Talisman(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))

class Ring(Item):
	def __init__(self, name, description, item_type="ring", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		return self.name+("!" if len(self.modifiers_granted)>0 else "")

	@staticmethod
	def de_json(data):
		return Ring(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))


class Headwear(Item):
	def __init__(self, name, description, item_type="ring", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		return self.name+" |def:%s/ev:%s|"%(self.stats["defence"], self.stats["evasion"]) + ("!" if len(self.modifiers_granted)>0 else "")

	@staticmethod
	def de_json(data):
		return Headwear(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))


def get_randomized_item(prototype, coolity, stats, item_args):
		if coolity == 0:
			coolity = 0.01
		real_stats = stats.copy()
		for key in list(stats.keys()):
			if isinstance(stats[key], list): #is a dice range
				if isinstance( stats[key][0], str):
					real_stats[key] = get_dice_in_range(stats[key], coolity)
				if isinstance( stats[key][0], int):
					real_stats[key] = get_number_in_range(stats[key], coolity)
			if isinstance(stats[key], dict):
				for stat in stats[key]:
					if isinstance(stats[key][stat], list):
						if isinstance( stats[key][stat][0], str):
							real_stats[key][stat] = get_dice_in_range(stats[key][stat], coolity)
						if isinstance( stats[key][stat][0], int):
							real_stats[key][stat] = get_number_in_range(stats[key][stat], coolity)

		if not "modifiers_granted" in item_args.keys():
				item_args["modifiers_granted"] = []
		if not "requirements" in item_args.keys():
				item_args["requirements"] = {}
		if not "abilities_granted" in item_args.keys():
				item_args["abilities_granted"] = []
		if not "tags_granted" in item_args.keys():
			 item_args["tags_granted"] = []
		return prototype(item_args["name"], item_args["description"], item_args["item_type"], real_stats, item_args["abilities_granted"], item_args["modifiers_granted"], item_args["requirements"], item_args["tags_granted"])

def get_item_by_name(name, coolity=0):
	print(name)
	banned_items = ["animal_teeth", "animal_claws", "rodent_teeth"]
	if name == "random":
		names = []
		for itemtype in item_listing.keys():
			for item in item_listing[itemtype].keys():
				if not item in banned_items:
					names.append(item)
		name = random.choice(names)
	item_args = None
	item_stats = None
	item_type = None
	for key in list(item_listing.keys()):
		if name == key:
			name = random.choice([item for item in list(item_listing[key].keys()) if not item in banned_items])
			print(name)
		for item in list(item_listing[key].keys()):
			if item == name:
				item_args = item_listing[key][item]["args"]
				item_stats = item_listing[key][item]["stats"]
				item_type = key
				break

	prototype = None
	if item_type == "primary_weapon":
		prototype = PrimaryWeapon
	elif item_type == "secondary_weapon":
		prototype = SecondaryWeapon
	elif item_type == "armor":
		prototype = Armor	
	elif item_type == "talisman":
		prototype = Talisman
	elif item_type == "ring":
		prototype = Ring
	elif item_type == "headwear":
		prototype = Headwear

	if prototype:
		item_args["item_type"] = item_type
		return get_randomized_item(prototype, coolity, item_stats, item_args)
	return "Unknown item"

item_listing = { 
	"primary_weapon":{
		"rapier": {"stats": {"damage" : ["1d6","2d6"], "accuracy" : ["2d6","7d6"]} , "args":{"name":"rapier", "description":"Steel rapier!", "abilities_granted":["stab"]}},

		"club": {"stats": {"damage" : ["1d3","2d6"], "accuracy" : ["1d6","2d6"]} , "args":{"name":"club", "description":"A rough wooden club, good enough to break a skull!", "abilities_granted":["smash"]}},
		"mace": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["1d6","6d6"]} , "args":{"name":"mace", "description":"Like the club, except less bad!", "abilities_granted":["smash"]}},
		"sword": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["1d6","6d6"]} , "args":{"name":"sword", "description":"Steel sword!", "abilities_granted":["cut", "stab"]}},
		"claymore": {"stats": {"damage" : ["2d6","4d6"], "accuracy" : ["1d6","4d6"]} , "args":{"name":"claymore", "description":"A two handed sword that allows for sweeping attacks damaging many enemies at once.", "abilities_granted":["sweep", "stab"], "requirements": {"two handed": True}}},

		# enemy equipment below
		"rodent_teeth": {"stats": {"damage" : ["1d3","2d3"], "accuracy" : ["4d6", "6d6"]} , "args":{"name":"rodent teeth", "description":"Slightly sharp teeth.", "abilities_granted":["rodent bite"]}},
		"animal_teeth": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["3d6","5d6"]} , "args":{"name":"animal teeth", "description":"Sharp teeth.", "abilities_granted":["animal bite"]}},

	},
	"secondary_weapon":{
		"dagger": {"stats": { "damage" : ["1d3","1d6"], "accuracy" : ["-1d6","2d6"]} , "args":{"name":"dagger", "description":"Stabby stab!", "abilities_granted":["quickstab", "quickcut"]}},
		"shield": {"stats": {"defence" : ["1d3","5d6"], "evasion" : ["-2d6","-1d3"]} , "args":{"name":"shield", "description":"A shield.", "abilities_granted":["shieldup"]}},

		# enemy equipment below
		"animal_claws": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["2d6","6d6"]} , "args":{"name":"animal claws", "description":"Sharp claws.", "abilities_granted":["animal claw"]}},
	},
	"armor":{
		"chainmail": {"stats": { "characteristics_change":{"dexterity":[-3, 1]}, "defence" : ["2d6","5d6"], "evasion" : ["-4d6","-1d3"]} , "args":{"name":"chainmail", "description":"Light armor.", "tags_granted":["armor"]}},
		"plate armor": {"stats": { "characteristics_change":{"dexterity":[-5, -1]}, "defence" : ["3d6","7d6"], "evasion" : ["-7d6","-2d6"]} , "args":{"name":"plate armor", "description":"Heavy armor.", "tags_granted":["heavy armor"]}},
	},
	"talisman":{
		"amulet of defence": {"stats": {"defence" : ["1d6","2d6"]} , "args":{"name":"amulet of defence", "description":"The most boring talisman, it just protects you."}},
		"amulet of healing": {"stats": {"healing_amount" : ["1d6", "2d6"], "healing_chance": ["1d3", "2d6"]} , "args":{"name":"amulet of healing", "description":"Periodically heals you for random amounts of health.", "modifiers_granted": [ 

				{
				"name":"regeneration", 
				"params":{}
				} 
			]}},
	},
	"ring":{
		"ring of fire": {
			"stats": {"fire_damage" : ["1d3","2d6"], "fire_chance" : ["1d4", "6d6"]} , 
			"args":{
					"name":"ring of fire", "description":"Has a chance to cause fire damage on attack.",
					"modifiers_granted": [
						{
						"name":"fire_attack", 
						"params":{}
						} 
					]
			}
		},

		"ring of more vitality": {"stats": {"characteristics_change": {"vitality" : [1, 3]}} , "args":{"name":"ring of more vitality", "description":"Just gives you more vit."} },

		"ring of more dexterity": {"stats": {"characteristics_change": {"dexterity" : [1, 3]}} , "args":{"name":"ring of more dexterity", "description":"Just gives you more dex."} },

		"ring of thievery": {
			"stats": {
				"stats_change": {
					"evasion": ["1d6", "3d6"]
				},
				"characteristics_change": {
					"dexterity" : [1, 2]
				}
			},
			"args":{
				"name":"ring of thievery",
				"description":"Gives a dex bonus and an evasion bonus."
			}
		 },

		"ring of more strength": {"stats": {"characteristics_change": {"strength" : [1, 3]}} , "args":{"name":"ring of more strength", "description":"Just gives you more str."} },

		"ring of more intelligence": {"stats": {"characteristics_change": {"intelligence" : [1, 3]}} , "args":{"name":"ring of more intelligence", "description":"Just gives you more int."} },

		"ring of more hp": {"stats": {"stats_change": {"max_health" : [10, 50]}} , "args":{"name":"ring of more hp", "description":"Just gives you more max hp."}},
	},

	"headwear":{
		"helmet": {"stats": {"defence" : ["1d4","3d6"], "evasion" : ["-3d4","-1d2"]} }, "args":{"name":"helmet", "description":"Helmet, boring helmet."},
	}
}
