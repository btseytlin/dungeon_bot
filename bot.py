from PersistenceController import PersistenceController
from creatures import Player
from bot_events import RegistrationEvent
# read apikey from file
uid = 0

def event_over_callback(uid):
	event = DungeonBot.events[uid]
	for user in event.users:
		if PersistenceController.is_registered(user):
			ply = PersistenceController.get_ply(user)
			ply.event = None # Free all players from event
	del DungeonBot.events[uid] #delete event

class DungeonBot(object):
	events = {}
	api = None
	#set webhook

	def reply_error(self, user):
		self.sendMessage(user, "Unknown command")

	def start_main_loop(self):
		while True:
			updates = DungeonBot.api.getUpdates()
			for update in updates:
				message = update.message
				self.on_message(message)

	def on_message(self, message):
		user = message.from_user
		
		if not message.text: #if message text is missing or empty its an error
			self.reply_error(user, message)

		#check if player is registered
		if !PersistenceController.is_registered(user.username): 
			self.register_player(user)
		else:
			ply = PersistenceController.get_ply(user)
			if ply.event: #Check if player is in event
				DungeonBot.events[ply.event].handle_message(message) #If he is, let the event handle the message
			else:
				DungeonBot.api.sendMessage(user, "Oi mate how 'bout you start dungeon crawling?") #If he is not, invite him to start or join a dungeon crawl

			
			
			

		#pass message to someone else for actual handling
		print("Message from %s: %s" % (user["first_name"], message["text"]))

	def register_player(self, user):
		new_player = Player(None, None, None) #Create an empty player object
		PersistenceController.add_player(user, new_player) #Add him to Persistence
		registration = RegistrationEvent(event_over_callback, uid, player) #Create a registration event
		uid = uid + 1 #uid should increase so its stays unique
		DungeonBot.events[uid] = registration #add event to collection of events






