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
		if str(user.id) in self.players.keys():
			return True
		return False
	
	def clear_events(self):
		for uid in self.players:
			if self.players[uid].event:
				self.players[uid].event.finish()

	def add_player(self, user, player):
		self.players[str(user.id)] = player

	def get_ply(self, user):
		if self.is_registered(user):
			return self.players[str(user.id)]

	def save_players(self):
		players_to_save = {}
		for uid in list(self.players.keys()):
			if self.players[uid] and hasattr(self.players[uid], "level_up_points"):
				# ply = self.players[uid]
				# print("\nRespecing ply", ply.name)
				# print("Has perks", ply.level_perks)
				# print("---")
				# perks_copy = ply.level_perks.copy()
				# for perk in perks_copy:
				# 	print("Respecing perk", perk)
				# 	ply.level_perks.remove(perk)
				# 	ply.perk_points += 1
				players_to_save[uid] = self.players[uid].to_json()
				

		players_to_save = json.dumps(players_to_save)

		f = open(players_file_path, 'w')
		f.write(players_to_save)

		print("Players saved")

	def load_players(self):
		players_dict = {}
		try:
			with open(players_file_path, 'r') as f:
				players_dict = json.loads(f.read())
				for uid in list(players_dict.keys()):
					ply = Player.de_json(players_dict[uid])
					if ply:
						players_dict[uid] = ply
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

