from dungeon_bot.dungeon_bot import DungeonBot
import telegram
import logging

api_token_path = 'data/api.token'


log_path = './logs/botlog.log'
logger = logging.getLogger('dungeon_bot')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_path)
fh.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
console.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(fh)


with open(api_token_path) as f:
	apitoken = f.read()
tg = telegram.Bot(token=apitoken) 

dungeon_bot = DungeonBot()
dungeon_bot.api = tg

try:
	logger.info("Telegram DungeonBot started")
	dungeon_bot.start_main_loop()
except:
	logger.exception("E:")