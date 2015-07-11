import persistence
from creatures import Player
from bot_events import RegistrationEvent
import uuid
import json
# read apikey from file

persistence_controller = persistence.get_persistence_controller_instance()


def get_dungeon_bot_instance():
	if DungeonBot.instance:
		return DungeonBot.instance

def get_uid():
	return str(uuid.uuid4())[:8]

def event_over_callback(uid):
	event = DungeonBot.events[uid]
	for user in event.users:
		if persistence_controller.is_registered(user):
			ply = persistence_controller.get_ply(user)

			print("registered ply: %s"%(json.dumps(ply.__dict__)))
			ply.event = None # Free all players from event


	del DungeonBot.events[uid] #delete event

class DungeonBot(object):
	instance = None
	events = {}
	last_update_id = None
	api = None
	#set webhook

	def __init__(self):
		instance = self

	def reply_error(self, user):
		self.api.sendMessage(user.id, "Unknown command")

	def start_main_loop(self):
		while True:
			if self.last_update_id:
				updates = self.api.getUpdates(self.last_update_id)
			else:
				updates = self.api.getUpdates()

			for update in updates:
				self.last_update_id = update.update_id+1

				print("Last update id is %d"%(self.last_update_id))
				message = update.message
				print(("%s: %s")%(message.from_user.username, message.text))
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
			if ply.event and self.events[ply.event]: #Check if player is in event
				self.events[ply.event].handle_message(message) #If he is, let the event handle the message
			else:
				self.api.sendMessage(user.id, "Oi mate how 'bout you start dungeon crawling?") #If he is not, invite him to start or join a dungeon crawl


	def register_player(self, user):
		new_player = Player(None, None, None) #Create an empty player object
		persistence_controller.add_player(user, new_player) #Add him to Persistence
		uid = get_uid()
		registration = RegistrationEvent(self, event_over_callback, uid, user) #Create a registration event
		self.events[uid] = registration #add event to collection of events
		print("Registration event %s created"%(uid))






