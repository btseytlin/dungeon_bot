import persistence
import logging
persistence_controller = persistence.get_persistence_controller_instance()


class BotEvent(object):
	def __init__(self, bot, finished_callback, uid, users):
		self.bot = bot
		self.finished_callback = finished_callback
		self.uid = uid
		self.users = users

		for user in users:
			player = persistence_controller.get_ply(user)
			player.event = uid

	def handle_command(self, command, *args):
		print("Base bot event shouldnt handle any messages!")

	def finish(self):
		self.finished_callback(self.uid)

class RegistrationEvent(BotEvent):

	steps = [
		"name",
		"race", 
		"combat_class"
	]

	def __init__(self, bot, finished_callback, uid, user):
		BotEvent.__init__(self, bot, finished_callback, uid, [user])
		self.user = user
		self.current_step = 0
		self.new_player = persistence_controller.get_ply(user)

		logging.debug(self.bot)

		self.bot.api.sendMessage(self.user.id, 'You can restart the registration at any time by sending "restart".')
		self.bot.api.sendMessage(self.user.id, "Let's begin. What is your name?")

	def handle_command(self, command, *args):
		if command == "restart":
			self.current_step == 0
			self.bot.api.sendMessage(self.user.id, "Let's begin. What is your name?")

		if self.current_step == 0:
			self.new_player.name = (command + " " + " ".join([str(arg) for arg in args])).strip().title()
			self.current_step+=1
			self.bot.api.sendMessage(self.user.id, "What is your race?")

		elif self.current_step == 1:
			self.new_player.race = command
			self.bot.api.sendMessage(self.user.id, "What is your class?")
			self.current_step+=1

		elif self.current_step == 2:
			self.new_player.combat_class = command
			self.bot.api.sendMessage(self.user.id, 'Registration complete! Try "examine" to see your stats.')
			
			self.finish()
