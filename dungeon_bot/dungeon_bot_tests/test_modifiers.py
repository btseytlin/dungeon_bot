from util import *
from creatures import *
from items import *
from enemies import *
import logging

logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test items loaded")

def test_bonus_modifier():
	logger.info("Testing char changes.\n\n")
	item = get_item_by_name("ring of modifier test", 1)
	logger.info("Retrieved item:\n%s"%(item.examine_self()))
	ply = Player("testman", "test", "test", "test")
	logger.info("Retrieved player:\n%s\n"%(ply.examine_self()))
	ply.inventory.append(item)
	ply.equip(item)
	assert ply.characteristics["vitality"] == 6 and ply.stats["max_health"] == 60

	logger.info("Player equipped the item:\n%s\n%s"%(ply.examine_self(), ply.examine_equipment()))
	ply.unequip(item)
	assert ply.characteristics["vitality"] == 5 and ply.stats["max_health"] == 50
	logger.info("Player unequipped the item:\n%s\n%s"%(ply.examine_self(), ply.examine_equipment()))

def run_tests():
	logger.info(" -- Test simple bonus modifiers")
	test_bonus_modifier()
