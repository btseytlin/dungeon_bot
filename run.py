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

combat_log_path = './logs/combat.log'
combat_logger = logging.getLogger('dungeon_bot_combat')
combat_logger.setLevel(logging.INFO)
fh = logging.FileHandler(combat_log_path)
fh.setLevel(logging.INFO)
combat_logger.addHandler(fh)

with open(api_token_path) as f:
	apitoken = f.read()
tg = telegram.Bot(token=apitoken) 

dungeon_bot = DungeonBot()
dungeon_bot.api = tg

dungeon_bot.start_main_loop()
	