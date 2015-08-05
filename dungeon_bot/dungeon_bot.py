#!/usr/bin/env python3
from .persistence import PersistenceController
from .creatures import Player
from .bot_events import *
from .util import *
from .dungeon import *
import logging
import datetime
import random
import threading
import gc
persistence_controller = PersistenceController.get_instance()

logger = logging.getLogger('dungeon_bot')
def get_dungeon_bot_instance():
	if DungeonBot.instance:
		return DungeonBot.instance

def chat_over_callback(event):
	logger.debug("Chat tried to shutdown, this is a bug.")
	return ""

def event_over_callback(event):
	persistence_controller.save_players()
	logger.debug("Removing event %s"%(event.uid))
	del DungeonBot.events[event.uid] #delete event
	logger.debug("Event %s removed"%(event.uid))
	gc.collect()
	return ""
	

def crawl_event_over_callback(event):
	persistence_controller.save_players()
	for user in event.users:
		ply = persistence_controller.get_ply(user)
		ply.health = ply.stats["max_health"]
		ply.energy = ply.stats["max_energy"]
		ply.dead = False
		ply.refresh_derived()
	event_over_callback(event)
	return DungeonBot.instance.status()

def lobby_event_lover_callback(lobby):
	logger.debug("Removing lobby %s"%(lobby.uid))
	if lobby.uid in DungeonBot.open_lobbies:
		del DungeonBot.open_lobbies[lobby.uid]
	event_over_callback(lobby)
	if len(lobby.users) > 0:
		dungeon = Dungeon.new_dungeon([persistence_controller.get_ply(u) for u in lobby.users])
		
		dungeon_crawl = DungeonCrawlEvent(crawl_event_over_callback, lobby.users, dungeon)
		DungeonBot.events[dungeon_crawl.uid] = dungeon_crawl

		broadcast = []
		msg = dungeon_crawl.greeting_message
		for u in lobby.users:
			broadcast.append([u, msg])
		return broadcast
	return DungeonBot.instance.status()



class DungeonBot(object):

	allowed_commands = {
		"examine": "shows your stats", 
		"ex": "shows your stats", 
		"stats": "shows your stats",
		"st": "shows your stats",
		"info": "shows help",
		"help": "shows help",
		"h": "shows help",
		"inventory": "shows your inventory",
		"inv": "shows your inventory",
		"levelup": "opens the level up dialogue",
		"lvl": "opens the level up dialogue",
		"status": "shows where you are and what you are doing",
		"lobbies": "shows active lobbies with free slots",
		"lob": "shows active lobbies with free slots",
		"join [lobby]": "joins the specified lobby",
		"join": "joins a random lobby",
		"create [player_amount]": "creates a lobby",
		"cr [player_amount]": "creates a lobby",
		"reset_character [character name]": "removes your character and starts the registration process again, can't be undone!",
		"chat": "joins global chat"
	}

	instance = None
	events = {}
	open_lobbies = {}
	last_update_id = None
	api = None
	#set webhook

	intro_message = "Welcome! DungeonBot is a text RPG. Make a character, raid a dungeon, kill monsters, loot them for shiny things! And do it with your friends too!\nThe bot is very much WIP, so beware of bugs. Please send feedback to @btseytlin.\nHappy dungeon crawling!\n"
	def __init__(self):
		print('DungeonBot initialized')
		logger.debug("DungeonBot initialized")
		self.time_started = datetime.datetime.now()
		self.chat = ChatEvent(chat_over_callback)
		

		self.notifications = []

		with open("data/notifications.json") as f:
			notfications_plaintext = f.read()
			self.notifications = json.loads(notfications_plaintext) 
		print("Notifications loaded:\n%s"%("\n".join(["%s : %s"%(notification["id"], notification["text"]) for notification in self.notifications])))
		DungeonBot.instance = self

	@staticmethod
	def get_instance():
		if not DungeonBot.instance:
			DungeonBot.instance = DungeonBot()
		return DungeonBot.instance

	def resart():
		global persistence_controller
		persistence_controller.clear_events()
		#PersistenceController.instance = None
		#persistence_controller = PersistenceController.get_instance()
		DungeonBot.events = {}
		DungeonBot.open_lobbies = {}
		#DungeonBot.last_update_id += 2

	def cleanse_dead_events(self):
		for key in list(DungeonBot.events.keys()):
			event = DungeonBot.events[key]
			minutes_since_activity = divmod((datetime.datetime.now() - event.last_activity).total_seconds(), 60)[0]
			if minutes_since_activity > settings.event_cleanse_time:
				event.finish()
				logger.info("Finished %s %s for having %d minutes since last activity."%(event.__class__.__name__, event.uid, minutes_since_activity) )

	def status(self, user=None):
		msg = 'You are in the main screen of DungeonBot.\nFrom here you can inspect your inventory, your stats and characteristics, create and join lobbies.\nCreate a lobby by typing "create 1" (means "create lobby for one player") and jump straight into action!\n'
		msg += "There are %d players in the chat. Type \"chat\" to join them."%(len(self.chat.users))
		return msg

	def handle_command(self, user, command, *args):
		if (command in ["examine","ex","stats","st"]):
			argument = " ".join(args).lower()
			if len(args) == 0 or argument=="self" or argument == str(user.id) or argument.lower() == persistence_controller.get_ply(user).name.lower():
				return (persistence_controller.get_ply(user).examine_self())
		elif (command in ["inventory", "inv"]):
			return self.open_inventory(user)
		elif (command in ["levelup","lvl"]):
			return(self.open_level_up(user))
		elif (command in ["help","info","h"]):
			return(print_available_commands(self.allowed_commands))
		elif (command in ["lob","lobbies"]):
			return(self.list_lobbies())
		elif (command in ["chat"]):
			return(self.chat.add_user(user))
		elif (command in ["status"]):
			msg = self.status(user)
			return msg
		elif (command in ["join"]):
			lobby_uid = None
			if len(args) != 0:
				lobby_uid = args[0]
			return(self.join_lobby(user, lobby_uid))
		elif (command in ["reset_character"]):
			character = ""
			if len(args) != 0:
				character = " ".join(args).lower()
				if character == persistence_controller.get_ply(user).name.lower():
					del persistence_controller.players[str(user.id)]
					persistence_controller.save_players()
					return "Character deleted, type something to initiate registration."
				return "Wrong character name."

			return "Type your character name. It's required for confirmation."
		elif (command in ["create", "cr"]):
			if len(args) < 1:
				return "Specify the amount of players!"
			argument = " ".join(args).lower()
			if not argument.isdigit():
				return "Input a number!"
			amount = int(argument)
			lobby_uid = self.new_crawl_lobby(amount)
			return self.join_lobby(user, lobby_uid)

		if len(command.split(" "))>1:
			if isinstance(args, tuple):
				args = list(args)
			args = command.split(" ")[1:] + args
			command = command.split(" ")[0]
			return self.handle_command(user, command, *args)
		return 'Unknown command, try "help".'

	def start_main_loop(self):
		#start dead event collection timer
		self.timer = threading.Timer(600, self.cleanse_dead_events)
		self.timer.start() #run every 10 minutes

		while True:
			if DungeonBot.last_update_id:
				updates = self.api.getUpdates(DungeonBot.last_update_id)
			else:
				updates = self.api.getUpdates()

			for update in updates:
				#logger.debug("Got update with id %d"%(update.update_id))
				DungeonBot.last_update_id = update.update_id+1
				#logger.debug("Last update id is %d"%(self.last_update_id))

				message = update.message
				close_enough = self.time_started - datetime.timedelta(minutes=5)
				if datetime.datetime.fromtimestamp(message.date) >= close_enough :
					logger.info(("[MESSAGE] %s: %s")%(message.from_user.id, message.text))
					self.on_message(message)

	def send_message(self, user, message):
		if persistence_controller.is_registered(user): 
			ply = persistence_controller.get_ply(user)
			for notification in self.notifications:
				if ply.last_read_notification_id < notification["id"]:
					ply.last_read_notification_id = notification["id"]
					message += "\n"+notification["text"]
		self.api.sendMessage(user.id, message)

	def on_message(self, message):
		user = message.from_user

		if not message.text: #if message text is missing or empty its an error
			self.reply_error(user)

		#check if player is registered
		if not persistence_controller.is_registered(user): 
			print("User %s is not registered"%(str(user.username)+"("+str(user.id)+")"))
			self.send_message(user, DungeonBot.intro_message)
			self.register_player(user)
		else:
			ply = persistence_controller.get_ply(user)
			command, args = parse_command(message.text)
			if ply.event: #Check if player is in event
				try:
					response = ply.event.handle_command(user, command, *args)
				except:
					logger.exception("E internal event:")
					if ply.event:
						ply.event.finish()
					persistence_controller.save_players()
					response = "There has been an error.\n The current event has been finished.\n Your character has been saved just in case.\n We will look into the problem soon, but it will be much easier if you send a message to @btseytlin describing what happened.\nCheers!"

				if isinstance(response, list): #it's a broadcast
					for message in response:
						logger.info(("[RESPONSE] to user %s: %s")%(message[0].id, message[1]))

						self.send_message(message[0], message[1])
				else:
					logger.info(("[RESPONSE] to user %s: %s")%(user.id, response))
					self.send_message(user, response) #If he is, let the event handle the message
			else:
				#parse command on your own
				response = self.handle_command(user, command, *args)
				if isinstance(response, list): #it's a broadcast
					for message in response:
						logger.info(("[RESPONSE] to user %s: %s")%(message[0].id, message[1]))
						self.send_message(message[0], message[1])
				else:
					logger.info(("[RESPONSE] to user %s: %s")%(user.id, response))
					self.send_message(user, response)

	def register_player(self, user):
		new_player = Player(user.id, None) #Create an empty player object
		persistence_controller.add_player(user, new_player) #Add him to Persistence
		registration = RegistrationEvent(event_over_callback, user) #Create a registration event
		self.events[registration.uid] = registration #add event to collection of events
		self.send_message(user, registration.greeting_message)
		logger.debug("Registration event %s created"%(registration.uid))

	def open_inventory(self, user):
		inv = InventoryEvent(event_over_callback, user) #Create an inventory event
		self.events[inv.uid] = inv #add event to collection of events
		logger.debug("Inventory event %s created"%(inv.uid))
		return(inv.greeting_message)

	def open_level_up(self, user):
		if persistence_controller.get_ply(user).level_up_points > 0 or persistence_controller.get_ply(user).perk_points >0 :
			level_up = LevelUpEvent(event_over_callback, user)
			self.events[level_up.uid] = level_up
			logger.debug("Levelup event %s created"%(level_up.uid))
			return(level_up.greeting_message)
		return "You don't have any perk points or characteristic points to spend."

	def new_crawl_lobby(self, total_users):
		lobby = DungeonLobbyEvent(lobby_event_lover_callback, total_users) #Create a dungeon lobby event
		self.events[lobby.uid] = lobby #add event to collection of events
		self.open_lobbies[lobby.uid] = lobby
		logger.debug("Lobby event %s created"%(lobby.uid))
		return(lobby.uid)

	def list_lobbies(self):
		lobbies = []
		for key in list(self.open_lobbies.keys()):
			if self.open_lobbies[key]:
				lobby = self.open_lobbies[key]
				if not lobby.is_enough_players():
					lobby_desc = "Lobby %s\n"%(lobby.uid)
					lobby_desc += "%d out of %d users:"%(len(lobby.users), lobby.total_users)
					lobby_desc += ", ".join([ u.id for u in lobby.users ]) + ".\n"
					lobbies.append(lobby_desc)
		if len(lobbies) > 0:
			lobbies.insert(0, "Currently open lobbies:")
		else:
			lobbies.insert(0, "No lobbies found")
		return "\n".join(lobbies)

	def join_lobby(self, user, lobby_uid=None):
		if not lobby_uid:
			if len(list(self.open_lobbies.keys())) > 0:
				lobby_uid = random.choice(list(self.open_lobbies.keys()))#select random lobby
			else:
				lobby_uid = self.new_crawl_lobby(1) 
		if not lobby_uid in list(self.open_lobbies.keys()):
			return "No such lobby!"

		lobby = self.open_lobbies[lobby_uid]
		logger.debug("User %s joined lobby %s"%(str(user.username)+"("+str(user.id)+")", lobby_uid))
		return(lobby.add_user(user))







