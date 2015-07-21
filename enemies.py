import math
import random
from creatures import Enemy
def retrieve_enemy_for_difficulty(difficulty):
	candidates = []
	difficulty_margin = 0.25
	for i in range(0, len(enemy_list)):
		if abs(enemy_list[i][0] - difficulty <= difficulty_margin * difficulty):
			candidates.append(enemy_list[i][1])

	if len(candidates) == 0:
		candidates.append(random.choice(enemy_list)[1])

	return enemy_listing[random.choice(candidates)]()


rat_characteristics = {
			"strength": 1, #how hard you hit
			"vitality": 1, #how much hp you have
			"dexterity": 2, #how fast you act, your position in turn qeue
			"intelligence": 1, #how likely you are to strike a critical
			"faith": 1, #how much energy you have
		}

rat_stats = "stats": {
			"health": 10,
			"energy": 10,
			"max_health": 10,
			"max_energy": 10,
			"defence": "1d1",
			"evasion": "1d1",
			"level": 1,
			"exp_value": 10
		}

rat_abilities = ["rodent_bite"]
class Rat(Enemy):
	def __init__(self, name="rat", race="rodent", combat_class="animal", characteristics = rat_characteristics, stats=rat_stats, description="An angry grey rat.", inventory=[], equipment=None, tags=["animate", "rodent", "animal", "small"],abilities=["rodent_bite"],modifiers=[]):

		Enemy.__init__(self, name, race, combat_class,characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)

	def act(self):
		pass

big_rat_characteristis: {
	"strength": 1, #how hard you hit
	"vitality": 2, #how much hp you have
	"dexterity": 2, #how fast you act, your position in turn qeue
	"intelligence": 1, #how likely you are to strike a critical
	"faith": 1, #how much energy you have
}
big_rat_stats: {
	"health": 20,
	"energy": 10,
	"max_health": 20,
	"max_energy": 10,
	"defence": "1d2",
	"evasion": "1d1",
	"level": 1,
	"exp_value": 10
}
class BigRat(Enemy):
	def __init__(self, name="big rat", race="rodent", combat_class="animal", characteristics = big_rat_characteristis, stats=big_rat_stats, description="A big angry grey rat.", inventory=[], equipment=None, tags=["animate", "rodent", "animal", "small"],abilities=["rodent_bite"],modifiers=[]):

		Enemy.__init__(self, name, race, combat_class,characteristics, stats, description, inventory, equipment, tags, abilities, modifiers)

	def act(self):
		pass

enemy_list = [
	(1, "rat"),
	(1, "big rat")
]

enemy_listing = {
	"rat": Rat,
	"big rat": BigRat
}

