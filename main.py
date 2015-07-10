from bot import DungeonBot
from mock_telegram import MockAPI
import telegram

# read token from file

#tg = telegram.Bot(token='token')
tg = MockAPI()

DungeonBot.api = tg

DungeonBot.start_main_loop()