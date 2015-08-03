#!/usr/bin/env python3
import dungeon_bot
from dungeon_bot.dungeon_bot import DungeonBot
import telegram
#from telegram import Bot
import atexit
import logging

from logging.handlers import TimedRotatingFileHandler
api_token_path = 'data/api.token'

def clean_up():
	if dungeon_bot and dungeon_bot.timer:
		dungeon_bot.timer.cancel()

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

with open(api_token_path) as f:
	apitoken = f.read()
tg = telegram.Bot(token=apitoken) 

dungeon_bot = DungeonBot()
dungeon_bot.api = tg

dungeon_bot.start_main_loop()
	
atexit.register(clean_up)
