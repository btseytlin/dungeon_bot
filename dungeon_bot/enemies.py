from creatures import Enemy, Player
from abilities import *
from items import *
from util import * 
import random
def retrieve_enemies_for_difficulty(enemy_table, difficulty):
	total_len = 100
	right = clamp( difficulty + 0.3 * difficulty, 0, 100)
	left = clamp ( difficulty - 0.3 * total_len, 0, 100)
	#random_int = int(math.ceil(random_in_range_for_coolity(left, right, 0.5)))
	#print(random_int)
	candidates = []
	temp_list = sorted([int(x) for x in list(enemy_tables[enemy_table].keys()) if right >= int(x) > left] )

	if len(temp_list) == 0:
		left = 0
		temp_list = sorted([int(x) for x in list(enemy_tables[enemy_table].keys()) if right >= int(x) > left] )

	
	random_float = random_in_range_for_coolity(0, len(temp_list), 0.8)
	random_enemy = temp_list[int(math.floor(random_float))]
	# prev_num = temp_list[0]
	# for x in temp_list:
	# 	if x <= random_enemy:
	# 		prev_num = x
	# 	if x > random_enemy:
	# 		random_enemy = prev_num
	# 		break

	enemies = enemy_tables[enemy_table][str(random_enemy)]	
	#enemies = enemy_tables[enemy_table][random.choice(candidates)]
	return enemies[0](*enemies[1])


rat_characteristics = {
			"strength": 3, #how hard you hit
			"vitality": 2, #how much hp you have
			"dexterity": 3, #how fast you act, your position in turn qeue
			"intelligence": 1, #how likely you are to strike a critical
			"faith": 1, #how much energy you have
		}


default_equipment = {
	"armor": None,
	"primary_weapon": None,
	"secondary_weapon": None,
	"ring": None,
	"talisman": None,
	"headwear": None
}


rat_abilities = ["rodent_bite"]
class Rat(Enemy):
	drop_table = {
		"club" : 10,
		"sword" : 10,
		"plate armor" : 10,
		"helmet" : 10,
		"dagger" : 10,
		"chainmail" : 10,
		"amulet of defence" : 10,
		"amulet of healing" : 10,
		"ring of fire" : 10,
		"shield" : 10,
		"ring of not dying" : 1,
		"ring of much more dexterity" : 5,
		"ring of more vitality" : 10,
	}
	loot_coolity = 0.5

	def __init__(self, name="rat", level=1, characteristics = rat_characteristics, stats=None, description="An angry grey rat.", inventory=[], equipment=default_equipment, tags=["animate", "rodent", "animal", "small"],abilities=[],modifiers=[], exp_value=10):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("rodent_teeth", 0)
		self.inventory.append(teeth)
		self.equip(teeth)

	def act(self, turn_qeue):
		attack_infos = []

		while self.energy >= 2:
			targets = False
			for c in turn_qeue:
				if not c.dead and isinstance(c, Player):
					targets = True
					attack_infos.append(self.abilities[0].__class__.use(self, c, self.primary_weapon))
			if not targets:
				break

		return attack_infos


big_rat_characteristics = {
	"strength": 4, #how hard you hit
	"vitality": 3, #how much hp you have
	"dexterity": 3, #how fast you act, your position in turn qeue
	"intelligence": 1, #how likely you are to strike a critical
	"faith": 1, #how much energy you have
}

class BigRat(Enemy):
	drop_table = {
		"club" : 10,
		"sword" : 10,
		"plate armor" : 10,
		"helmet" : 10,
		"dagger" : 10,
		"chainmail" : 10,
		"amulet of defence" : 10,
		"amulet of healing" : 10,
		"ring of fire" : 10,
		"shield" : 10,
		"ring of not dying" : 1,
		"ring of much more dexterity" : 5,
		"ring of more vitality" : 10,
	}
	
	loot_coolity = 0.5

	def __init__(self, name="big rat", level=1, characteristics = big_rat_characteristics, stats=None, description="A big angry grey rat.", inventory=[], equipment=default_equipment, tags=["animate", "rodent", "animal", "small"],abilities=[],modifiers=[], exp_value=20):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("rodent_teeth", 0)
		self.inventory.append(teeth)
		self.equip(teeth)

	def act(self, turn_qeue):
		attack_infos = []

		while self.energy >= 2:
			targets = False
			for c in turn_qeue:
				if not c.dead and isinstance(c, Player):
					targets = True
					attack_infos.append(self.abilities[0].__class__.use(self, c,  self.primary_weapon))
			if not targets:
				break

		return attack_infos


enemy_list = { #name to enemy
	"rat": Rat,
	"big rat": BigRat
}

def rat_pack(size):
	description = "A rat"
	amount = 1
	if size == "small":
		description = "A small pack of rats.\n"
		amount = random.randint(1, 3)
	elif size == "medium":
		description = "A pack of rats.\n"
		amount = random.randint(3, 6)
	elif size == "big":
		description = "A hoard of rats.\n"
		amount = random.randint(6, 10)
	elif size == "huge":
		description = "RATS ARE EVERYWHERE.\n"
		amount = random.randint(10, 20)
	rats = [ Rat() if random.randint(0, 10) < 7 else BigRat() for x in range(amount)]
	return rats, description

enemy_tables = {
	"animal": { # coolity rating: (function to get enemy or enemy group, params)
		"1": (rat_pack,["small"] ),
		"10": (rat_pack, ["medium"] ),
		"20": (rat_pack, ["big"] ),
		"30": (rat_pack, ["huge"] )
	}
}