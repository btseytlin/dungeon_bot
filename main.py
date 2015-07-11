from dungeon_bot import DungeonBot
import telegram
from mock_telegram import MockBot
import logging

logging.basicConfig(level=logging.DEBUG, filename='botlog.log', datefmt='%H:%M:%S')

with open("api.token") as f:
	apitoken = f.read()
tg = telegram.Bot(token=apitoken) 
#tg = MockBot()

dungeon_bot = DungeonBot()
dungeon_bot.api = tg

try:
	logging.info("Telegram DungeonBot starting")
	dungeon_bot.start_main_loop()
except:
	logging.exception("Exception ")