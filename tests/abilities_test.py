import random
import statistics
from abilities import Smash
from util import diceroll, clamp

def get_attack_stastics(get_chance, get_damage):
	chances = []
	for i in range(1000):
		chances.append(get_chance_to_hit())

	#print("Chanes to hit are", chances)
	print("Average chance to hit", sum(chances)/len(chances))
	print("Median chance to hit", statistics.median(chances))

	print("")
	dmgs = []
	for i in range(1000):
		dmgs.append(get_dmg())

	#print("Chanes to hit are", chances)
	print("Average dmg", sum(dmgs)/len(dmgs))
	print("Median dmg", statistics.median(dmgs))

	avg_dmg = []
	for i in range(len(chances)):
		avg_dmg.append(chances[i]/100 * dmgs[i])
	print("")
	print("Average real dmg per hit", sum(avg_dmg)/len(avg_dmg))

""" Test smash combat formula """
def get_chance_to_hit():
	is_small = int(False)*2
	is_quick = int(False)*2
	is_big = int(False)*3
	is_slow = int(False)*3
	evasion = "1d6"
	accuracy = "4d6"
	dexterity = 5
	target_dex = 5
	chance_to_hit = Smash.get_chance_to_hit(dexterity, accuracy, evasion, is_small, is_quick, is_big, is_slow)

	return chance_to_hit

def get_dmg():
	weapon_dmg = "2d6"
	strength = 5
	defence = "5d6"
	is_armored = int(False) * 2
	is_heavy_armored = int(False) * 3
	dmg = Smash.get_damage(weapon_dmg, strength, defence, is_armored, is_heavy_armored)
	return dmg

print("Testing smash")
get_attack_stastics(get_chance_to_hit, get_dmg)