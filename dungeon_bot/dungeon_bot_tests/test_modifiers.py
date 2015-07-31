from util import *
from creatures import *
from items import *
from enemies import *
from abilities import *
from modifiers import *
import logging

logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test items loaded")

def test_bonus_modifier():
	logger.info("Testing char changes.\n\n")
	item = get_item_by_name("ring of modifier test", 1)
	logger.info("Retrieved item:\n%s"%(item.examine_self()))
	ply = Player("testman", "test")
	logger.info("Retrieved player:\n%s\n"%(ply.examine_self()))
	ply.inventory.append(item)
	ply.equip(item)
	assert ply.characteristics["vitality"] == 6 and ply.stats["max_health"] == 60

	logger.info("Player equipped the item:\n%s\n%s"%(ply.examine_self(), ply.examine_equipment()))
	ply.unequip(item)
	assert ply.characteristics["vitality"] == 5 and ply.stats["max_health"] == 50
	logger.info("Player unequipped the item:\n%s\n%s"%(ply.examine_self(), ply.examine_equipment()))

def test_shielded_modifier():
	logger.info("Testing shielded modifier.\n\n")
	ply = Player("testman", "test")

	defences = [ply.defence for x in range(10000)]
	logger.info("Average defence:\n%f"%(sum(defences)/len(defences)))


	item = get_item_by_name("shield", 1)
	logger.info("Retrieved item:\n%s"%(item.examine_self()))
	logger.info("Retrieved player:\n%s\n"%(ply.examine_self()))
	ply.inventory.append(item)
	ply.equip(item)
	ability = abilities["shieldup"]
	logger.info("Player equipped the item:\n%s\n%s"%(ply.examine_self(), ply.examine_equipment()))
	defences = [ply.defence for x in range(10000)]
	logger.info("Average defence with shield:\n%f"%(sum(defences)/len(defences)))

	ability_info = ability.use( ply, None, item )
	msg = ability_info.description
	logger.info("Used ability, msg: \n%s\n"%(msg))
	logger.info("Ply status now:\n%s\n"%(ply.examine_self()))

	defences = [ply.defence for x in range(10000)]
	logger.info("Average defence with shield and modifier:\n%f"%(sum(defences)/len(defences)))

def run_tests():
	logger.info(" -- Test simple bonus modifiers")
	test_bonus_modifier()

	logger.info(" -- Test shielded modifier")
	test_shielded_modifier()

