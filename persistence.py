import logging
class PersistenceController(object):
	players = {}
	instance = None

	def __init__(self):
		instance = self
		
	def is_registered(self, user):
		if user.username in self.players.keys():
			return True
		return False
	
	def add_player(self, user, player):
		self.players[user.username] = player

	def get_ply(self, user):
		#if is_registered(user.username):
		return self.players[user.username]

	@staticmethod
	def get_instance():
		return PersistenceController.instance

def get_persistence_controller_instance():
	if not PersistenceController.instance:
		PersistenceController.instance = PersistenceController()
	return PersistenceController.instance

