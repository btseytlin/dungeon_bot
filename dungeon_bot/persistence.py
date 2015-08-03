#!/usr/bin/env python3
import json
from .creatures import Player
players_file_path = "./data/players.json"
class PersistenceController(object):
	players = {}
	instance = None

	def __init__(self):
		PersistenceController.instance = self
		self.players = self.load_players()
		
	def is_registered(self, user):
		if user.username in self.players.keys():
			return True
		return False
	
	def clear_events(self):
		for uname in self.players:
			self.players[uname].event = None

	def add_player(self, user, player):
		self.players[user.username] = player

	def get_ply(self, user):
		#if is_registered(user.username):
		return self.players[user.username]

	def save_players(self):
		players_to_save = {}
		for uname in list(self.players.keys()):
			players_to_save[uname] = json.dumps(self.players[uname].to_json())

		players_to_save = json.dumps(players_to_save)

		f = open(players_file_path, 'w')
		f.write(players_to_save)

		print("Players saved")

	def load_players(self):
		players_dict = {}
		try:
			with open(players_file_path, 'r') as f:
				players_dict = json.loads(f.read())
				for uname in list(players_dict.keys()):
					players_dict[uname] = Player.de_json(players_dict[uname])
				self.players = players_dict
				print("Players loaded")
		except FileNotFoundError:
			print("No player data found")

		return players_dict

	@staticmethod
	def get_instance():
		if not PersistenceController.instance:
			PersistenceController.instance = PersistenceController()
		return PersistenceController.instance

def get_persistence_controller_instance():
	if not PersistenceController.instance:
		PersistenceController.instance = PersistenceController()
	return PersistenceController.instance

