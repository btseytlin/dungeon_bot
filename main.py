from dungeon_bot import DungeonBot
import telegram
from mock_telegram import MockBot
import logging

logging.basicConfig(level=logging.DEBUG, filename='botlog.log', datefmt='%H:%M:%S')

# read token from file
apitoken = "90526238:AAH75hEHDV0LBDfC1UKyMHnXmoDNB7AeQ6A"
tg = telegram.Bot(token=apitoken)
#tg = MockBot()

dungeon_bot = DungeonBot()
dungeon_bot.api = tg

try:
	dungeon_bot.start_main_loop()
except:
	logging.exception("Exception ")