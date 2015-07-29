import telegram
import logging

log_path = './logs/test.log'
logger = logging.getLogger('dungeon_bot_test_log')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_path)
fh.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(fh)


# import dungeon_bot.dungeon_bot_tests.test_abilities
# logger.info("Running abilities tests.\n")
# dungeon_bot.dungeon_bot_tests.test_abilities.run_tests()

import dungeon_bot.dungeon_bot_tests.test_jsonify
logger.info("Running jsonification tests.\n")
dungeon_bot.dungeon_bot_tests.test_jsonify.run_tests()

import dungeon_bot.dungeon_bot_tests.test_items
logger.info("Running item tests.\n")
dungeon_bot.dungeon_bot_tests.test_items.run_tests()


import dungeon_bot.dungeon_bot_tests.test_modifiers
logger.info("Running Modifier tests.\n")
dungeon_bot.dungeon_bot_tests.test_modifiers.run_tests()

