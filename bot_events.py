from PersistenceController import PersistenceController

class BotEvent(object):
	def __init__(self, finished_callback, uid, users):
		self.finished_callback = finished_callback
		self.uid = uid
		self.users = users

		for user in users:
			ply = PersistenceController.get_ply(user)
			ply.event = uid

	def handle_message(self, message):
		print("Base bot event shouldnt handle any messages!")

	def finish(self):
		self.finished_callback(uid)

class RegistrationEvent(BotEvent):

	steps = [
		"name",
		"race", 
		"combat_class"
	]

	def __init__(self, finished_callback, uid, user, player):
		BotEvent.__init__(self, finished_callback, uid, [user])
		self.user = user
		self.current_step = 0
		self.new_player = player
		DungeonBot.api.sendMessage(user, "What is your name?")

	def handle_message(self, message):
		if self.current_step == 0:
			self.new_player.name == message.text
			self.current_step+=1
			DungeonBot.api.sendMessage(user, "What is your race?")

		elif self.current_step == 1:
			self.new_player.race == message.text
			DungeonBot.api.sendMessage(user, "What is your class?")
			self.current_step+=1

		elif self.current_step == 2:
			self.new_player.combat_class == message.text
			DungeonBot.api.sendMessage(user, "Registration complete!")
			
			self.finish()
