
from util import *
from creatures import *
from items import *
from enemies import *
import logging

logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test items loaded")
"""Test random dice generation"""
def test_random_dice():
	left = 1
	right = 100
	logger.info("\nFor coolity = 1")
	coolity = 1
	randoms = []
	for x in range(10000):
		randoms.append(random_in_range_for_coolity(left, right, coolity))

	top = list(filter(lambda x: x > 0.8*right, randoms))
	bottom = list(filter(lambda x: x < 0.2*right, randoms))
	logger.info("Avg rangom %f"%(sum(randoms)/len(randoms)))
	logger.info("%d top value occurencies"%(len(top)))
	logger.info("%d bottom value occurencies"%(len(bottom)))
	logger.info("%d middle value occurencies"%(abs(len(randoms)-len(top)-len(bottom))))
	logger.info("\nFor coolity = 0.5")
	coolity = 0.5
	randoms = []
	for x in range(10000):
		randoms.append(random_in_range_for_coolity(left, right, coolity))

	top = list(filter(lambda x: x > 0.8*right, randoms))
	bottom = list(filter(lambda x: x < 0.2*right, randoms))
	logger.info("Avg rangom %f"%(sum(randoms)/len(randoms)))
	logger.info("%d top value occurencies"%(len(top)))
	logger.info("%d bottom value occurencies"%(len(bottom)))
	logger.info("%d middle value occurencies"%(abs(len(randoms)-len(top)-len(bottom))))

	logger.info("\nFor coolity = 0")
	coolity = 0
	randoms = []
	for x in range(10000):
		randoms.append(random_in_range_for_coolity(left, right, coolity))

	top = list(filter(lambda x: x > 0.8*right, randoms))
	bottom = list(filter(lambda x: x < 0.2*right, randoms))
	logger.info("Avg rangom %f"%(sum(randoms)/len(randoms)))
	logger.info("%d top value occurencies"%(len(top)))
	logger.info("%d bottom value occurencies"%(len(bottom)))
	logger.info("%d middle value occurencies"%(abs(len(randoms)-len(top)-len(bottom))))

	dices = []
	for x in range(10):
		dices.append(get_dice_in_range(["1d1","6d6"], coolity))
	logger.info(", ".join(dices))

"""Test loot dropping from creatures"""
def test_loot_drop():
	max_attempts = 20
	loot_dropped = False
	i = 0
	while not loot_dropped and i < max_attempts:
		i+=1
		ply = Player("testman", "tester", "testinator", "test")
		enemy = retrieve_enemy_for_difficulty(1)
		death_msg = enemy.die(ply)
		if "loot" in death_msg:
			loot_dropped = True
			assert ply.inventory[0] != None
		else:
			continue
		logger.info("Loot dropped, death msg:\n%s"%(death_msg))
		logger.info("Ply inventory:\n%s"%(ply.examine_inventory()))
		logger.info("Item:\n%s"%(ply.inventory[0].examine_self()))

""" Test equipping armor: defence change, evasion change, granting tags, modifiers and abiltiies """
def test_armor_equip():
	item = "plate_armor"
	armor = get_item_by_name(item, 1)
	assert armor
	logger.info("Retrieved item:\n%s"%(armor.examine_self()))
	ply = Player("testman", "test", "test", "test")
	logger.info("Retrieved player:\n%s\n%s"%(ply.examine_self(), ply.examine_inventory()))
	defences = [ply.defence for x in range(10000)]
	evasions = [ply.evasion for x in range(10000)]
	logger.info("Defence, Evasion without armor:\n%f, %f"%(ply.defence, ply.evasion))
	logger.info("Average defence, evasion without armor:\n%f, %f"%(sum(defences)/len(defences), sum(evasions)/len(evasions)))
	ply.inventory.append(armor)
	logger.info("Gave player the item:\n%s"%(ply.examine_inventory()))
	armor.equip(ply)
	assert "armor" or "heavy armor" in ply.tags
	logger.info("Player equipped the item:%s\n%s"%(ply.examine_self(), ply.examine_equipment()))
	defences = [ply.defence for x in range(10000)]
	evasions = [ply.evasion for x in range(10000)]
	logger.info("Average defence, evasion with armor:\n%f, %f"%(sum(defences)/len(defences), sum(evasions)/len(evasions)))
	
	armor.unequip(ply)
	
	assert not "armor" in ply.tags
	logger.info("Player unequipped the item:\n%s\n%s"%(ply.examine_self(), ply.examine_equipment()))
	defences = [ply.defence for x in range(10000)]
	evasions = [ply.evasion for x in range(10000)]
	logger.info("Average defence, evasion without armor:\n%f, %f"%(sum(defences)/len(defences), sum(evasions)/len(evasions)))

def run_tests():
	logger.info(" -- Testing random dice generation in range.")
	test_random_dice()

	logger.info(" -- Testing loot drop.")
	test_loot_drop()

	logger.info(" -- Testing armor equip.")
	test_armor_equip()