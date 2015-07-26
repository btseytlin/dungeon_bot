from persistence import PersistenceController
from creatures import Player
from bot_events import *
from util import *
import logging
import datetime
from dungeon import *
import random
persistence_controller = PersistenceController.get_instance()

logger = logging.getLogger('dungeon_bot')
def get_dungeon_bot_instance():
	if DungeonBot.instance:
		return DungeonBot.instance

def event_over_callback(event):
	logger.debug("Removing event %s"%(event.uid))
	del DungeonBot.events[event.uid] #delete event
	logger.debug("Event %s removed"%(event.uid))

def lobby_event_lover_callback(lobby):
	logger.debug("Removing lobby %s"%(lobby.uid))
	del DungeonBot.open_lobbies[lobby.uid]
	event_over_callback(lobby)
	if len(lobby.users) > 0:
		dungeon = Dungeon.new_dungeon([persistence_controller.get_ply(u) for u in lobby.users])
		
		dungeon_crawl = DungeonCrawlEvent(event_over_callback, lobby.users, dungeon)
		DungeonBot.events[dungeon_crawl.uid] = dungeon_crawl

		broadcast = []
		msg = dungeon_crawl.greeting_message
		for u in lobby.users:
			broadcast.append([u, msg])
		return broadcast

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

		"lobbies": "shows active lobbies with free slots",
		"lob": "shows active lobbies with free slots",
		"join [lobby]": "joins the specified lobby",
		"join": "joins a random lobby",
		"create [player_amount]": "creates a lobby",
		"cr [player_amount]": "creates a lobby",
	}

	instance = None
	events = {}
	open_lobbies = {}
	last_update_id = None
	api = None
	#set webhook

	def __init__(self):
		logger.debug("DungeonBot initialized")
		self.time_started = datetime.datetime.now()
		DungeonBot.instance = self

	@staticmethod
	def get_instance():
		if not DungeonBot.instance:
			DungeonBot.instance = DungeonBot()
		return DungeonBot.instance

	def parse_command(self, user, message):
		words = message.text.strip().lower().split(' ')
		command = words[0]
		args = words[1:]
		return command,args

	def handle_command(self, user, command, *args):
		if (command in ["examine","ex","stats","st"]):
			if len(args) > 1:
				return self.reply_error(user)
			elif len(args) == 0 or args[0]=="self" or args[0] == user.username or args[0] == persistence_controller.get_ply(user).name:
				return (persistence_controller.get_ply(user).examine_self())
		elif (command in ["inventory", "inv"]):
			return self.open_inventory(user)
		elif (command in ["help","info","h"]):
			return(util.print_available_commands(self.allowed_commands))
		elif (command in ["lob","lobbies"]):
			return(self.list_lobbies())
		elif (command in ["join"]):
			lobby_uid = None
			if len(args) != 0:
				lobby_uid = args[0]
			return(self.join_lobby(user, lobby_uid))
		elif (command in ["create", "cr"]):
			if len(args) < 1:
				return "Specify the amount of players!"
			amount = int(args[0])
			lobby_uid = self.new_crawl_lobby(amount)
			return self.join_lobby(user, lobby_uid)

		return 'Unknown command, try "help"'


	def reply_error(self, user):
		self.api.sendMessage(user.id, "Unknown command, try 'help'.")

	def start_main_loop(self):
		while True:
			if self.last_update_id:
				updates = self.api.getUpdates(self.last_update_id)
			else:
				updates = self.api.getUpdates()

			for update in updates:
				logger.debug("Got update with id %d"%(update.update_id))
				self.last_update_id = update.update_id+1
				logger.debug("Last update id is %d"%(self.last_update_id))

				message = update.message
				close_enough = self.time_started - datetime.timedelta(minutes=15)
				if datetime.datetime.fromtimestamp(message.date) >= close_enough :
					logger.info(("[MESSAGE] %s: %s")%(message.from_user.username, message.text))
					self.on_message(message)


	def on_message(self, message):
		user = message.from_user

		if not message.text: #if message text is missing or empty its an error
			self.reply_error(user, message)

		#check if player is registered
		if not persistence_controller.is_registered(user): 
			print("User %s is not registered"%(user.username))
			self.api.sendMessage(user.id, "This bot lets you crawl dungeons! Lets register your info so you can play!")
			self.register_player(user)
		else:
			ply = persistence_controller.get_ply(user)
			command, args = self.parse_command(user, message)
			if ply.event: #Check if player is in event
				response = ply.event.handle_command(user, command, *args)

				if isinstance(response, list): #it's a broadcast
					print("its a fooking broadcast mate")
					for message in response:
						self.api.sendMessage(message[0].id, message[1])
				else:
					self.api.sendMessage(user.id, response) #If he is, let the event handle the message
			else:
				#parse command on your own
				response = self.handle_command(user, command, *args)
				if isinstance(response, list): #it's a broadcast
					for message in response:
						self.api.sendMessage(message[0].id, message[1])
				else:
					self.api.sendMessage(user.id, response)

	def register_player(self, user):
		new_player = Player(user.username, None, None, None) #Create an empty player object
		persistence_controller.add_player(user, new_player) #Add him to Persistence
		registration = RegistrationEvent(event_over_callback, user) #Create a registration event
		self.events[registration.uid] = registration #add event to collection of events
		self.api.sendMessage(user.id, registration.greeting_message)
		logger.debug("Registration event %s created"%(registration.uid))

	def open_inventory(self, user):
		inv = InventoryEvent(event_over_callback, user) #Create an inventory event
		self.events[inv.uid] = inv #add event to collection of events
		logger.debug("Inventory event %s created"%(inv.uid))
		return(inv.greeting_message)
		
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
				if not lobby.is_enough_players:
					lobby_desc = "Lobby %s\n"%(lobby.uid)
					lobby_desc += "%d out of %d users:"%(len(lobby.users), lobby.total_users)
					lobby_desc += ", ".join([ u.username for u in lobby.users ]) + ".\n"
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
		logger.debug("User %s joined lobby %s"%(user.username, lobby_uid))
		return(lobby.add_user(user))







