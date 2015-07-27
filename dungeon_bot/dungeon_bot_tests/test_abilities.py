import random
import statistics
import abilities
import logging
from util import diceroll, clamp

logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test abilities loaded")
def get_attack_stastics(get_chance, get_damage):
	chances = []
	for i in range(1000):
		chances.append(get_chance())

	#logger.info("Chanes to hit are", chances)

	logger.info("Average chance to hit: %f"%(sum(chances)/len(chances)))
	logger.info("Median chance to hit %f"%(statistics.median(chances)))

	dmgs = []
	for i in range(1000):
		dmgs.append(get_damage())

	#logger.info("Chanes to hit are", chances)
	logger.info("Average dmg %f"%(sum(dmgs)/len(dmgs)))
	logger.info("Median dmg %f"%(statistics.median(dmgs)))

	avg_dmg = []
	for i in range(len(chances)):
		avg_dmg.append(chances[i]/100 * dmgs[i])
	logger.info("Average real dmg per hit: %f"%(sum(avg_dmg)/len(avg_dmg)))

""" Test smash combat formula """
def get_smash_chance_to_hit():
	is_small = int(False)*2
	is_quick = int(False)*2
	is_big = int(False)*3
	is_slow = int(False)*3
	evasion = "2d6"
	accuracy = "4d6"
	dexterity = 5

	chance_to_hit = abilities.Smash.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

	return chance_to_hit

def get_smash_dmg():
	weapon_dmg = "2d6"
	strength = 5
	defence = "5d6"
	is_armored = int(False) * 2
	is_heavy_armored = int(False) * 3
	dmg = abilities.Smash.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)
	return dmg

""" Test rodent bite combat formula """
def get_rodent_bite_chance_to_hit():
	is_small = int(False)
	is_quick = int(False)
	is_big = int(False)
	is_slow = int(False)
	evasion = "2d6"
	accuracy = abilities.RodentBite.base_accuracy
	dexterity = 5

	chance_to_hit = abilities.RodentBite.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

	return chance_to_hit

def get_rodent_bite_dmg():
	dmg = abilities.RodentBite.base_damage
	strength = 3
	defence = "5d6"
	is_armored = int(False) * 3
	is_heavy_armored = int(False) * 5

	dmg = abilities.RodentBite.get_damage(dmg, strength, defence, is_armored, is_heavy_armored)
	return dmg

def run_tests():
	logger.info("Testing Smash ability.\n")
	get_attack_stastics(get_smash_chance_to_hit, get_smash_dmg)
	logger.info("\n")
	logger.info("Testing rodent bite.\n")
	get_attack_stastics(get_rodent_bite_chance_to_hit, get_rodent_bite_dmg)
	logger.info("\n")
