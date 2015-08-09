#!/usr/bin/env python3
from .persistence import PersistenceController
from .creatures import Player
from .bot_events import *
from .util import *
from .level_perks import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardHide
import logging
import datetime
import random
import gc



persistence_controller = PersistenceController.get_instance()


logger = logging.getLogger('dungeon_bot')
def get_dungeon_bot_instance():
	if DungeonBot.instance:
		return DungeonBot.instance

def chat_over_callback(event):
	logger.debug("Chat tried to shutdown, this is a bug.")
	return ""

def registration_over_callback(event):
	if str(event.user.id) in DungeonBot.registration_events.keys():
		del DungeonBot.registration_events[str(event.user.id)]
	event_over_callback(event)
	
def event_over_callback(event):
	if event.terminated_for_idle:
		for user in event.users:
			DungeonBot.instance.send_message(user, "Event was finished for inactivity.")
	persistence_controller.save_players()
	logger.debug("Removing event %s"%(event.uid))
	if event.uid in DungeonBot.events.keys():
		del DungeonBot.events[event.uid] #delete event
	logger.debug("Event %s removed"%(event.uid))
	gc.collect()
	return ""
	



def lobby_event_lover_callback(lobby):
	logger.debug("Removing lobby %s"%(lobby.uid))
	if lobby.uid in DungeonBot.lobbies:
		del DungeonBot.lobbies[lobby.uid]
	event_over_callback(lobby)

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
		"level up": "opens the level up dialogue",
		"lvl": "opens the level up dialogue",
		"status": "shows where you are and what you are doing",
		"lobbies": "shows active lobbies with free slots",
		"lob": "shows active lobbies with free slots",
		"join [lobby]": "joins the specified lobby",
		"join": "joins a random lobby",
		"create [player_amount]": "creates a lobby",
		"cr [player_amount]": "creates a lobby",
		"reset_character [character name]": "removes your character and starts the registration process again, can't be undone!",
		"chat": "joins global chat",
		"dev [message]": "sends a message to the developers, use in case of errors or bugs",
		"bug [message]": "sends a message to the developers, use in case of errors or bugs",
		"close keyboard": "closes custom keyboard", "open keyboard": "opens custom keyboard", 
	}

	custom_keyboard_status = { #"userid": "show"/"close"/"never show"
	}

	instance = None
	events = {}
	lobbies = {}
	registration_events = {}
	last_update_id = None
	api = None
	#set webhook

	intro_message = "Welcome! DungeonBot is a text RPG. Make a character, raid a dungeon, kill monsters, loot them for shiny things! And do it with your friends too!\nThe bot is very much WIP, so beware of bugs. Please send feedback using the \"dev\" command .\nHappy dungeon crawling!\n"
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
		DungeonBot.lobbies = {}
		#DungeonBot.last_update_id += 2



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
		elif (command in ["level up","lvl"]) or command == "level" and " ".join(args) == "up":
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
		elif command in ["close"] and " ".join(args) == "keyboard":
			DungeonBot.custom_keyboard_status[str(user.id)] = "close"
			return "Keybroad closed."
		elif command in ["open"] and " ".join(args) == "keyboard":
			DungeonBot.custom_keyboard_status[str(user.id)] = "show"
			return "Keybroad opened."
		elif (command in ["bug", "dev"]):
			if len(args) >0:
				msg = " ".join(args)
				logger.info("[DEVREQUEST] User %s : %s"%(str(user.id),msg))
				return "Your message has been sent to the developers! Thank you!"

			return "Input your message!"
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

		while True:
			if DungeonBot.last_update_id:
				updates = self.api.getUpdates(DungeonBot.last_update_id)
			else:
				updates = self.api.getUpdates()
			try:
				for update in updates:
					#logger.debug("Got update with id %d"%(update.update_id))
					DungeonBot.last_update_id = update.update_id+1
					#logger.debug("Last update id is %d"%(self.last_update_id))

					message = update.message
					close_enough = self.time_started - datetime.timedelta(minutes=5)
					if datetime.datetime.fromtimestamp(message.date) >= close_enough:
						if not message.text or not only_roman_chars(message.text): 
							self.api.sendMessage(message.from_user.id, "There was some error processing your message.\nPlease use English only.")
						else:
							self.on_message(message)
							logger.info(("[MESSAGE] %s: %s")%(message.from_user.id, message.text))
							
			except (KeyboardInterrupt):
				persistence_controller.clear_events()

				for event in list(DungeonBot.events.keys()):
					DungeonBot.events[event].finish()

				for event in list(DungeonBot.registration_events.keys()):
					DungeonBot.registration_events[event].finish()

				for event in list(DungeonBot.lobbies.keys()):
					DungeonBot.lobbies[event].finish()

				raise

				#DungeonBot.resart()
	def get_keyboard(self, user):
		keyboard = [
			["help", "status", "chat"],
			["lobbies", "join", "create 1"],
			["examine self", "inventory", "level up"],
			["close keyboard"],
		]
		return keyboard

	def get_reply_markup(self, user):
		action = "show"
		ply = persistence_controller.get_ply(user)
		if user and str(user.id):
			if ply.event:
				if str(user.id) in ply.event.custom_keyboard_status.keys():
					if ply.event.custom_keyboard_status[str(user.id)] == "close" or ply.event.custom_keyboard_status[str(user.id)] == "never show":
						action = "close"
			else:
				if str(user.id) in DungeonBot.custom_keyboard_status.keys():
					if DungeonBot.custom_keyboard_status[str(user.id)] == "close" or DungeonBot.custom_keyboard_status[str(user.id)] == "never show":
						action = "close"

		markup = None
		keyboard = None
		if action == "show":
			if ply.event:
				keyboard = ply.event.get_keyboard(user)
			else:
				keyboard = self.get_keyboard(user)
			
		if keyboard:
			markup = ReplyKeyboardMarkup(keyboard)
		else:
			markup = ReplyKeyboardHide(True)
		return markup

	def send_message(self, user, message):
		reply_markup = ReplyKeyboardHide(True)
		if persistence_controller.is_registered(user): 
			ply = persistence_controller.get_ply(user)
			for notification in self.notifications:
				if ply.last_read_notification_id < notification["id"]:
					ply.last_read_notification_id = notification["id"]
					message += "\n"+notification["text"]

			reply_markup = self.get_reply_markup(user)

		self.api.sendMessage(user.id, message, None, None, reply_markup)

	def on_message(self, message):
		user = message.from_user
		try:
			#check if player is registered
			if not persistence_controller.is_registered(user): 
				if str(user.id) in DungeonBot.registration_events.keys():
					command, args = parse_command(message.text)
					response = DungeonBot.registration_events[str(user.id)].handle_command(user, command, *args)
					self.send_message(user, response)
				else:
					print("User %s is not registered"%(str(user.id)))
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
						response = "An error occured.\n The current event has been finished.\n Your character has been saved just in case.\n We will look into the problem soon, but it will be much easier if you send a message using  the \"bug\" command describing what happened.\nCheers!"

					if isinstance(response, list): #it's a broadcast
						for msg in response:
							if msg:
								logger.info(("[RESPONSE] to user %s: %s")%(msg[0].id, msg[1]))

								self.send_message(msg[0], msg[1])
					else:
						logger.info(("[RESPONSE] to user %s: %s")%(user.id, response))
						if response:	
							self.send_message(user, response) #If he is, let the event handle the message
				else:
					#parse command on your own
					response = self.handle_command(user, command, *args)
					if isinstance(response, list): #it's a broadcast
						for msg in response:
							if msg:
								logger.info(("[RESPONSE] to user %s: %s")%(msg[0].id, msg[1]))
								self.send_message(msg[0], msg[1])
					else:
						logger.info(("[RESPONSE] to user %s: %s")%(user.id, response))
						if response:
							self.send_message(user, response)
		except:
			logger.exception("E:")
			response = "An error occured.\n The current event has been finished.\n Your character has been saved just in case.\n We will look into the problem soon, but it will be much easier if you send a message using  the \"bug\" command describing what happened.\nCheers!"
			

	def register_player(self, user):
		new_player = Player(user.id, None) #Create an empty player object

		registration = RegistrationEvent(registration_over_callback, new_player, user) #Create a registration event
		DungeonBot.registration_events[str(user.id)] = registration 
		DungeonBot.events[registration.uid] = registration #add event to collection of events
		self.send_message(user, registration.greeting_message)
		logger.debug("Registration event %s created"%(registration.uid))

	def open_inventory(self, user):
		inv = InventoryEvent(event_over_callback, user) #Create an inventory event
		DungeonBot.events[inv.uid] = inv #add event to collection of events
		logger.debug("Inventory event %s created"%(inv.uid))
		return(inv.greeting_message)

	def open_level_up(self, user):
		player = persistence_controller.get_ply(user)
		av_perks = [level_perks_listing[key] for key in level_perks_listing if player.fits_perk_requirements(level_perks_listing[key], level_perks_listing[key].requirements)]
		if player.level_up_points > 0 or player.perk_points >0 and len(av_perks)>0:
			level_up = LevelUpEvent(event_over_callback, user)
			if level_up:
				DungeonBot.events[level_up.uid] = level_up
				logger.debug("Levelup event %s created"%(level_up.uid))
				return(level_up.greeting_message)
		return "You don't have any perk points or perks you can take."

	def new_crawl_lobby(self, total_users):
		lobby = DungeonLobbyEvent(lobby_event_lover_callback, total_users) #Create a dungeon lobby event
		DungeonBot.events[lobby.uid] = lobby #add event to collection of events
		DungeonBot.lobbies[lobby.uid] = lobby
		logger.debug("Lobby event %s created"%(lobby.uid))
		return(lobby.uid)

	def list_lobbies(self):
		lobbies = []
		for key in list(DungeonBot.lobbies.keys()):
			if DungeonBot.lobbies[key]:
				lobby = DungeonBot.lobbies[key]
				if not lobby.is_enough_players() and not lobby.crawl:
					lobby_desc = "Lobby %s\n"%(lobby.uid)
					lobby_desc += "%d out of %d users:"%(len(lobby.users), lobby.total_users)
					lobby_desc += ", ".join([ persistence_controller.get_ply(u).name for u in lobby.users ]) + ".\n"
					lobbies.append(lobby_desc)
		if len(lobbies) > 0:
			lobbies.insert(0, "Currently open lobbies:")
		else:
			lobbies.insert(0, "No lobbies found")
		return "\n".join(lobbies)

	def join_lobby(self, user, lobby_uid=None):
		if not lobby_uid:
			open_lobbes = [lobby for lobby in list(DungeonBot.lobbies.keys()) if not DungeonBot.lobbies[lobby].is_enough_players() and not DungeonBot.lobbies[lobby].crawl]
			if len(open_lobbes) > 0:
				lobby_uid = random.choice(open_lobbes)#select random lobby
			else:
				lobby_uid = self.new_crawl_lobby(1) 
		if not lobby_uid in list(DungeonBot.lobbies.keys()):
			return "No such lobby!"

		lobby = DungeonBot.lobbies[lobby_uid]
		logger.debug("User %s joined lobby %s"%(persistence_controller.get_ply(user).name, lobby_uid))
		if not lobby.is_enough_players() and not lobby.crawl:
			return(lobby.add_user(user))
		else:
			return "The lobby is full or the game already started."







