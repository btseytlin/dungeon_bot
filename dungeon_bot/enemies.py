from creatures import Enemy, Player
from abilities import *
import random
def retrieve_enemy_for_difficulty(difficulty):
	candidates = []
	difficulty_margin = 0.25
	for i in range(0, len(enemy_list)):
		if abs(enemy_list[i][0] - difficulty <= difficulty_margin * difficulty):
			candidates.append(enemy_list[i][1])

	if len(candidates) == 0:
		candidates.append(random.choice(enemy_list))

	prototype = random.choice(candidates)
	return prototype()


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
		"club" : 20,
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
	}
	loot_coolity = 0.5

	def __init__(self, name="rat", race="rodent", combat_class="animal", level=1, characteristics = rat_characteristics, stats=None, description="An angry grey rat.", inventory=[], equipment=default_equipment, tags=["animate", "rodent", "animal", "small"],abilities=[],modifiers=[], exp_value=10):
		Enemy.__init__(self, name, race, combat_class, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("rodent_teeth", 0)
		self.equip(teeth)

	def act(self, turn_qeue):
		attack_msgs = ""

		while self.energy >= 2:
			targets = False
			for c in turn_qeue:
				if not c.dead and isinstance(c, Player):
					targets = True
					attack_msgs += self.abilities[0].__class__.use(self, c)
			if not targets:
				break

		return attack_msgs



big_rat_characteristics = {
	"strength": 4, #how hard you hit
	"vitality": 3, #how much hp you have
	"dexterity": 3, #how fast you act, your position in turn qeue
	"intelligence": 1, #how likely you are to strike a critical
	"faith": 1, #how much energy you have
}

class BigRat(Enemy):
	drop_table = {
		"club" : 20,
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
	}
	
	loot_coolity = 0.5

	def __init__(self, name="big rat", race="rodent", combat_class="animal", level=1, characteristics = big_rat_characteristics, stats=None, description="A big angry grey rat.", inventory=[], equipment=default_equipment, tags=["animate", "rodent", "animal", "small"],abilities=[],modifiers=[], exp_value=20):
		Enemy.__init__(self, name, race, combat_class, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		teeth = get_item_by_name("rodent_teeth", 0)
		self.equip(teeth)

	def act(self, turn_qeue):
		attack_msgs = ""

		while self.energy >= 2:
			targets = False
			for c in turn_qeue:
				if not c.dead and isinstance(c, Player):
					targets = True
					attack_msgs += self.abilities[0].__class__.use(self, c)
			if not targets:
				break

		return attack_msgs


enemy_list = [
	(1, Rat),
	(1, BigRat)
]