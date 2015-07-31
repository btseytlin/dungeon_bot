import random
import statistics
import abilities
import logging
from util import diceroll, clamp
from enemies import *

logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test creatures loaded")

def test_get_enemies_for_difficulty():
	enemies = retrieve_enemies_for_difficulty("animal", 1)
	logger.info("Enemies for diff 1:%s"%(enemies))

	enemies = retrieve_enemies_for_difficulty("animal", 10)
	logger.info("Enemies for diff 10:%s"%(enemies))

	enemies = retrieve_enemies_for_difficulty("animal", 20)
	logger.info("Enemies for diff 20:%s"%(enemies))

	enemies = retrieve_enemies_for_difficulty("animal", 40)
	logger.info("Enemies for diff 40:%s"%(enemies))

def run_tests():
	logger.info("Testing getting random enemies.\n")
	test_get_enemies_for_difficulty()
