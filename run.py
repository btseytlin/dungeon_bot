#!/usr/bin/env python3
import dungeon_bot
from dungeon_bot.dungeon_bot import DungeonBot
import telegram
from telegram import TelegramError
#from telegram import Bot
import atexit
import logging

from logging.handlers import TimedRotatingFileHandler

api_token_path = 'data/api.token'

dungeon_bot_instance = None
def clean_up():
	if dungeon_bot_instance and dungeon_bot_instance.timer:
		dungeon_bot_instance.timer.cancel()
	# else:
	# 	DungeonBot.get_instance().timer.cancel()
	#DungeonBot.resart()

def start():
	try:
		global dungeon_bot_instance
		with open(api_token_path) as f:
			apitoken = f.read().strip()
		tg = telegram.Bot(token=apitoken) 

		dungeon_bot_instance = DungeonBot()
		dungeon_bot_instance.api = tg

		dungeon_bot_instance.start_main_loop()
	except (KeyboardInterrupt):
		logger.exception("Finished program.")
		clean_up()


log_path = './logs/botlog.log'

logger = logging.getLogger('dungeon_bot')

logger.setLevel(logging.DEBUG)

fh = TimedRotatingFileHandler(log_path, when="d", interval = 1, backupCount = 5)
fh.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
console.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(fh)



combat_log_path = './logs/combat.log'
combat_logger = logging.getLogger('dungeon_bot_combat')
combat_logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(combat_log_path, when="d", interval = 1, backupCount = 5)
fh.setLevel(logging.INFO)
combat_logger.addHandler(fh)

atexit.register(clean_up)

start()

