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
			"dexterity": 5, #how fast you act, your position in turn qeue
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
		"dexterity": 5, #how fast you act, your position in turn qeue
		"intelligence": 3, #how likely you are to strike a critical
	}

class Rat(Enemy):
	drop_table = {
		"club" : 5,
		"dagger" : 5,
		"ring" : 5,
		"helmet": 3,
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
	"dexterity": 5, #how fast you act, your position in turn qeue
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
	"dexterity": 5, #how fast you act, your position in turn qeue
	"intelligence": 5, #how likely you are to strike a critical
}

class Wolf(Enemy):
	drop_table = {
		"chainmail" : 3,
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
	"strength": 5, #how hard you hit
	"vitality": 4, #how much hp you have
	"dexterity": 6, #how fast you act, your position in turn qeue
	"intelligence": 5, #how likely you are to strike a critical
}

class WolfLeader(Enemy):
	drop_table = {
		"chainmail" : 3,
		"primary weapon" : 5,
		"secondary weapon" : 3,
		"ring" : 3,
		"talisman": 4,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.8

	def __init__(self, level=1, name="wolf pack leader", characteristics = wolf_characteristics, stats=None, description="An angry grey wolf.", inventory=[], equipment=default_equipment, tags=["living", "animate", "animal", "quick"],abilities=[],modifiers=[], exp_value=300):
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
	"dexterity": 5, #how fast you act, your position in turn qeue
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
		"random": 3,
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
	"dexterity": 5, #how fast you act, your position in turn qeue
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
	}

	loot_coolity = 0.3
	def __init__(self, level=1, name="undead soldier",  characteristics = undead_soldier_characteristics, stats=None, description="An undead soldier.", inventory=[], equipment=default_equipment, tags=["living", "animate", "humanoid", "undead", "slow"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "sword", "dagger", "mace", "claymore", "rapier"]), 0 )]
		items.append( get_item_by_name("shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( random.choice(["chainmail", "plate armor", "helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item)

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
	"dexterity": 5, #how fast you act, your position in turn qeue
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
		"helmet": 3,
		"headwear": 5,
		"random": 3,
		"claymore": 4,
	}

	loot_coolity = 0.3
	def __init__(self, level=1, name="undead knight", characteristics = undead_knight_characteristics, stats=None, description="An undead knight.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead", "slow"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["sword", "mace", "claymore"]), 0 )]
		items.append( get_item_by_name( "shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( "chainmail" , 0 ) ) if random.randint(0,10) > 2 else items.append( get_item_by_name( "plate armor" , 0 ) )
		items.append( get_item_by_name( "helmet" , 0 ) ) if random.randint(0,10) > 2 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item)

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

""" demon enemies bewow """

lesser_demon_characteristics = {
	"strength": 3, #how hard you hit
	"vitality": 2, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn qeue
	"intelligence": 4, #how likely you are to strike a critical
}

class LesserDemon(Enemy):
	drop_table = {
		"ring" : 3,
		"talisman": 4,
		"helmet": 3,
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
				self.equip(item)

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
	"dexterity": 4, #how fast you act, your position in turn qeue
	"intelligence": 4, #how likely you are to strike a critical
}
class BetaDemon(Enemy):
	drop_table = {
		"club" : 10,
		"ring of more dexterity" : 3,
		"ring of more vitality" : 6,
		"ring" : 3,
		"talisman": 4,
		"helmet": 3,
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
				self.equip(item)

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

""" human enemies below """


thug_characteristics = {
	"strength": 7, #how hard you hit
	"vitality": 6, #how much hp you have
	"dexterity": 4, #how fast you act, your position in turn qeue
	"intelligence": 4, #how likely you are to strike a critical
}

class Thug(Enemy):
	drop_table = {
		"club" : 7,
		"mace": 4,
		"primary weapon": 3,
		"armor": 4,
		"ring of more strength" : 5,
		"ring of more intelligence" : 2,
		"ring" : 3,
		"talisman": 4,
		"helmet": 3,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.5
	def __init__(self, level=1, name="thug", characteristics = thug_characteristics, stats=None, description="A thug, strong and massive, but quite slow.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "slow", "big", "human", "living"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "sword", "mace", "claymore"]), 0 )]
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item)

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
	"dexterity": 4, #how fast you act, your position in turn qeue
	"intelligence": 4, #how likely you are to strike a critical
}

class Peasant(Enemy):
	drop_table = {
		"club" : 7,
		"dagger" : 7,
		"mace": 4,
		"primary weapon": 3,
		"armor": 2,
		"ring of more strength" : 5,
		"ring of more intelligence" : 2,
		"ring" : 3,
		"talisman": 4,
		"helmet": 3,
		"headwear": 5,
		"random": 3,
		"rapier": 3,
	}
	loot_coolity = 0.3
	def __init__(self, level=1, name="peasant", characteristics = peasant_characteristics, stats=None, description="A peasant turned bandit.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "dagger", "mace"]), 0 )]
		items.append( get_item_by_name("shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( random.choice(["chainmail", "plate armor", "helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item)

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
	"dexterity": 8, #how fast you act, your position in turn qeue
	"intelligence": 8, #how likely you are to strike a critical
}

class Thief(Enemy):
	drop_table = {
		"random": 20,
		"dagger": 10,
		"rapier": 5,
	}
	loot_coolity = 0.7
	def __init__(self, level=1, name="thief", characteristics = thief_characteristics, stats=None, description="A professional thief.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid", "quick"],abilities=[],modifiers=[], exp_value=400):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( "dagger", 1 )]
		items.append( get_item_by_name( "rapier" , 0 ) ) if random.randint(0,10) > 5 else None
		items.append( get_item_by_name( random.choice(["ring of thievery", "ring of more vitality"]) , 0 ) ) if random.randint(0,10) > 8 else None
		items.append( get_item_by_name( random.choice(["amulet of defence", "bone amulet"]) , 0 ) ) if random.randint(0,10) > 8 else None
		for item in items:
			if self.add_to_inventory(item):
				self.equip(item)

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
	"lesser demon": LesserDemon,
	"beta demon": BetaDemon,
	"peasant": Peasant,
	"thief": Thief,
}

def rat_pack(size):
	description = "A rat.\n"
	rat_levels = list(range(1, 3))
	amount = 1
	if size == "small":
		amount = random.randint(1, 3)
		if amount > 1:
			description = "A small pack of rats.\n"
	elif size == "medium":
		description = "A pack of rats.\n"
		amount = random.randint(3, 6)
	elif size == "big":
		description = "A hoard of rats.\n"
		amount = random.randint(6, 10)
	elif size == "huge":
		description = "RATS ARE EVERYWHERE.\n"
		amount = random.randint(10, 20)
	rats = [ Rat(random.choice(rat_levels)) if random.randint(0, 10) < 7 else BigRat(random.choice(rat_levels)) for x in range(amount+1)]
	return rats, description

def wolf_pack(size):
	wolf_leader = None
	wolf_levels = list(range(1, 4))
	wolf_leader_levels = list(range(1, 4))
	description = "A wolf.\n"
	amount = 1
	if size == "small":
		amount = random.randint(1, 3)
		if amount > 1:
			description = "A small pack of wolves.\n"
	elif size == "medium":
		description = "A pack of wolves.\n"
		amount = random.randint(3, 5)
		wolf_leader = WolfLeader(random.choice(wolf_leader_levels)) if random.randint(0, 10) > 9 else None
	elif size == "big":
		description = "A big pack of wolves!\n"
		amount = random.randint(5, 10)
		wolf_leader = WolfLeader(random.choice(wolf_leader_levels)) if random.randint(0, 10) > 6 else None
	elif size == "huge":
		description = "Wolves circle around you in a hoarde.\n"
		amount = random.randint(10, 20)
		wolf_leader = WolfLeader(random.choice(wolf_leader_levels)) if random.randint(0, 10) > 3 else None
	
	wolves = [ Wolf(random.choice(wolf_levels)) for x in range(amount+1)]
	if wolf_leader:
		wolves.append(wolf_leader)
	return wolves, description

def bear():
	description = "A bear.\n"
	levels = list(range(1, 3))
	return [Bear(random.choice(levels))], description

def undead_soldier_pack(size):
	description = "An undead soldier.\n"
	levels = list(range(1,10))
	amount = 1
	if size == "small":
		amount = random.randint(1, 3)
		if amount != 1:
			description = "A small group of undead soldiers.\n"
	elif size == "medium":
		description = "A group of undead soldiers.\n"
		amount = random.randint(3, 6)
	elif size == "big":
		description = "A squad of undead soldiers.\n"
		amount = random.randint(6, 10)
	elif size == "huge":
		description = "An army of undead soldiers.\n"
		amount = random.randint(10, 20)
	soldiers = [ UndeadSoldier(random.choice(levels)) if random.randint(0, 10) < 7 else UndeadKnight(random.choice(levels)) for x in range(amount+1)]
	return soldiers, description

def lesser_demon_pack(size):
	description = "A lesser demon.\n"
	beta_demon = None
	levels = list(range(1,10))
	beta_levels = list(range(1,10))
	amount = 1
	if size == "small":
		amount = random.randint(1, 3)
		if amount != 1:
			description = "A small group of lesser demons.\n"
	elif size == "medium":
		description = "A group of lesser demons.\n"
		amount = random.randint(3, 6)

		if random.randint(0, 10) > 9:
			beta_demon = BetaDemon(random.choice(beta_levels))

	elif size == "big":
		description = "A hoard of lesser demons.\n"
		amount = random.randint(6, 10)

		if random.randint(0, 10) > 6:
			beta_demon = BetaDemon(random.choice(beta_levels))

	elif size == "huge":
		description = "Lesser demons are everywhere.\n"
		amount = random.randint(10, 20)

		if random.randint(0, 10) > 3:
			beta_demon = BetaDemon(random.choice(beta_levels))

	demons = [ LesserDemon(random.choice(levels)) for x in range(amount+1)]
	if beta_demon:
		demons.append(beta_demon)
		description+= "A beta demon.\n"
	return demons, description

def beta_demon():
	description = "A beta demon.\n"
	levels = list(range(1,10))
	beta_demon = BetaDemon(random.choice(levels))
	return [beta_demon], description

def peasant_pack(size):
	description = "A peasant.\n"
	levels = list(range(1,10))
	thief = None
	amount = 1
	if size == "small":
		amount = random.randint(1, 3)
		if amount != 1:
			description = "A small group of Peasants.\n"
	elif size == "medium":
		description = "A group of Peasants.\n"
		amount = random.randint(3, 6)

		if random.randint(0, 10) > 9:
			thief = Thief(random.choice(levels))
	elif size == "big":
		description = "A hoard of Peasants.\n"
		amount = random.randint(6, 10)
		if random.randint(0, 10) > 6:
			thief = Thief(random.choice(levels))
	elif size == "huge":
		description = "Peasants are everywhere.\n"
		amount = random.randint(10, 20)
		if random.randint(0, 10) > 3:
			thief = Thief(random.choice(levels))
	peasants = [ Peasant(random.choice(levels)) for x in range(amount+1)]
	if thief:
		peasants.append(thief)
		description+= "A thief accompanies them.\n"
	return peasants, description

def thief():
	description = "A thief.\n"
	thief = Thief()
	return [thief], description

def thugs(size):
	description = "A thug.\n"
	levels = list(range(1,5))
	amount = 1
	if size == "small":
		amount = random.randint(2, 3)
		if amount != 1:
			description = "A small group of thugs.\n"
	elif size == "medium":
		description = "A group of thugs.\n"
		amount = random.randint(3, 5)

	elif size == "big":
		description = "A hoard of thugs.\n"
		amount = random.randint(5, 8)

	elif size == "huge":
		description = "thugs are everywhere.\n"
		amount = random.randint(8, 15)
	thugs = [ Thug(random.choice(levels)) for x in range(amount+1)]
	return thugs, description

enemy_tables = { # difficulty rating: (function to get enemy or enemy group, params)
	"common": { 
		"1": (rat_pack, [] ),
		"1": (rat_pack,["small"] ),
		"5": (rat_pack, ["medium"] ),
		"10": (rat_pack, ["big"] ),
		"30": (rat_pack, ["huge"] )
	},
	"animal": { 
		"1": (wolf_pack,[] ),
		"1": (wolf_pack,["small"] ),
		"10": (wolf_pack, ["medium"] ),
		"10": (bear, [] ),
		"30": (wolf_pack, ["big"] ),
		"50": (wolf_pack, ["huge"] )
	},
	"undead": { 
		"1": (undead_soldier_pack,[] ),
		"1": (undead_soldier_pack,["small"] ),
		"2": (undead_soldier_pack, ["medium"] ),
		"10": (undead_soldier_pack, ["big"] ),
		"30": (undead_soldier_pack, ["huge"] )
	},
	"demon": { 
		"1": (lesser_demon_pack,[] ),
		"1": (lesser_demon_pack,["small"] ),
		"3": (lesser_demon_pack, ["medium"] ),
		"10": (beta_demon, [] ),
		"20": (lesser_demon_pack, ["big"] ),
		"30": (lesser_demon_pack, ["huge"] )
	},
	"human": { 
		"1": (peasant_pack,[] ),
		"1": (thugs, []),
		"5": (thugs, ["small"]),
		"10": (thugs, ["medium"]),
		"1": (peasant_pack,["small"] ),
		"5": (peasant_pack, ["medium"] ),
		"5": (thief, [] ),
		"10": (peasant_pack, ["big"] ),
		"30": (peasant_pack, ["huge"] )
	},
}