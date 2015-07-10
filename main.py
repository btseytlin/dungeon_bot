from bot import DungeonBot
import telegram
from mock_telegram import MockBot

# read token from file

#tg = telegram.Bot(token='token')
tg = MockBot()

DungeonBot.api = tg

DungeonBot.start_main_loop()