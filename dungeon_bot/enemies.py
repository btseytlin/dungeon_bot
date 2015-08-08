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


lich_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 5, #how much hp you have
	"dexterity": 5, #how fast you act, your position in turn qeue
	"intelligence": 7, #how likely you are to strike a critical
}

class Lich(Enemy):
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

	loot_coolity = 0.8
	def __init__(self, level=1, name="lich", characteristics = lich_characteristics, stats=None, description="A lich.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "undead"],abilities=[],modifiers=[], exp_value=100):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["sword", "rapier", "mace"]), 0 )]
		items.append( get_item_by_name( "shield", 0 ) ) if random.randint(0,10) > 7 else None
		items.append( get_item_by_name( "chainmail" , 0 ) ) if random.randint(0,10) > 2 else None
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

crystaline_characteristics = {
	"strength": 5, #how hard you hit
	"vitality": 10, #how much hp you have
	"dexterity": 1, #how fast you act, your position in turn qeue
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
		print(self.abilities)
		if self.lich:
			if self.lich.dead:
				attack_infos.append(self.abilities[0].__class__.use(self, self.lich, None, combat_event))
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
'''
mage_characteristics = {
	"strength": 2, #how hard you hit
	"vitality": 2, #how much hp you have
	"dexterity": 4, #how fast you act, your position in turn qeue
	"intelligence": 6, #how likely you are to strike a critical
}

class Mage(Enemy):
	drop_table = {
		"club" : 7,
		"dagger" : 7,
		"mace": 4,
		"ring of more intelligence" : 2,
		"ring" : 3,
		"talisman": 4,
		"random": 3,
	}
	loot_coolity = 0.3
	def __init__(self, level=1, name="mage", characteristics = mage_characteristics, stats=None, description="A magical peasant.", inventory=[], equipment=default_equipment, tags=["human", "living", "animate", "humanoid"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "dagger", "mace"]), 0 )]
		items.append( get_item_by_name( random.choice(["chainmail", "helmet"]) , 0 ) ) if random.randint(0,10) > 8 else None
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

		return attack_infos'''

ogre_characteristics = {
	"strength": 9, #how hard you hit
	"vitality": 2, #how much hp you have
	"dexterity": 4, #how fast you act, your position in turn qeue
	"intelligence": 2, #how likely you are to strike a critical
}

class Ogre(Enemy):
	drop_table = {
		"club" : 6,
		"mace": 5,
		"primary weapon": 3,
		"armor": 4,
		"ring of more strength" : 5,
		"helmet": 3,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.7
	def __init__(self, level=1, name="ogre", characteristics = ogre_characteristics, stats=None, description="A slow hulking ogre. It looks hungry for you.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "slow", "big", "human", "living"],abilities=[],modifiers=[], exp_value=500):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "mace"]), 0 )]
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
	#"mage": Mage,
	"ogre": Ogre,
}

""" Common enemy spawn functions """

def rat_pack(size):
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

def wolf_leader(size):
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

def wolf_pack(size, special_enemy=None):
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
<<<<<<< HEAD
		wolf_leader = WolfLeader(random.choice(wolf_leader_levels)) if random.randint(0, 10) > 3 else None

	wolves = [ Wolf(random.choice(wolf_levels)) for x in range(amount+1)]
	if wolf_leader:
		wolves.append(wolf_leader)
=======

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
>>>>>>> 434c8189152f9f4827c3b6f2910a5b83a67e6830
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

""" Undead enemy spawn functions """
def undead_soldier_pack(size, special_enemy=None):
	description = "An undead soldier.\n"
	amount = 1
	if size == "small":
		levels = list(range(1,6))
		amount = random.randint(1, 2)
		if amount > 1:
			description = "A small group of undead soldiers.\n"
	elif size == "medium":
		levels = list(range(6,15))
		description = "A group of undead soldiers.\n"
		amount = random.randint(2, 3)
	elif size == "big":
		levels = list(range(15,35))
		description = "A big group of undead soldiers.\n"
		amount = random.randint(3, 5)
	elif size == "huge":
		levels = list(range(25,50))
		description = "A unit of undead soldiers.\n"
		amount = random.randint(4, 6)

	desc = ""
	lich_group = []
	if special_enemy:
		if special_enemy == "lich":
			if size == "big" and random.randint(0, 10) > 6:
				lich_group, desc = lich("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				lich_group, desc = lich("very strong")
			elif random.randint(0, 10) > 8:
				lich_group, desc = lich()

	description += desc
	soldiers = [ UndeadSoldier(random.choice(levels)) if random.randint(0, 10) < 7 else UndeadKnight(random.choice(levels)) for x in range(amount+1)] + lich_group

	return soldiers, description

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
def lesser_demon_pack(size, special_enemy = None):
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
	if special_enemy:
		if special_enemy == "beta demon":
			if size == "medium" and random.randint(0, 10) > 4:
				beta_demon, desc = beta_demon()
			elif size == "big" and random.randint(0, 10) > 4:
				beta_demon, desc = beta_demon("strong")
			elif size == "huge" and random.randint(0, 10) > 4:
				beta_demon, desc = beta_demon("very strong")

	demons += beta_demon
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

def peasant_pack(size, special_enemy = None):
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

<<<<<<< HEAD
'''def mages():
	description = "A mage."
	levels = list(range(5,10))
	amount = 1
	if size == "small":
		amount = random.randint(1, 3)
		if amount != 1:
			description = "Novice mages.\n"
	elif size == "medium":
		description = "Average mages.\n"
		levels = list(range(10,20))
		amount = random.randint(3, 6)
	elif size == "big":
		description = "Mage overseers.\n"
		levels = list(range(15-25))
		amount = random.randint(4, 7)
	elif size == "huge":
		description = "Grandmaster Mages.\n"
		levels = list(range(40,50))
		amount = random.randint(3, 5)
	mages = [ Mage(random.choice(levels)) for x in range(amount+1)]
	return mages, description
'''

def thugs(size):
=======
def thief(size = None):
	if size == "strong":
		thief_levels = list(range(10, 20))
		thief_enemy = Thief(random.choice(thief_levels))
		description = "An professional thief.\n"
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
>>>>>>> 434c8189152f9f4827c3b6f2910a5b83a67e6830
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

def ogres():
	description = "An ogre."
	levels = list(range(5,15))
	amount = 1
	if size == "small":
		amount = random.randint(1, 3)
		if amount != 1:
			description = "Bridge trolls.\n"
	elif size == "medium":
		description = "Town destroyers.\n"
		levels = list(range(10,20))
		amount = random.randint(3, 6)
	elif size == "big":
		description = "City destroyers.\n"
		levels = list(range(25-35))
		amount = random.randint(4, 7)
	elif size == "huge":
		description = "Goliaths.\n"
		levels = list(range(40,50))
		amount = random.randint(2, 5)
	ogres = [ Ogre(random.choice(levels)) for x in range(amount+1)]
	return ogres, description

enemy_tables = { # difficulty rating: (function to get enemy or enemy group, params)
	"common": {
		"1": (rat_pack, [] ),
		"5": (rat_pack,["small"] ),
		"15": (rat_pack, ["medium"] ),
		"30": (rat_pack, ["big"] ),
	},
	"animal": {
		"1": (wolf_pack,[] ),
		"5": (wolf_pack,["small"] ),
		"10": (wolf_pack, ["medium"] ),
		"15": (wolf_pack, ["medium", "wolf leader"] ),
		"10": (bear, [] ),
		"20": (wolf_pack, ["big"] ),
		"25": (wolf_pack, ["big", "wolf leader"] ),
		"30": (bear, ["strong"] ),
		"40": (wolf_pack, ["huge"] ),
		"50": (wolf_pack, ["huge", "wolf leader"] ),
		"50": (bear, ["very strong"] ),
	},
<<<<<<< HEAD
	"undead": {
=======
	"undead": {

>>>>>>> 434c8189152f9f4827c3b6f2910a5b83a67e6830
		"1": (undead_soldier_pack,[] ),
		"1": (undead_soldier_pack,["small"] ),
		"5": (undead_soldier_pack, ["medium"] ),
		"10": (lich, []),
		"10": (undead_soldier_pack, ["big" ] ),
		"15": (undead_soldier_pack, ["big", "lich"] ),
		"30": (lich, ["strong"]),
		"30": (undead_soldier_pack, ["huge"] ),
		"60": (undead_soldier_pack, ["huge", "lich"] ),
		"50": (lich, ["very strong"]),
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
<<<<<<< HEAD
		"1": (thugs, []),
		"5": (thugs, ["small"]),
		"10": (thugs, ["medium"]),
		"1": (peasant_pack,["small"] ),
		"5": (peasant_pack, ["medium"] ),
		"5": (thief, [] ),
		"10": (peasant_pack, ["big"] ),
		"30": (peasant_pack, ["huge"] )
		#"5": (mages, ["small"]),
		#"15": (mages, ["medium"]),
		#"25": (mages, ["big"]),
		#"35": (mages, ["huge"])
=======
		"5": (peasant_pack,["small"] ),
		"5": (thugs, []),
		"10": (thief, [] ),
		"10": (peasant_pack,["medium"] ),
		"10": (peasant_pack,["medium", "thief"] ),
		"15": (peasant_pack,["medium", "thugs"] ),
		"15": (thugs, ["strong"]),
		"15": (thief, ["strong"]),
		"20": (peasant_pack,["big", "thugs"] ),
		"20": (peasant_pack,["big", "thief"] ),
		"30": (thief, ["very strong"] ),
		"30": (thugs, ["very strong"] ),
		"40": (peasant_pack,["huge"] ),
		"50": (peasant_pack,["huge", "thugs"] ),
		"50": (peasant_pack,["huge", "thief"] ),

>>>>>>> 434c8189152f9f4827c3b6f2910a5b83a67e6830
	},
	"ogre": {
		"8": (ogres,[] ),
		"15": (ogres,["small"] ),
		"20": (ogres, ["medium"] ),
		"30": (ogres, ["big"] ),
		"40": (ogres, ["huge"] )
	},

}
