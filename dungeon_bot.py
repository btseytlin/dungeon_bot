import persistence
from creatures import Player
import bot_events
import uuid
import json
import logging
import util
import pprint
import datetime
# read apikey from file

persistence_controller = persistence.get_persistence_controller_instance()


def get_dungeon_bot_instance():
	if DungeonBot.instance:
		return DungeonBot.instance

def event_over_callback(uid):
	logging.debug("Removing event %s"%(uid))
	event = DungeonBot.events[uid]
	for user in event.users:
		if persistence_controller.is_registered(user):
			player = persistence_controller.get_ply(user)

			print("registered player: %s"%(player.to_json()))
			player.event = None # Free all players from event

	del DungeonBot.events[uid] #delete event
	logging.debug("Event %s removed"%(uid))

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
	}

	instance = None
	events = {}
	last_update_id = None
	api = None
	#set webhook

	def __init__(self):
		logging.debug("DungeonBot initialized")
		self.time_started = datetime.datetime.now()
		instance = self

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
			return(util.print_available_commands(allowed_commands))

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
				logging.debug("Got update with id %d"%(update.update_id))
				self.last_update_id = update.update_id+1
				logging.debug("Last update id is %d"%(self.last_update_id))

				message = update.message
				if datetime.datetime.fromtimestamp(message.date) >= self.time_started:
					logging.info(("[MESSAGE] %s: %s")%(message.from_user.username, message.text))
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
			if ply.event and self.events[ply.event]: #Check if player is in event

				self.api.sendMessage(user.id, self.events[ply.event].handle_command(command, *args)) #If he is, let the event handle the message
			else:
				#parse command on your own
				self.api.sendMessage(user.id, self.handle_command(user, command, *args))

	def register_player(self, user):
		new_player = Player(None, None, None) #Create an empty player object
		persistence_controller.add_player(user, new_player) #Add him to Persistence
		uid = util.get_uid()
		registration = bot_events.RegistrationEvent(event_over_callback, uid, user) #Create a registration event
		self.events[uid] = registration #add event to collection of events
		self.api.sendMessage(user.id, registration.greeting_message)
		logging.debug("Registration event %s created"%(uid))

	def open_inventory(self, user):
		uid = util.get_uid()
		inv = bot_events.InventoryEvent(event_over_callback, uid, user) #Create a registration event
		self.events[uid] = inv #add event to collection of events
		logging.debug("Inventory event %s created"%(uid))
		return(inv.greeting_message)
		






