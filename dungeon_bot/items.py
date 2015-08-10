#!/usr/bin/env python3
from .util import *
from .modifiers import *
class Item(object):
	def __init__(self, name, description, item_type,  stats = {},  abilities_granted = [], modifiers_granted = [], requirements = None, tags_granted = []):
		self._name = name
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
	    return self.full_name

	@property
	def short_name(self):
		return self._name

	@property
	def name(self):
		return self._name+ "".join(["*" for modifier in self.modifiers_granted])

	@property
	def full_name(self):
	    return self._name + (" of " if len(self.modifiers_granted)>0 else "")+ " and ".join([modifier["name"] for modifier in self.modifiers_granted])

	def use(self, user, target ):
		return "Can't use %s."%(self.name)

	def examine_self(self):
		requirements = []
		for x in list(self.requirements.keys()):
			if isinstance(self.requirements[x], dict):
				for req in list(self.requirements[x].keys()):
					requirements.append("|\t"+req+":" +str(self.requirements[x][req]))
			else:
				if self.requirements[x] == False or self.requirements[x] == True:
					requirements.append("|\t"+x)
				else:
					requirements.append("|\t"+x+":" +str(self.requirements[x]))

		stats = []

		for x in list(self.stats.keys()):
			if isinstance(self.stats[x], dict):
				for stat in list(self.stats[x].keys()):
					stats.append("|\t"+str(stat)+":" +str(self.stats[x][stat]))
			else:
				stats.append("|\t"+x+":" +str(self.stats[x]))

		for modifier in self.modifiers_granted:
			for key in [stat for stat in list(modifier["stats"].keys()) if not stat in ["duration", "priority", "characteristics_change", "stats_change", "abilities_granted", "tags_granted"] ]:
				stats.append("|\t"+key+":" +str(modifier["stats"][key]))
			for characteristic in list(modifier["stats"]["characteristics_change"].keys()):
				stats.append("|\t"+characteristic+":" + ("+" if modifier["stats"]["characteristics_change"][characteristic] > 0 else "") +str(modifier["stats"]["characteristics_change"][characteristic]))
			for stat in list(modifier["stats"]["stats_change"].keys()):
				if isinstance(modifier["stats"]["stats_change"][stat], str):
					stats.append("|\t"+stat+":" +str(modifier["stats"]["stats_change"][stat]))
				else:
					stats.append("|\t"+stat+":" + ("+" if modifier["stats"]["stats_change"][stat] > 0 else "") +str(modifier["stats"]["stats_change"][stat]))

		lines = []
		lines.append("%s, %s."%(self.full_name.capitalize(), self.item_type))
		lines.append("%s"%(self.description)) if self.description != "" else None
		lines.append("Requirements:\n%s"%("\n".join(requirements))) if requirements != [] else None
		lines.append("Stats:\n%s"%("\n".join(stats))) if stats != [] else None
		lines.append("Abilities granted:\n|\t%s"%(", ".join(self.abilities_granted))) if self.abilities_granted != [] else None
		lines.append("Tags granted:\n|\t%s"%(", ".join(self.tags_granted))) if self.tags_granted != [] else None
		desc = "\n".join(lines)
		return desc

	def to_json(self):
		big_dict = self.__dict__.copy()
		big_dict["requirements"] = self.requirements
		big_dict["abilities_granted"] = self.abilities_granted
		big_dict["stats"] = self.stats
		big_dict["modifiers_granted"] = self.modifiers_granted
		big_dict["name"] = self._name
		return big_dict

	@staticmethod
	def de_json(data):
		if "_name" in data and not "name" in data:
			data["name"] = data["_name"]
		if data.get("item_type") == "primary weapon":
			return PrimaryWeapon.de_json(data)
		if data.get("item_type") == "secondary weapon":
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
		return None

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
	def __init__(self, name, description, item_type="primary weapon", stats=default_weapon_stats, abilities_granted = default_weapon_abilities, modifiers_granted = [], requirements = default_weapon_requirements, tags_granted = []):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)
	@property
	def short_desc(self):
		sh_dsc = super(PrimaryWeapon, self).short_desc
		return sh_dsc+" |acc:%s/dmg:%s|"%(self.stats["accuracy"], self.stats["damage"])


	@staticmethod
	def de_json(data):
		return PrimaryWeapon(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))


class SecondaryWeapon(Item):
	def __init__(self, name, description, item_type="secondary weapon", stats=default_weapon_stats, abilities_granted = default_weapon_abilities, modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		sh_dsc = super(SecondaryWeapon, self).short_desc
		if "accuracy" in list(self.stats.keys()):
			return sh_dsc+" |acc:%s/dmg:%s|"%(self.stats["accuracy"], self.stats["damage"])
		else:
			return sh_dsc+" |def:%s/ev:%s|"%(self.stats["defense"], self.stats["evasion"])

	@staticmethod
	def de_json(data):
		return SecondaryWeapon(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))


class Armor(Item):
	def __init__(self, name, description, item_type="armor", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		sh_dsc = super(Armor, self).short_desc
		if "defense" in self.stats.keys() and "evasion"  in self.stats.keys():
			return sh_dsc+" |def:%s/ev:%s|"%(self.stats["defense"], self.stats["evasion"])
		return sh_dsc

	@staticmethod
	def de_json(data):
		return Armor(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))

class Talisman(Item):
	def __init__(self, name, description, item_type="talisman", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		sh_dsc = super(Talisman, self).short_desc
		return sh_dsc

	@staticmethod
	def de_json(data):
		return Talisman(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))

class Ring(Item):
	def __init__(self, name, description, item_type="ring", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		sh_dsc = super(Ring, self).short_desc
		return sh_dsc

	@staticmethod
	def de_json(data):
		return Ring(data.get('name'), data.get('description'), data.get("item_type"), data.get('stats'), data.get("abilities_granted"), data.get("modifiers_granted"), data.get("requirements"), data.get("tags_granted"))


class Headwear(Item):
	def __init__(self, name, description, item_type="ring", stats={}, abilities_granted = [], modifiers_granted = [], requirements = default_weapon_requirements, tags_granted=[]):
		Item.__init__(self, name, description, item_type, stats, abilities_granted, modifiers_granted, requirements, tags_granted)

	@property
	def short_desc(self):
		sh_dsc = super(Headwear, self).short_desc
		if "defense" in self.stats.keys() and "evasion"  in self.stats.keys():
			return sh_dsc+" |def:%s/ev:%s|"%(self.stats["defense"], self.stats["evasion"])
		return sh_dsc

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
		#print("Something someething",item_args["modifiers_granted"])
		if "random_effects" in item_args.keys():
			random_modifiers = get_random_modifiers_for_coolity(coolity)
			item_args["modifiers_granted"] = item_args["modifiers_granted"] + random_modifiers

		if not "requirements" in item_args.keys():
			item_args["requirements"] = {}
		if not "abilities_granted" in item_args.keys():
			item_args["abilities_granted"] = []
		if not "tags_granted" in item_args.keys():
			item_args["tags_granted"] = []

		#print("And in the end", item_args["modifiers_granted"])
		return prototype(item_args["name"], item_args["description"], item_args["item_type"], real_stats, item_args["abilities_granted"], item_args["modifiers_granted"], item_args["requirements"], item_args["tags_granted"])

def get_item_by_name(name, coolity=0):
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
		for item in list(item_listing[key].keys()):
			if item == name:
				item_args = item_listing[key][item]["args"].copy()
				if not "stats" in item_listing[key][item].keys():
					item_listing[key][item]["stats"] = {}
				item_stats = item_listing[key][item]["stats"].copy()
				item_type = key
				break
	prototype = None
	if item_type == "primary weapon":
		prototype = PrimaryWeapon
	elif item_type == "secondary weapon":
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
	"primary weapon":{
		"rapier": {"stats": {"damage" : ["1d6","2d6"], "accuracy" : ["2d6","5d6"]} , "args":{"name":"rapier", "description":"A rapier is fast and deadly to unarmed oponents. It requires some skill to use efficiently.","random_effects": True, "abilities_granted":["stab", "quick stab"], "requirements": {"characteristics":{"dexterity": 7}}}},

		"club": {"stats": {"damage" : ["1d3","2d6"], "accuracy" : ["1d6","2d6"]} , "args":{"name":"club","random_effects": True, "description":"A rough wooden club, good enough to break a skull! An unarmed, untrained, weak skull.", "abilities_granted":["smash"]}},

		"mace": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["1d6","5d6"]} , "args":{"name":"mace","random_effects": True, "description":"Like the club, except less bad!", "abilities_granted":["smash"], "requirements":{"characteristics":{"strength":6}}}},

		"sword": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["1d6","5d6"]} , "args":{"name":"sword","random_effects": True, "description":"Steel sword!", "abilities_granted":["cut", "stab"],"requirements":{"characteristics":{"strength":5, "dexterity": 5}}}},

		"quaterstaff": {"stats": {"characteristics_change":{"intelligence":[0, 3]}, "damage" : ["1d3","2d3"], "accuracy" : ["1d6","7d6"]} , "args":{"name":"quaterstaff","random_effects": True, "description":"Quite easy to use, hard to master. It doesn't deal much damage, but in the hands of a strong fighter it's a deadly weapon.", "abilities_granted":["smack"], "requirements": { "two handed": True }}},

		"steel spear": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["1d6","6d6"]} , "args":{"name":"steel spear","random_effects": True, "description":"A spear is the simpliest weapon. It doesn't make it any less effective. It's main selling point is that it requires little to no skills to use one. Anyone can hit stuff with a spear.", "abilities_granted":["stab"], "requirements": {"two handed": True, "characteristics":{"strength":4} }}},

		"steel halberd": {"stats": {"damage" : ["1d6","4d6"], "accuracy" : ["1d6","6d6"]} , "args":{"name":"steel halberd","random_effects": True, "description":"A halberd is a deadly weapon, but it requires a lot of finese to use.", "abilities_granted":["sweep", "crush"], "requirements": {"two handed": True, "characteristics":{"strength":7, "dexterity": 6} }}},

		"claymore": {"stats": {"damage" : ["2d6","3d6"], "accuracy" : ["1d6","4d6"]} , "args":{"name":"claymore","random_effects": True, "description":"A two handed sword that allows for sweeping attacks damaging many enemies at once.", "abilities_granted":["sweep", "stab"], "requirements": {"two handed": True, "characteristics":{"strength":8} }}},

		"stone maul": {"stats": {"damage" : ["2d6","4d6"], "accuracy" : ["1d6","2d6"]} , "args":{"name":"stone maul","random_effects": True, "description":"A huge two handed stone hammer allows to strike many enemies at once.", "abilities_granted":["swing", "crush"], "requirements": {"two handed": True, "characteristics":{"strength":8} }}},

		# enemy equipment below
		"rodent_teeth": {"stats": {"damage" : ["1d3","2d3"], "accuracy" : ["4d6", "6d6"]} , "args":{"name":"rodent teeth", "description":"Slightly sharp teeth.", "abilities_granted":["rodent bite"]}},
		"animal_teeth": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["3d6","5d6"]} , "args":{"name":"animal teeth", "description":"Sharp teeth.", "abilities_granted":["animal bite"]}},

	},
	"secondary weapon":{
		"dagger": {"stats": { "damage" : ["1d3","3d5"], "accuracy" : ["-1d6","2d6"]} , "args":{"name":"dagger", "description":"Stabby stab!", "random_effects": True, "abilities_granted":["quick stab", "quick cut"]}},

		"knife": {"stats": { "damage" : ["1d3","1d10"], "accuracy" : ["-1d6","2d6"]} , "args":{"name":"knife", "description":"Dare bring a knife to a magic fight.","random_effects": True,  "abilities_granted":["quick stab"]}},

		"buckler": {"stats": {"defense" : ["1d1","1d5"], "evasion" : ["0d6","1d3"]} ,"args":{"random_effects": True, "name":"buckler", "description":"Tiny shield strapped to your arm. Offers little protection, but allows for a bashing attack.", "abilities_granted":["bash"]}},

		"targe shield": {"stats": {"defense" : ["1d6","2d6"], "evasion" : ["-4d6","-1d6"]} , "args":{"name":"targe shield","random_effects": True,"requirements": {"characteristics":{"strength": 5}}, "description":"Big round shield, protects you from hip to neck.", "abilities_granted":["shield up"]}},

		"tower shield": {"stats": {"characteristics_change":{"dexterity":[-3, -1]}, "defense" : ["2d6","4d6"], "evasion" : ["-8d6","-3d6"]} ,"args":{"random_effects": True, "name":"tower shield", "description":"Huge shield covers nearly all of your body at the expense of being extremely heavy.","requirements": {"characteristics":{"strength": 6}}, "abilities_granted":["shield up"]}},


		# enemy equipment below
		"animal_claws": {"stats": {"damage" : ["1d6","3d6"], "accuracy" : ["2d6","6d6"]} , "args":{"name":"animal claws", "description":"Sharp claws.", "abilities_granted":["animal claw"]}},
	},
	"armor":{

		"hermit cloak": {"stats": { "characteristics_change":{"intelligence":[0, 4]}, "defense" : ["0d6","1d3"]} , "args":{"random_effects": True, "name":"hermit cloak", "description":"Makes you appear like a stray philosopher. Seems to speed up growth of grey hairs.", "tags_granted":[]}},

		"ritual cloak": {"stats": { "characteristics_change":{"intelligence":[0, 6]}, "defense" : ["0d6","1d3"]}, "args":{"random_effects": True, "name":"ritual cloak", "description":"It's hard to wear, but it's worth it. The voices say it's worth it.", "tags_granted":[]}},

		"leather armor": {"stats": { "characteristics_change":{"dexterity":[-2, 1]}, "defense" : ["1d6","3d6"], "evasion" : ["-2d6","-1d3"]} , "args":{"random_effects": True, "name":"leather armor", "description":"Very light armor.", "tags_granted":["armor"]}},

		"chainmail": {"stats": { "characteristics_change":{"dexterity":[-3, 0]}, "defense" : ["1d6","5d6"], "evasion" : ["-5d6","-1d6"]} , "args":{"random_effects": True, "name":"chainmail", "description":"Light armor.", "tags_granted":["armor"], "requirements": {"characteristics":{"vitality": 5} }} },
		"plate armor": {"stats": { "characteristics_change":{"dexterity":[-5, -2]}, "defense" : ["2d6","7d6"], "evasion" : ["-10d6","-2d6"]} , "args":{"name":"plate armor", "description":"Heavy armor.","random_effects": True, "tags_granted":["heavy armor"], "requirements": {"characteristics":{"vitality": 7} }}},
	},
	"talisman":{
		"bone amulet": {"stats":{}, "args":{"name":"bone amulet", "description":"A amulet cut from a bone. A human bone.", "random_effects": True}},

		"pyramid talisman": {"stats":{}, "args":{"name":"pyramid talisman", "description":"A strange thing.", "random_effects": True}},

		"petrified eye": {"stats":{}, "args":{"name":"petrified eye", "description":"A very strange thing.", "random_effects": True}},

		"ancient coin": {"stats":{}, "args":{"name":"ancient coin", "description":"Not worth much as money this stone coin looks scary and kinda hipstery.", "random_effects": True}},

		"crowned skull": {"stats":{}, "args":{"name":"ptrified eye", "description":"A skull in a crown. Somehow you can't remove the crown from the skull no matter how you try.", "random_effects": True}},
	},
	"ring":{

		"bone ring": {"stats":{}, "args":{"name":"bone ring", "description":"A ring cut from a bone. A human bone.", "random_effects": True}},

		"steel ring": {"stats":{}, "args":{"name":"steel ring", "description":"A solid steel ring. Metal as hell.", "random_effects": True}},

		"wooden ring": {"stats":{}, "args":{"name":"wooden ring", "description":"A ring cut from a birch.", "random_effects": True}},

		"golden ring": {"stats":{}, "args":{"name":"golden ring", "description":"For the times when you need to look fabulous in the dungeons.", "random_effects": True}},
		# "ring of more vitality": {"stats": {"characteristics_change": {"vitality" : [1, 3]}} , "args":{"name":"ring of more vitality", "description":"Just gives you more vit."} },

		# "ring of more dexterity": {"stats": {"characteristics_change": {"dexterity" : [1, 3]}} , "args":{"name":"ring of more dexterity", "description":"Just gives you more dex."} },

		# "ring of thievery": {
		# 	"stats": {
		# 		"stats_change": {
		# 			"evasion": ["1d6", "3d6"]
		# 		},
		# 		"characteristics_change": {
		# 			"dexterity" : [1, 2]
		# 		}
		# 	},
		# 	"args":{
		# 		"name":"ring of thievery",
		# 		"description":"Gives a dex bonus and an evasion bonus."
		# 	}
		#  },

		# "ring of more strength": {"stats": {"characteristics_change": {"strength" : [1, 3]}} , "args":{"name":"ring of more strength", "description":"Just gives you more str."} },

		# "ring of more intelligence": {"stats": {"characteristics_change": {"intelligence" : [1, 3]}} , "args":{"name":"ring of more intelligence", "description":"Just gives you more int."} },

		# "ring of more hp": {"stats": {"stats_change": {"max_health" : [10, 50]}} , "args":{"name":"ring of more hp", "description":"Just gives you more max hp."}},
	},

	"headwear":{
		"iron helmet": {"stats": {"defense" : ["1d4","2d6"], "evasion" : ["-3d4","-1d2"]} , "args":{"name":"iron helmet", "description":"Helmet, boring helmet. Makes you look like certain someone from Skyrim though.", "random_effects": True}
		},

		"bronze crown": {"stats":{} , "args":{"name":"bronze crown", "description":"Fancy crown.", "random_effects": True}
		},

		"golden crown": {
			 "args":{"name":"golden crown", "description":"Fancier crown.", "tags_granted":["fabulous"],"random_effects": True
			 }
		},
		
	}
}
