class PersistenceController(object):
	players = {}

	def is_registered(self, user):
		if user.username in players.keys():
			return True
		return False
	
	def add_player(self, user, player):
		players[user.username] = player

	def get_ply(self, user):
		#if is_registered(user.username):
		return players[user.username]
	