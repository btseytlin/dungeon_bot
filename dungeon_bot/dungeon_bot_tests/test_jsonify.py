import test
import json
from creatures import Player, Enemy, Creature
import logging

logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test jsonify loaded")

def test_jsonify_player():
	ply = Player("testman", "test", "test", "test")
	logger.info("Player:\n %s\n"%(ply.examine_self()) )
	jsonified = json.dumps(ply.to_json())
	logger.info("Jsonified player:\n %s\n"%(jsonified))
	logger.info("Dejsonified player:\n %s\n"%(Player.de_json(jsonified).examine_self() ))
	jsonified_again = json.dumps(Player.de_json(jsonified).to_json()) 
	logger.info("Jsonified again:\n %s\n"%(jsonified_again))
	#assert json.dumps(Player.de_json(jsonified).to_json()) == jsonified
	#todo compare method for players

def run_tests():
	logger.info("Testing jsonifying Player")
	test_jsonify_player()