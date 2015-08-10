#!/usr/bin/env python3
from .creatures import Enemy, Player
from .abilities import *
from .items import *
from .util import *
import random
def retrieve_enemies_for_difficulty(enemy_table, difficulty):
	total_len = 100
	right = clamp( difficulty + 0.3 * difficulty, 0, 100)
	left = clamp ( difficulty - 0.3 * total_len, 0, 100)
	candidates = []
	temp_list = sorted([int(x) for x in list(enemy_tables[enemy_table].keys()) if right >= int(x) > left] )

	if len(temp_list) == 0:
		left = 0
		temp_list = sorted([int(x) for x in list(enemy_tables[enemy_table].keys()) if right >= int(x) > left] )


	random_float = random_in_range_for_coolity(0, len(temp_list), 0.8)

	random_enemy = temp_list[int(math.floor(random_float))]


	enemies = enemy_tables[enemy_table][str(random_enemy)]

	return enemies[0](*enemies[1])

default_equipment = {
	"armor": None,
	"primary weapon": None,
	"secondary weapon": None,
	"ring": None,
	"talisman": None,
	"headwear": None
}

""" test enemies """


dummy_characteristics = {
			"strength": 5, #how hard you hit
			"vitality": 5, #how much hp you have
			"dexterity": 5, #how fast you act, your position in turn queue
			"intelligence": 5, #how likely you are to strike a critical
		}

class Dummy(Enemy):
	drop_table = {

	}
	loot_coolity = 0

	def __init__(self, level=1000000, name="dummy", characteristics = dummy_characteristics, stats=None, description="Testing dummy, it has so much hp you can hit in endlessly. Also skips every turn.", inventory=[], equipment=default_equipment, tags=[],abilities=[],modifiers=[], exp_value=0):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)

	def act(self, combat_event):
		attack_infos = []
		return attack_infos



""" common enemeies """



rat_characteristics = {
		"strength": 2, #how hard you hit
		"vitality": 2, #how much hp you have
		"dexterity": 5, #how fast you act, your position in turn queue
		"intelligence": 3, #how likely you are to strike a critical
	}

class Rat(Enemy):
	drop_table = {
		"club" : 5,
		"dagger" : 5,
		"ring" : 5,
		"iron helmet": 3,
		"random": 2,
	}
	loot_coolity = 0.5

	def __init__(self, level=1, name="rat",  characteristics = rat_characteristics, stats=None, description="An angry grey rat.", inventory=[], equipment=default_equipment, tags=["animate", "living","rodent", "animal", "small"],abilities=[],modifiers=[], exp_value=50):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("rodent_teeth", 0)
		if self.add_to_inventory(teeth):
			self.equip(teeth)

	def act(self, combat_event):
		attack_infos = []
		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			while self.energy >= self.abilities[0].energy_required:
				attack_infos.append(self.abilities[0].__class__.use(self, self.target, self.primary_weapon, combat_event))
				if not self.target or self.target.dead:
					break

		return attack_infos


big_rat_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 2, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class BigRat(Enemy):
	drop_table = {
		"club" : 5,
		"dagger" : 5,
		"ring" : 5,
		"talisman": 5,
		"headwear": 5,
		"random": 5,
	}

	loot_coolity = 0.5

	def __init__(self, level=1, name="big rat", characteristics = big_rat_characteristics, stats=None, description="A big angry grey rat.", inventory=[], equipment=default_equipment, tags=["living", "animate", "rodent", "animal", "small"],abilities=[],modifiers=[], exp_value=80):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("rodent_teeth", 0)
		if self.add_to_inventory(teeth):
			self.equip(teeth)

	def act(self, combat_event):
		attack_infos = []
		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			while self.energy >= self.abilities[0].energy_required:
				attack_infos.append(self.abilities[0].__class__.use(self, self.target, self.primary_weapon, combat_event))
				if not self.target or self.target.dead:
					break

		return attack_infos


""" animal enemies """
default_equipment = {
	"armor": None,
	"primary weapon": None,
	"secondary weapon": None,
	"ring": None,
	"talisman": None,
	"headwear": None
}

wolf_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 3, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class Wolf(Enemy):
	drop_table = {
		"armor" : 3,
		"primary weapon" : 3,
		"secondary weapon" : 3,
		"ring" : 3,
		"talisman": 4,
		"headwear": 5,
		"random": 3,
	}

	loot_coolity = 0.5

	def __init__(self, level=1, name="wolf", characteristics = wolf_characteristics, stats=None, description="An angry grey wolf.", inventory=[], equipment=default_equipment, tags=["living", "animate", "animal"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("animal_teeth", 0)
		claws = get_item_by_name("animal_claws", 0)
		if self.add_to_inventory(teeth):
			self.equip(teeth)
		if self.add_to_inventory(claws):
			self.equip(claws)


	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			while self.energy >= self.abilities[0].energy_required:
				if random.randint(0, 1) == 1:
					attack_infos.append(self.abilities[0].__class__.use(self, self.target, self.primary_weapon, combat_event))
				else:
					attack_infos.append(self.abilities[1].__class__.use(self, self.target, self.secondary_weapon, combat_event))
				if not self.target or self.target.dead:
					break

		return attack_infos

wolf_leader_characteristics = {
	"strength": 6, #how hard you hit
	"vitality": 4, #how much hp you have
	"dexterity": 6, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class WolfLeader(Enemy):
	drop_table = {
		"armor" : 5,
		"primary weapon" : 5,
		"secondary weapon" : 5,
		"ring" : 5,
		"talisman": 5,
		"headwear": 5,
		"random": 15,
		"bone ring" : 3,
	}
	loot_coolity = 0.8

	def __init__(self, level=1, name="wolf pack leader", characteristics = wolf_leader_characteristics, stats=None, description="An angry grey wolf.", inventory=[], equipment=default_equipment, tags=["living", "animate", "animal", "quick"],abilities=[],modifiers=[], exp_value=300):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("animal_teeth", 0)
		claws = get_item_by_name("animal_claws", 0)
		if self.add_to_inventory(teeth):
			self.equip(teeth)
		if self.add_to_inventory(claws):
			self.equip(claws)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
					break

		return attack_infos

bear_characteristics = {
	"strength": 7, #how hard you hit
	"vitality": 7, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class Bear(Enemy):
	drop_table = {
		"chainmail" : 3,
		"plate armor" : 3,
		"primary weapon" : 3,
		"sword": 4,
		"club": 5,
		"secondary weapon" : 3,
		"ring" : 3,
		"talisman": 4,
		"headwear": 5,
		"random": 15,
		"bone ring" : 3,
	}

	loot_coolity = 1

	def __init__(self, level=1, name="bear", characteristics = bear_characteristics, stats=None, description="An angry big bear. Very dangerous!", inventory=[], equipment=default_equipment, tags=["living", "animate", "animal", "big"],abilities=[],modifiers=[], exp_value=300):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("animal_teeth", 0)
		claws = get_item_by_name("animal_claws", 0)
		if self.add_to_inventory(teeth):
			self.equip(teeth)
		if self.add_to_inventory(claws):
			self.equip(claws)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
					break

		return attack_infos

""" undead enemies below """

undead_soldier_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 3, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 4, #how likely you are to strike a critical
}

class UndeadSoldier(Enemy):
	drop_table = {
		"chainmail" : 3,
		"claymore": 2,
		"plate armor" : 1,
		"primary weapon" : 3,
		"mace": 6,
		"sword": 4,
		"club": 5,
		"dagger": 5,
		"secondary weapon" : 3,
		"bone amulet" : 3,
		"ring" : 3,
		"talisman": 4,
		"headwear": 5,
		"random": 3,
		"rapier": 3,
		"bone ring" : 3,
	}

	loot_coolity = 0.3
	def __init__(self, level=1, name="undead soldier",  characteristics = undead_soldier_characteristics, stats=None, description="An undead soldier.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead", "slow"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "sword", "dagger", "mace", "claymore", "rapier"]), 0 )]
		items.append( get_item_by_name("targe shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( random.choice(["chainmail", "plate armor", "iron helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
					break
		return attack_infos


undead_siren_characteristics = {
	"strength": 2, #how hard you hit
	"vitality": 2, #how much hp you have
	"dexterity": 3, #how fast you act, your position in turn queue
	"intelligence": 7, #how likely you are to strike a critical
}

class UndeadSiren(Enemy):
	drop_table = {
		"random": 10,
		"bone ring" : 3,
		"bronze cworn": 5,
		"petrified eye": 5,
		"crowned skull": 5,
	}

	loot_coolity = 0.3
	def __init__(self, level=1, name="undead siren",  characteristics = undead_siren_characteristics, stats=None, description="A horribly misfigured woman. It seems to be abducted by something evil.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead", "slow"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		self.base_abilities.append(FearScream("fear scream", None))
		#items = [get_item_by_name( random.choice(["club", "sword", "dagger", "mace", "claymore", "rapier"]), 0 )]
		#items.append( get_item_by_name("targe shield", 0 ) ) if random.randint(0,10) > 7 else None
		#items.append( get_item_by_name( random.choice(["chainmail", "plate armor", "iron helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		#for item in items:
		#	if self.add_to_inventory(item):
		#		self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
					break
		return attack_infos


undead_legionaire_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 6, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class UndeadLegionaire(Enemy):
	drop_table = {
		"chainmail" : 3,
		"plate armor" : 1,
		"primary weapon" : 3,
		"steel spear": 6,
		"halberd": 6,
		"targe shield": 4,
		"secondary weapon" : 3,
		"bone amulet" : 3,
		"ring" : 3,
		"talisman": 4,
		"headwear": 5,
		"random": 3,
		"rapier": 3,
		"bone ring" : 3,
		"petrified eye" : 3,
	}

	loot_coolity = 0.5
	def __init__(self, level=1, name="undead legionaire",  characteristics = undead_legionaire_characteristics, stats=None, description="An undead legionaire.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead", "slow"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["steel spear", "steel halberd"]), 0 )]
		items.append( get_item_by_name(random.choice(["targe shield", "tower shield"]), 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( random.choice(["chainmail", "plate armor", "iron helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []
		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
					break
		return attack_infos

undead_warleader_characteristics = {
	"strength": 7, #how hard you hit
	"vitality": 7, #how much hp you have
	"dexterity": 6, #how fast you act, your position in turn queue
	"intelligence": 6, #how likely you are to strike a critical
}

class UndeadWarLeader(Enemy):
	drop_table = {
		"chainmail" : 3,
		"plate armor" : 3,
		"primary weapon" : 10,
		"steel spear": 6,
		"halberd": 6,
		"targe shield": 4,
		"secondary weapon" : 10,
		"bone amulet" : 10,
		"ring" : 3,
		"talisman": 10,
		"headwear": 5,
		"random": 10,
		"rapier": 3,
		"bone ring" : 10,
		"petrified eye" : 15,
		"crowned skull" : 15,
	}

	loot_coolity = 0.5
	def __init__(self, level=1, name="undead war leader",  characteristics = undead_warleader_characteristics, stats=None, description="A two and half meters high undead soldier. He carries a torn banner that has long lost it's colors. He seems sentinent and sane. His will to to dismember you is logically calculated.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead", "big"],abilities=[], modifiers=[], exp_value=500):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["sword", "claymore", "rapier", "mace", "steel spear", "stone maul", "steel halberd"]), 0 )]
		items.append( get_item_by_name(random.choice(["targe shield", "dagger"]), 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( random.choice(["ritual cloak", "golden crown"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

		self.base_abilities.append(FearScream("fear scream", None))

	def act(self, combat_event):
		attack_infos = []
		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
					break
		return attack_infos

undead_knight_characteristics = {
	"strength": 4, #how hard you hit
	"vitality": 4, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 4, #how likely you are to strike a critical
}

class UndeadKnight(Enemy):
	drop_table = {
		"chainmail" : 7,
		"plate armor" : 4,
		"primary weapon" : 3,
		"sword": 7,
		"mace": 7,
		"club": 5,
		"dagger": 5,
		"secondary weapon" : 3,
		"bone amulet" : 3,
		"ring" : 3,
		"talisman": 4,
		"iron helmet": 3,
		"bone ring" : 3,
		"headwear": 5,
		"random": 3,
		"claymore": 4,
	}

	loot_coolity = 0.3
	def __init__(self, level=1, name="undead knight", characteristics = undead_knight_characteristics, stats=None, description="An undead knight.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead", "slow"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["sword", "mace", "claymore"]), 0 )]
		items.append( get_item_by_name( "targe shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( "chainmail" , 0 ) ) if random.randint(0,10) > 2 else items.append( get_item_by_name( "plate armor" , 0 ) )
		items.append( get_item_by_name( random.choice(["iron helmet", "bronze crown"]), 0) ) if random.randint(0,10) > 2 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos


lich_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 7, #how likely you are to strike a critical
}

class Lich(Enemy):
	drop_table = {
		"primary weapon" : 5,
		"dagger": 5,
		"bone amulet" : 5,
		"bone ring" : 5,
		"ring" : 5,
		"talisman": 5,
		"headwear": 5,
		"random": 3,
	}

	loot_coolity = 0.8
	def __init__(self, level=1, name="lich", characteristics = lich_characteristics, stats=None, description="A lich.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( "primary weapon", 0 )]
		items.append( get_item_by_name( "targe shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( "armor" , 0 ) ) if random.randint(0,10) > 2 else None
		items.append( get_item_by_name( "headwear", 0) ) if random.randint(0,10) > 2 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos

crystaline_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 10, #how much hp you have
	"dexterity": 1, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class LichCrystaline(Enemy):
	drop_table = {
		"random": 10,
	}

	loot_coolity = 0.8
	def __init__(self, level=1, name="crystaline", characteristics = crystaline_characteristics, stats=None, description="A huge crystal, it glows with various colors.", inventory=[], equipment=default_equipment, tags=[],abilities=[],modifiers=[], exp_value=400):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		self.base_abilities.append(Revive("revive", None))

	def act(self, combat_event):
		attack_infos = []
		if self.lich:
			if self.lich.dead:
				attack_infos.append(self.abilities[0].__class__.use(self, self.lich, None, combat_event))
		return attack_infos

""" demon enemies bewow """

lesser_demon_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 2, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 4, #how likely you are to strike a critical
}

class LesserDemon(Enemy):
	drop_table = {
		"ring" : 3,
		"talisman": 4,
		"iron helmet": 3,
		"headwear": 5,
		"random": 3,
		"claymore": 2,
	}

	loot_coolity = 0.2
	def __init__(self, level=1, name="lesser demon", characteristics = lesser_demon_characteristics, stats=None, description="A lesser demon.", inventory=[], equipment=default_equipment, tags=["living","animate", "demon" ],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = []
		items.append( get_item_by_name("animal_teeth", 0 ) )
		items.append( get_item_by_name("animal_claws", 0 ) )
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos

beta_demon_characteristics = {
	"strength": 6, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 4, #how fast you act, your position in turn queue
	"intelligence": 4, #how likely you are to strike a critical
}
class BetaDemon(Enemy):
	drop_table = {
		"club" : 10,
		"mace" : 5,
		"ring" : 3,
		"talisman": 4,
		"iron helmet": 3,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.2
	def __init__(self, level=1, name="beta demon", characteristics = beta_demon_characteristics, stats=None, description="An beta demon. It's huge and wields a club from a huge bone.", inventory=[], equipment=default_equipment, tags=["animate", "living","demon", "slow", "big"],abilities=[],modifiers=[], exp_value=300):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = []
		items.append( get_item_by_name("club", 0 ) )
		items.append( get_item_by_name("animal_claws", 0 ) )
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break
		return attack_infos

""" human enemies below """


thug_characteristics = {
	"strength": 7, #how hard you hit
	"vitality": 6, #how much hp you have
	"dexterity": 4, #how fast you act, your position in turn queue
	"intelligence": 4, #how likely you are to strike a critical
}

class Thug(Enemy):
	drop_table = {
		"club" : 7,
		"mace": 4,
		"primary weapon": 3,
		"armor": 4,
		"ring" : 3,
		"talisman": 4,
		"iron helmet": 3,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.5
	def __init__(self, level=1, name="thug", characteristics = thug_characteristics, stats=None, description="A thug, strong and massive, but quite slow.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "slow", "big", "human", "living"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "sword", "mace", "claymore"]), 0 )]
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos

peasant_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 3, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class Peasant(Enemy):
	drop_table = {
		"club" : 7,
		"dagger" : 7,
		"mace": 4,
		"primary weapon": 3,
		"armor": 2,
		"ring" : 3,
		"talisman": 4,
		"iron helmet": 3,
		"headwear": 5,
		"random": 3,
		"rapier": 3,
	}
	loot_coolity = 0.3
	def __init__(self, level=1, name="peasant", characteristics = peasant_characteristics, stats=None, description="A peasant turned bandit.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "dagger", "mace", "quaterstaff"]), 0 )]
		items.append( get_item_by_name("targe shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( random.choice(["chainmail", "plate armor", "iron helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos

mercenary_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class Mercenary(Enemy):
	drop_table = {
		"primary weapon": 5,
		"secondary weapon": 5,
		"armor": 5,
		"ring" : 5,
		"headwear": 5,
		"random": 10,
	}
	loot_coolity = 0.5
	def __init__(self, level=1, name="mercenary", characteristics = mercenary_characteristics, stats=None, description="Sword for hire. Somewhat professional, quite experienced. Usually hired as canon foder and not really relied on.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( "primary weapon", 0 )]
		items.append( get_item_by_name("secondary weapon", 0 ) ) if random.randint(0,10) > 3 else None
		items.append( get_item_by_name( random.choice(["leather armor", "chainmail", "plate armor"]) , 0 ) ) if random.randint(0,10) > 3 else None
		items.append( get_item_by_name( random.choice(["headwear"]) , 0 ) ) if random.randint(0,10) > 3 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break
		return attack_infos

mercenary_spearman_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 7, #how fast you act, your position in turn queue
	"intelligence": 5, #how likely you are to strike a critical
}

class MercenarySpearman(Enemy):
	drop_table = {
		"steel spear": 10,
		"primary weapon": 5,
		"secondary weapon": 5,
		"armor": 5,
		"ring" : 5,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.5
	def __init__(self, level=1, name="mercenary spearman", characteristics = mercenary_spearman_characteristics, stats=None, description="The backbone of mercenary armies, a spearman. He is well trianed and experienced.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( "steel spear", 0 )]
		items.append( get_item_by_name( random.choice(["leather armor", "chainmail", "plate armor"]) , 0 ) ) if random.randint(0,10) > 3 else None
		items.append( get_item_by_name( random.choice(["iron helmet"]) , 0 ) ) if random.randint(0,10) > 3 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break
		return attack_infos

mercenary_leader_characteristics = {
	"strength": 6, #how hard you hit
	"vitality": 6, #how much hp you have
	"dexterity": 6, #how fast you act, your position in turn queue
	"intelligence": 7, #how likely you are to strike a critical
}

class MercenaryLeader(Enemy):
	drop_table = {
		"primary weapon": 10,
		"secondary weapon": 10,
		"armor": 5,
		"ring" : 5,
		"headwear": 5,
		"random": 15,
	}
	loot_coolity = 0.9
	def __init__(self, level=1, name="mercenary leader", characteristics = mercenary_leader_characteristics, stats=None, description="A leader of mercenaries. Hardened veteran of unfair fights.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid"],abilities=[],modifiers=[], exp_value=400):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( "primary weapon", 0 )]
		items.append( get_item_by_name( "secondary weapon", 0 ) ) if random.randint(0,10) > 3 else None
		items.append( get_item_by_name( random.choice(["leather armor", "chainmail", "plate armor"]) , 0 ) ) if random.randint(0,10) > 2 else None
		items.append( get_item_by_name( random.choice(["headwear"]) , 0 ) ) if random.randint(0,10) > 3 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break
		return attack_infos


thief_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 3, #how much hp you have
	"dexterity": 8, #how fast you act, your position in turn queue
	"intelligence": 8, #how likely you are to strike a critical
}

class Thief(Enemy):
	drop_table = {
		"random": 20,
		"dagger": 10,
	}
	loot_coolity = 0.7
	def __init__(self, level=1, name="thief", characteristics = thief_characteristics, stats=None, description="A professional thief.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid", "quick"],abilities=[],modifiers=[], exp_value=400):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( "dagger", 1 )]
		items.append( get_item_by_name( "rapier" , 0 ) ) if random.randint(0,10) > 5 else None
		items.append( get_item_by_name( random.choice(["steel ring", "golden ring", "ring"]) , 0 ) ) if random.randint(0,10) > 8 else None
		items.append( get_item_by_name( random.choice(["bone amulet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos

mercenary_mage_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 3, #how much hp you have
	"dexterity": 4, #how fast you act, your position in turn queue
	"intelligence": 8, #how likely you are to strike a critical
}

class MercenaryMage(Enemy):
	drop_table = {
		"dagger" : 7,
		"armor":5,
		"ring" : 10,
		"talisman": 10,
		"bronze crown": 5,
		"random": 5,
	}
	loot_coolity = 0.8
	def __init__(self, level=1, name="mage", characteristics = mercenary_mage_characteristics, stats=None, description="Fireball for hire,.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["quaterstaff", "dagger"]), 0 )]
		items.append( get_item_by_name( random.choice(["hermit cloak", "leather armor", "ritual cloak"]) , 0 ) ) if random.randint(0,10) > 6 else None
		items.append( get_item_by_name( random.choice(["ring", "talisman", "headwear"]) , 0 ) ) if random.randint(0,10) > 6 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

		spells = ["heal", "fireball", "lightning", "mass pain"]
		for spell in spells:
			self.base_abilities.append(abilities_listing[spell](spell, None))
		


	def act(self, combat_event):
		attack_infos = []

		for c in combat_event.enemies:
			if not c.dead and c.health < c.stats["max_health"] and not "regeneration" in [modifier.name for modifier in c.modifiers]:
				ability = [x for x in self.abilities if x.name == "heal"][0]
				if self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, c, ability.granted_by, combat_event))

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			if len([enemy for enemy in combat_event.enemies if not enemy.dead]) > 0 and not "pain" in [modifier.name for modifier in self.target.modifiers]:
				ability = [x for x in self.abilities if x.name == "mass pain"][0]
			else:
				ability = [x for x in self.abilities if x.name == "fireball"][0]
			while self.energy >= ability.energy_required:
				attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
				if not self.target or self.target.dead:
					break
		return attack_infos

ogre_characteristics = {
	"strength": 9, #how hard you hit
	"vitality": 8, #how much hp you have
	"dexterity": 4, #how fast you act, your position in turn queue
	"intelligence": 2, #how likely you are to strike a critical
}

class Ogre(Enemy):
	drop_table = {
		"club" : 6,
		"mace": 5,
		"primary weapon": 3,
		"armor": 4,
		"iron helmet": 3,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.7
	def __init__(self, level=1, name="ogre", characteristics = ogre_characteristics, stats=None, description="A slow hulking ogre. It looks hungry for you.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "slow", "big", "humanoid", "living"],abilities=[],modifiers=[], exp_value=400):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "mace"]), 0 )]
		items.append( get_item_by_name( random.choice(["chainmail", "plate armor", "iron helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item, True)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos

""" enemy group functions below """
enemy_list = { #name to enemy
	"rat": Rat,
	"big rat": BigRat,
	"wolf": Wolf,
	"wolf pack leader": WolfLeader,
	"bear": Bear,
	"undead soldier": UndeadSoldier,
	"undead knight": UndeadKnight,
	"undead legionaire": UndeadLegionaire,
	"undead warleader": UndeadWarLeader,
	"undead siren": UndeadSiren,

	"lich": Lich,
	"crystaline": LichCrystaline,

	"lesser demon": LesserDemon,
	"beta demon": BetaDemon,
	"peasant": Peasant,
	"mercenary": Mercenary,
	"mercenary spearman": MercenarySpearman,
	"mercenary leader": MercenaryLeader,
	"thief": Thief,

	
	#"mage": Mage,
	"ogre": Ogre,

}

""" Common enemy spawn functions """

def rat_pack(size=None):
	description = "A rat.\n"
	rat_levels = list(range(1, 5))
	amount = 1
	if size == "small":
		rat_levels = list(range(1, 10))
		amount = random.randint(1, 3)
		if amount > 1:
			description = "A small pack of rats.\n"
	elif size == "medium":
		rat_levels = list(range(5, 15))
		description = "A pack of rats.\n"
		amount = random.randint(2, 4)
	elif size == "big":
		rat_levels = list(range(15, 25))
		description = "A hoard of rats.\n"
		amount = random.randint(4, 5)
	rats = [ Rat(random.choice(rat_levels)) if random.randint(0, 10) < 7 else BigRat(random.choice(rat_levels)) for x in range(amount+1)]
	return rats, description

""" Animal enemy spawn functions """

def wolf_leader(size=None):
	if size == "strong":
		leader_levels = list(range(10, 20))
		leader = WolfLeader(random.choice(leader_levels))
		description = "A mature wolf pack leader.\n"
	elif size == "very strong":
		leader_levels = list(range(20, 35))
		leader = WolfLeader(random.choice(leader_levels))
		description = "A fearsome wolf pack leader.\n"
	else:
		leader_levels = list(range(5, 10))
		leader = WolfLeader(random.choice(leader_levels))
		description = "A young wolf pack leader.\n"
	return [leader], description

def wolf_pack(size=None, special_enemy=None):
	wolf_levels = list(range(1, 4))
	description = "A wolf.\n"
	amount = 1
	if size == "small":
		wolf_levels = list(range(1, 5))
		amount = random.randint(1, 2)
		if amount > 1:
			description = "A small pack of wolves.\n"
	elif size == "medium":
		description = "A pack of wolves.\n"
		wolf_levels = list(range(5, 15))
		amount = random.randint(2, 4)
	elif size == "big":
		description = "A big pack of mature wolves.\n"
		wolf_levels = list(range(15, 35))
		amount = random.randint(3, 5)
	elif size == "huge":
		description = "A big pack of fearsome wolves.\n"
		wolf_levels = list(range(35, 50))
		amount = random.randint(10, 20)
	desc = ""
	leader = []
	if special_enemy:
		if special_enemy == "wolf leader":
			if size == "medium" and random.randint(0, 10) > 4:
				leader, desc = wolf_leader()
			elif size == "big" and random.randint(0, 10) > 4:
				leader, desc = wolf_leader("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				leader, desc = wolf_leader("very strong")

	wolves = [ Wolf(random.choice(wolf_levels)) for x in range(amount+1)] + leader
	description += desc
	return wolves, description

def bear(size = None):
	if size == "strong":
		bear_levels = list(range(10, 20))
		bear = Bear(random.choice(bear_levels))
		description = "A mature bear.\n"
	elif size == "very strong":
		bear_levels = list(range(20, 35))
		bear = Bear(random.choice(bear_levels))
		description = "A fearsome bear.\n"
	else:
		bear_levels = list(range(5, 10))
		bear = Bear(random.choice(bear_levels))
		description = "A young bear.\n"
	return [bear], description

def ogres(size = None):
	description = "An ogre."
	levels = list(range(5,15))
	amount = 1
	if size == "small":
		amount = random.randint(1, 2)
		if amount != 1:
			description = "A couple young ogres.\n"
	elif size == "medium":
		description = "Mature ogres.\n"
		levels = list(range(10,20))
		amount = random.randint(1, 3)
	elif size == "big":
		description = "Dangerous ogres.\n"
		levels = list(range(20,35))
		amount = random.randint(2, 4)
	elif size == "huge":
		description = "Very dangerous ogres.\n"
		levels = list(range(35,50))
		amount = random.randint(2, 5)
	ogres = [ Ogre(random.choice(levels)) for x in range(amount+1)]
	return ogres, description

""" Undead enemy spawn functions """
def undead_soldier_pack(size=None, special_enemy=None):
	description = "An undead soldier.\n"
	levels = list(range(1,6))
	amount = 1
	if size == "small":
		levels = list(range(10,25))
		amount = random.randint(1, 2)
		if amount > 1:
			description = "A small group of undead soldiers.\n"
	elif size == "medium":
		levels = list(range(15,35))
		description = "A group of undead soldiers.\n"
		amount = random.randint(2, 3)
	elif size == "big":
		levels = list(range(35,55))
		description = "A big group of undead soldiers.\n"
		amount = random.randint(3, 5)
	elif size == "huge":
		levels = list(range(55,65))
		description = "A unit of undead soldiers.\n"
		amount = random.randint(4, 6)

	desc = ""
	special_enemies= []
	lich_group = []
	siren_group = []
	if special_enemy:
		if special_enemy == "lich":
			if size == "big" and random.randint(0, 10) > 6:
				lich_group, desc = lich("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				lich_group, desc = lich("very strong")
			elif random.randint(0, 10) > 8:
				lich_group, desc = lich()
		if special_enemy == "siren":
			if size == "big" and random.randint(0, 10) > 6:
				siren_group, desc = undead_siren("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				siren_group, desc = undead_siren("very strong")
			elif random.randint(0, 10) > 8:
				siren_group, desc = undead_siren()
	special_enemies += lich_group + siren_group
	description += desc
	soldiers = [ UndeadSoldier(random.choice(levels)) if random.randint(0, 10) < 7 else UndeadKnight(random.choice(levels)) for x in range(amount+1)] + special_enemies

	return soldiers, description

def undead_legionaire_pack(size=None, special_enemy=None):
	description = "An undead soldier.\n"
	amount = 1
	levels = list(range(1,6))
	if size == "small":
		levels = list(range(5,15))
		amount = random.randint(1, 2)
		if amount > 1:
			description = "A small group of undead legionaires.\n"
	elif size == "medium":
		levels = list(range(15,35))
		description = "A group of undead legionaires.\n"
		amount = random.randint(2, 3)
	elif size == "big":
		levels = list(range(25,55))
		description = "A group of veteran undead legionaires.\n"
		amount = random.randint(3, 5)
	elif size == "huge":
		levels = list(range(45,65))
		description = "A unit of elite undead legionaires.\n"
		amount = random.randint(4, 6)

	desc = ""
	special_enemies = []
	lich_group = []
	siren_group = []
	if special_enemy:
		if special_enemy == "lich":
			if size == "big" and random.randint(0, 10) > 6:
				lich_group, desc = lich("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				lich_group, desc = lich("very strong")
			elif random.randint(0, 10) > 8:
				lich_group, desc = lich()
		if special_enemy == "siren":
			if size == "big" and random.randint(0, 10) > 6:
				siren_group, desc = undead_siren("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				siren_group, desc = undead_siren("very strong")
			elif random.randint(0, 10) > 8:
				siren_group, desc = undead_siren()
	special_enemies += lich_group + siren_group
	description += desc
	soldiers = [ UndeadLegionaire(random.choice(levels)) if random.randint(0, 10) < 7 else UndeadKnight(random.choice(levels)) for x in range(amount+1)] + siren_group

	return soldiers, description

def undead_siren(size = None):
	if not size:
		description = "A siren.\n"
		levels = list(range(5,10))
		siren = UndeadSiren(random.choice(levels))
		enemies = [ siren ]

	elif size == "strong":
		description = "A strong siren.\n"
		levels = list(range(10,20))
		siren = UndeadSiren(random.choice(levels))
		enemies = [ siren ]

	elif size == "very strong":
		description = "Two very strong sirens.\n"
		levels = list(range(10,20))
		siren = UndeadSiren(random.choice(levels))
		siren1 = UndeadSiren(random.choice(levels))
		enemies = [ siren, siren1 ]
	return enemies, description

def undead_warleader(size = None):
	if not size:
		description = "An undead warleader.\n"
		levels = list(range(35,60))
		warleader = UndeadWarLeader(random.choice(levels))
		enemies = [ warleader ]

	elif size == "strong":
		description = "A honored undead warleader.\n"
		levels = list(range(60,70))
		warleader = UndeadWarLeader(random.choice(levels))
		enemies = [ warleader ]


	elif size == "very strong":
		description = "A legendary undead warleader.\n"
		levels = list(range(70,85))
		warleader = UndeadWarLeader(random.choice(levels))
		enemies = [ warleader ]

	return enemies, description

def lich(size = None):
	if not size:
		description = "A lich.\n"
		levels = list(range(5,10))
		lich = Lich(random.choice(levels))
		crystaline = LichCrystaline(random.choice(levels))
		crystaline.lich = lich
		enemies = [ lich, crystaline ]

	elif size == "strong":
		description = "A strong lich.\n"
		levels = list(range(10,20))
		lich = Lich(random.choice(levels))
		crystaline = LichCrystaline(random.choice(levels))
		crystaline.lich = lich
		enemies = [ lich, crystaline ]

	elif size == "very strong":
		description = "Two very strong liches.\n"
		levels = list(range(10,20))
		lich = Lich(random.choice(levels))
		lich1 = Lich(random.choice(levels))
		crystaline = LichCrystaline(random.choice(levels))
		crystaline1 = LichCrystaline(random.choice(levels))
		crystaline.lich = lich
		crystaline1.lich = lich1
		enemies = [lich, lich1, crystaline, crystaline1]

	return enemies, description

""" Demon enemy spawn functions """
def lesser_demon_pack(size=None, special_enemy = None):
	description = "A lesser demon.\n"
	levels = list(range(1,5))
	amount = 1
	if size == "small":
		amount = random.randint(1, 2)
		levels = list(range(5,15))
		if amount != 1:
			description = "A small group of lesser demons.\n"

	elif size == "medium":
		levels = list(range(10,25))
		description = "A group of lesser demons.\n"
		amount = random.randint(3, 4)

	elif size == "big":
		levels = list(range(20,40))
		description = "A group of hardened lesser demons.\n"
		amount = random.randint(4, 5)

	elif size == "huge":
		levels = list(range(30,60))
		description = "A group of horrible lesser demons.\n"
		amount = random.randint(4, 5)

	demons = [ LesserDemon(random.choice(levels)) for x in range(amount+1)]
	desc = ""
	beta_demons = []
	if special_enemy:
		if special_enemy == "beta demon":
			if size == "medium" and random.randint(0, 10) > 4:
				beta_demons, desc = beta_demon()
			elif size == "big" and random.randint(0, 10) > 4:
				beta_demons, desc = beta_demon("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				beta_demons, desc = beta_demon("very strong")

	demons += beta_demons
	description += desc
	return demons, description

def beta_demon(size = None):
	if size == "strong":
		demon_levels = list(range(10, 20))
		demon = BetaDemon(random.choice(demon_levels))
		description = "A strong beta demon.\n"
	elif size == "very strong":
		demon_levels = list(range(20, 35))
		demon = BetaDemon(random.choice(demon_levels))
		description = "A fearsome beta demon.\n"
	else:
		demon_levels = list(range(5, 10))
		demon = BetaDemon(random.choice(demon_levels))
		description = "A beta demon.\n"
	return [demon], description

""" Human enemy spawn functions """

def peasant_pack(size=None, special_enemy = None):
	description = "A peasant.\n"
	levels = list(range(1,5))
	amount = 1
	if size == "small":
		amount = random.randint(1, 2)
		levels = list(range(5,15))
		if amount != 1:
			description = "A small group of peasants.\n"
	elif size == "medium":
		levels = list(range(10,25))
		description = "A group of peasants.\n"
		amount = random.randint(3, 4)
	elif size == "big":
		levels = list(range(20,40))
		description = "A group of experienced peasants.\n"
		amount = random.randint(4, 5)
	elif size == "huge":
		levels = list(range(30,60))
		description = "A group of armed to the teeth peasants.\n"
		amount = random.randint(4, 5)
	peasants = [ Peasant(random.choice(levels)) for x in range(amount+1)]

	thieves = []
	thug_enemies = []
	desc = ""
	if special_enemy:
		if special_enemy == "thief":
			if size == "medium" and random.randint(0, 10) > 4:
				thieves, desc = thief()
			elif size == "big" and random.randint(0, 10) > 4:
				thieves, desc = thief("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				thieves, desc = thief("very strong")
		elif special_enemy == "thugs":
			if size == "medium" and random.randint(0, 10) > 4:
				thug_enemies, desc = thugs()
			elif size == "big" and random.randint(0, 10) > 4:
				thug_enemies, desc = thugs("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				thug_enemies, desc = thugs("very strong")
	peasants += thieves
	peasants += thug_enemies
	description += desc
	return peasants, description

def mercenary_pack(size=None, special_enemy = None):
	description = "A mercenary.\n"
	levels = list(range(1,5))
	amount = 1
	if size == "small":
		amount = random.randint(1, 2)
		levels = list(range(5,15))
		if amount != 1:
			description = "A small group of mercenaries.\n"
	elif size == "medium":
		levels = list(range(10,25))
		description = "A group of mercenaries.\n"
		amount = random.randint(3, 4)
	elif size == "big":
		levels = list(range(20,40))
		description = "A group of experienced mercenaries.\n"
		amount = random.randint(4, 5)
	elif size == "huge":
		levels = list(range(30,60))
		description = "A group of veteran mercenaries.\n"
		amount = random.randint(4, 5)
	mercs = [ Mercenary(random.choice(levels)) if random.randint(1, 10) < 6 else MercenarySpearman(random.choice(levels)) for x in range(amount+1)]

	thieves = []
	thug_enemies = []
	merc_leader = []
	mage_enemies = []
	desc = ""
	if special_enemy:
		if special_enemy == "thief":
			if size == "medium" and random.randint(0, 10) > 3:
				thieves, desc = thief()
			elif size == "big" and random.randint(0, 10) > 3:
				thieves, desc = thief("strong")
			elif size == "huge" and random.randint(0, 10) > 3:
				thieves, desc = thief("very strong")
		elif special_enemy == "thugs":
			if size == "medium" and random.randint(0, 10) > 3:
				thug_enemies, desc = thugs()
			elif size == "big" and random.randint(0, 10) > 3:
				thug_enemies, desc = thugs("strong")
			elif size == "huge" and random.randint(0, 10) > 3:
				thug_enemies, desc = thugs("very strong")
		elif special_enemy == "leader":
			if size == "medium" and random.randint(0, 10) > 3:
				merc_leader, desc = mercenary_leader()
			elif size == "big" and random.randint(0, 10) > 3:
				merc_leader, desc = mercenary_leader("strong")
			elif size == "huge" and random.randint(0, 10) > 3:
				merc_leader, desc = mercenary_leader("very strong")
		elif special_enemy == "mages":
			if size == "medium" and random.randint(0, 10) > 3:
				mages, desc = merc_mages("medium")
			elif size == "small" and random.randint(0, 10) > 3:
				mages, desc = merc_mages("small")
			elif size == "big" and random.randint(0, 10) > 3:
				mages, desc = merc_mages("big")
			elif size == "huge" and random.randint(0, 10) > 3:
				mages, desc = merc_mages("huge")

	mercs += thieves
	mercs += thug_characteristics
	mercs += merc_leader
	mercs += mage_enemies
	description += desc
	return mercs, description

def mercenary_leader(size = None):
	if size == "strong":
		levels = list(range(10, 30))
		merc_leader_enemy = MercenaryLeader(random.choice(levels))
		description = "A hardened mercenary leader.\n"
	elif size == "very strong":
		levels = list(range(30, 55))
		merc_leader_enemy = MercenaryLeader(random.choice(levels))
		description = "A legendary mercenary leader.\n"
	else:
		levels = list(range(5, 10))
		merc_leader_enemy = MercenaryLeader(random.choice(levels))
		description = "A mercenary leader.\n"
	return [merc_leader_enemy], description

def merc_mages(size=None):
	description = "A mage."
	levels = list(range(5,10))
	amount = 1
	if size == "small":
		amount = random.randint(1, 2)
		if amount != 1:
			description = "Novice mages.\n"
	elif size == "medium":
		description = "Average mages.\n"
		levels = list(range(10,20))
		amount = random.randint(2, 3)
	elif size == "big":
		description = "Experienced mages.\n"
		levels = list(range(20,40))
		amount = random.randint(2, 3)
	elif size == "huge":
		description = "Veteran mages.\n"
		levels = list(range(40,60))
		amount = random.randint(2, 3)
	mages = [ MercenaryMage(random.choice(levels)) for x in range(amount+1)]
	return mages, description


def thief(size = None):
	if size == "strong":
		thief_levels = list(range(10, 20))
		thief_enemy = Thief(random.choice(thief_levels))
		description = "A professional thief.\n"
	elif size == "very strong":
		thief_levels = list(range(20, 35))
		thief_enemy = Thief(random.choice(thief_levels))
		description = "A legendary thief.\n"
	else:
		thief_levels = list(range(5, 10))
		thief_enemy = Thief(random.choice(thief_levels))
		description = "A thief.\n"
	return [thief_enemy], description

def thugs(size = None):
	description = "A thug.\n"
	levels = list(range(1,5))
	amount = 1
	if size == "strong":
		amount = random.randint(2, 3)
		levels = list(range(10,20))
		description = "A couple of tough thugs.\n"
	elif size == "very strong":
		levels = list(range(20,40))
		description = "A group of professional thugs.\n"
		amount = random.randint(2, 3)
	else:
		description = "A thug.\n"
		levels = list(range(5,10))
		amount = 1

	thugs = [ Thug(random.choice(levels)) for x in range(amount+1)]
	return thugs, description


enemy_tables = { # difficulty rating: (function to get enemy or enemy group, params)
	"common": {
		#"1": (rat_pack, [] ),
		#"5": (rat_pack,["small"] ),
		#"15": (rat_pack, ["medium"] ),
		#"30": (rat_pack, ["big"] ),
	},
	"animal": {
		"1": (wolf_pack,[] ),
		"5": (wolf_pack,["small"] ),
		"5": (ogres,[] ),
		"10": (wolf_pack, ["medium"] ),
		"15": (wolf_pack, ["medium", "wolf leader"] ),
		"15": (ogres,["small"] ),
		"10": (bear, [] ),
		"20": (wolf_pack, ["big"] ),
		"20": (ogres, ["medium"] ),
		"25": (wolf_pack, ["big", "wolf leader"] ),
		"30": (bear, ["strong"] ),
		"30": (ogres, ["big"] ),
		"40": (wolf_pack, ["huge"] ),
		"40": (ogres, ["huge"] ),
		"50": (wolf_pack, ["huge", "wolf leader"] ),
		"50": (bear, ["very strong"] ),
	},
	"undead": {
		"1": (undead_soldier_pack,[] ),
		"1": (undead_soldier_pack,["small"] ),
		"5": (undead_soldier_pack, ["medium"] ),
		"5": (undead_legionaire_pack, []),
		"10": (undead_siren, []),
		"10": (undead_legionaire_pack, ["small", "siren"]),
		"10": (lich, []),
		"10": (undead_soldier_pack, ["big" ] ),
		"10": (undead_legionaire_pack, ["medium"]),
		"15": (undead_soldier_pack, ["big", "lich"] ),
		"15": (undead_soldier_pack, ["big", "siren"] ),
		"20": (undead_legionaire_pack, ["medium", "lich"]),
		"20": (undead_legionaire_pack, ["medium", "siren"]),
		"30": (lich, ["strong"]),
		"30": (undead_soldier_pack, ["huge"] ),
		"40": (undead_warleader, []),
		"50": (lich, ["very strong"]),
		"60": (undead_soldier_pack, ["huge", "lich"] ),
		"60": (undead_soldier_pack, ["huge", "siren"] ),
		"60": (undead_warleader, ["strong"]),
		"80": (undead_warleader, ["very strong"]),
	},
	"demon": {
		"1": (lesser_demon_pack,[] ),
		"5": (lesser_demon_pack,["small"] ),
		"10": (lesser_demon_pack, ["medium"] ),
		"15": (lesser_demon_pack, ["medium", "beta demon"] ),
		"10": (beta_demon, [] ),
		"20": (lesser_demon_pack, ["big"] ),
		"20": (beta_demon, ["strong"] ),
		"25": (lesser_demon_pack, ["big", "beta_demon"] ),

		"40": (lesser_demon_pack, ["huge"] ),
		"40": (beta_demon, ["very strong"] ),
		"50": (lesser_demon_pack, ["huge", "beta demon"] ),
	},
	"human": {
		"1": (peasant_pack,[] ),
		"5": (peasant_pack,["small"] ),
		"5": (thugs, []),
		"10": (thief, [] ),
		"5": (mercenary_pack,[] ),
		"10": (merc_mages, []),
		"10": (peasant_pack,["medium"] ),
		"10": (mercenary_pack,["small"] ),
		"10": (peasant_pack,["medium", "thief"] ),
		"15": (peasant_pack,["medium", "thugs"] ),
		"15": (mercenary_pack,["small", "thugs"] ),
		"15": (mercenary_pack,["small", "mages"] ),
		"15": (thugs, ["strong"]),
		"15": (thief, ["strong"]),
		"15": (mercenary_leader, []),
		"20": (peasant_pack,["big", "thugs"] ),
		"20": (peasant_pack,["big", "thief"] ),
		"20": (mercenary_pack,["medium", "thugs"] ),
		"20": (mercenary_pack,["medium", "thief"] ),
		"20": (mercenary_pack,["medium", "mages"] ),
		"20": (mercenary_pack,["medium", "leader"] ),
		"30": (thief, ["very strong"] ),
		"30": (thugs, ["very strong"] ),
		"30": (mercenary_leader, ["strong"]),
		"35": (mercenary_pack,["big", "thugs"] ),
		"35": (mercenary_pack,["big", "thief"] ),
		"35": (mercenary_pack,["big", "mages"] ),
		"35": (mercenary_pack,["big", "leader"] ),
		"40": (peasant_pack,["huge"] ),
		"40": (mercenary_leader, ["very strong"]),
		"50": (peasant_pack,["huge", "thugs"] ),
		"50": (peasant_pack,["huge", "thief"] ),
		"55": (mercenary_pack,["huge", "thugs"] ),
		"55": (mercenary_pack,["huge", "thief"] ),
		"55": (mercenary_pack,["huge", "mages"] ),
		"55": (mercenary_pack,["huge", "leader"] ),
	},

}
