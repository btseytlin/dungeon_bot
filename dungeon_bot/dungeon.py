from util import *
from enemies import *
import random
class Dungeon(object):
	def __init__(self, name, description, players, enemy_types, rooms = [], current_room = 0, difficulty=None):
		self.uid = get_uid()
		self.name = name
		self.enemy_types = enemy_types
		self.description = description
		self.rooms = rooms		
		self.players = players
		self.current_room = current_room

		if not difficulty:
			self.difficulty = sum([p.level for p in players])/len(self.players) + 100
		else:
			self.difficulty = difficulty
			
		print("Dungeon difficulty = %d"%(self.difficulty))

	@staticmethod
	def new_dungeon(players): #TODO add biomes, randomize dungeon creation
		dungeon_name = random.choice(list(dungeons.keys()))
		dungeon_description = dungeons[dungeon_name]["description"]
		dungeon_enemy_types = dungeons[dungeon_name]["enemy_types"]
		dungeon_players = players 
		dungeon = Dungeon(dungeon_name, dungeon_description, dungeon_players, dungeon_enemy_types)
		dungeon.generate_rooms(random.randint(3, 10))
		return dungeon

	def generate_rooms(self, amount):
		for i in range(amount+1):
			room_type = random.choice(["combat"])
			room = Room(room_type)
			if room_type == "riddle":
				#todo add riddle rooms
				pass
			elif room_type == "combat":
				enemy_type = random.choice(self.enemy_types)
				room.combat_enemies, room.description = retrieve_enemies_for_difficulty(enemy_type, self.difficulty)
			self.rooms.append(room)

class Room(object):
	def __init__(self, room_type, combat_enemies = []):
		self.uid = get_uid()
		self.room_type = room_type
		self.combat_enemies = combat_enemies
		self.description = ""

	def enter(self):
		pass

dungeons = {
	"Crypt of low levels" : {
		"description": "A horrifyingly easy crypt with pussy enemies.", 
		"enemy_types":["animal"]
	}
}