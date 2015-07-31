from util import *
from enemies import *
import random
class Dungeon(object):
	def __init__(self, name, description, players, rooms = [], current_room = 0, difficulty=None):
		self.uid = get_uid()
		self.name = name
		self.description = description
		self.rooms = rooms		
		self.players = players
		self.current_room = current_room

		if not difficulty:
			self.difficulty = sum([p.level for p in players])/len(self.players)
		else:
			self.difficulty = difficulty
			
		print("Dungeon difficulty = %d"%(self.difficulty))

	@staticmethod
	def new_dungeon(players): #TODO add biomes, randomize dungeon creation
		dungeon_name = "Dungeon of rats #" + str(random.randint(0, 100)) 
		dungeon_description = "A dungeon that only rats inhabit. It's actually a peasant's basement.\nA big basement. With rats."
		dungeon_players = players 
		dungeon = Dungeon(dungeon_name, dungeon_description, dungeon_players)
		dungeon.generate_rooms(1)
		return dungeon

	def generate_rooms(self, amount):
		for i in range(amount+1):
			room_type = random.choice(["combat"])
			room = Room(room_type)
			if room_type == "loot":
				#todo add loot rooms
				pass #retrieve a loot distribution event
			elif room_type == "riddle":
				#todo add riddle rooms
				pass
			elif room_type == "combat":
				combat_enemies = retrieve_enemies_for_difficulty("animal", self.difficulty)
				room.combat_enemies = combat_enemies
			self.rooms.append(room)

class Room(object):
	def __init__(self, room_type, combat_enemies = []):
		self.uid = get_uid()
		self.room_type = room_type
		self.combat_enemies = combat_enemies

	def enter(self):
		pass