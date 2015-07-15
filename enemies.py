import math
import random
from creatures import Enemy
def retrieve_enemy_for_difficulty(difficulty):
	candidates = []
	for i in range(0, len(enemy_list)):
		if abs(enemy_list[i][0] - difficulty <= difficulty/4.0):
			candidates.append(enemy_list[i][1])

	if len(candidates) == 0:
		candidates.append(random.choice(enemy_list)[1])

	return Enemy.de_json(enemy_listing[random.choice(candidates)])


enemy_list = [
	(1, "rat"),
	(1, "big rat")
]

enemy_listing = {
	"rat": {
		"name": "rat", 
		"race": "animal",
		"combat_class": "animal", 
		"characteristics": {
			"strength": 1, #how hard you hit
			"vitality": 1, #how much hp you have
			"dexterity": 2, #how fast you act, your position in turn qeue
			"intelligence": 1, #how likely you are to strike a critical
			"faith": 1, #how much energy you have
		},
		"stats": {
			"health": 10,
			"energy": 10,
			"max_health": 10,
			"max_energy": 10,
			"defence": "1d1",
			"evasion": "1d1",
			"level": 1,
			"exp_value": 10
		},
		"description": "A rat",
		"inventory": None,
		"equipment": None,
		"tags":["animate", "rodent", "animal", "small"],
		"abilities":["rodent_bite"],
		"modifiers":None
	},
	"big rat": {
		"name": "big rat", 
		"race": "animal",
		"combat_class": "animal", 
		"characteristics": {
			"strength": 1, #how hard you hit
			"vitality": 2, #how much hp you have
			"dexterity": 2, #how fast you act, your position in turn qeue
			"intelligence": 1, #how likely you are to strike a critical
			"faith": 1, #how much energy you have
		},
		"stats": {
			"health": 20,
			"energy": 10,
			"max_health": 20,
			"max_energy": 10,
			"defence": "1d2",
			"evasion": "1d1",
			"level": 1,
			"exp_value": 10
		},
		"description": "A rat",
		"inventory": None,
		"equipment": None,
		"tags":["animate", "rodent", "animal", "small"],
		"abilities":["rodent_bite"],
		"modifiers":None
	}
}

