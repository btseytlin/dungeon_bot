import persistence
from creatures import Player
from bot_events import RegistrationEvent
import uuid
import json
import logging
import util
import pprint
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
			ply = persistence_controller.get_ply(user)

			print("registered ply: %s"%(json.dumps(ply.__dict__)))
			ply.event = None # Free all players from event

	del DungeonBot.events[uid] #delete event
	logging.debug("Event %s removed"%(uid))

class DungeonBot(object):

	allowed_commands = {
		"examine": "shows your stats", 
		"stats": "shows your stats",
		"info": "shows help",
		"help": "shows help",
	}

	instance = None
	events = {}
	last_update_id = None
	api = None
	#set webhook

	def __init__(self):
		logging.debug("DungeonBot initialized")
		instance = self

	def parse_command(self, user, message):
		words = message.text.strip().lower().split(' ')
		command = words[0]
		args = words[1:]
		return command,args

	def handle_command(self, user, command, *args):
		if not command in self.allowed_commands.keys():
			return self.reply_error(user)

		if command == "examine" or command == "stats":
			if len(args) > 1:
				return self.reply_error(user)
			elif len(args) == 0 or args[0]=="self" or args[0] == user.username or args[0] == persistence_controller.get_ply(user).name:
				return self.api.sendMessage(user.id, str(persistence_controller.get_ply(user)))

		elif command == "help" or command == "info":
			help_text = "Welcome to dungeon bot lobby! Here you can register, delete and reset characters, view your stats, inventory.\n"
			help_text += "Available commands:\n"

			allowed_comms_descs = {}
			for command, desc in self.allowed_commands.iteritems():
				if not desc in allowed_comms_descs:
					commands_for_desc = [command]
					for comm, descr in self.allowed_commands.iteritems():
						if descr == desc:
							if not comm in commands_for_desc:
								commands_for_desc.append(comm)
					commands_for_desc = ", ".join(commands_for_desc)
					allowed_comms_descs[desc] = commands_for_desc
			allowed_comms = dict(zip(allowed_comms_descs.values(),allowed_comms_descs.keys()))# swap keys and values in dict
			for comms, desc in allowed_comms.iteritems():
				help_text+= "  %s : %s\n"%(comms, desc)

			return self.api.sendMessage(user.id, help_text) 

	def reply_error(self, user):
		self.api.sendMessage(user.id, "Unknown command")

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

				self.events[ply.event].handle_command(command, *args) #If he is, let the event handle the message
			else:
				#parse command on your own
				self.handle_command(user, command, *args)

	def register_player(self, user):
		new_player = Player(None, None, None) #Create an empty player object
		persistence_controller.add_player(user, new_player) #Add him to Persistence
		uid = util.get_uid()
		registration = RegistrationEvent(self, event_over_callback, uid, user) #Create a registration event
		self.events[uid] = registration #add event to collection of events
		print("Registration event %s created"%(uid))






