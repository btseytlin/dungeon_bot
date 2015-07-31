import json
from persistence import PersistenceController
from util import *
from abilities import *
import random
from creatures import *
from items import *
import logging

combat_logger = logging.getLogger('dungeon_bot_combat')
persistence_controller = PersistenceController.get_instance()
class BotEvent(object):
	def __init__(self, finished_callback, users):
		self.finished_callback = finished_callback
		
		self.users = users
		self.uid = get_uid()

		for user in users:
			player = persistence_controller.get_ply(user)
			player.event = self

	def handle_command(self, user, command, *args):
		print("Base bot event shouldnt handle any messages!")

	def add_user(self, user):
		self.users.append(user)
		player = persistence_controller.get_ply(user)
		player.event = self

	def on_player_leave(self, user):
		player = persistence_controller.get_ply(user)
		player.event = None

	def remove_user(self, user):
		for u in self.users:
			if u.username == user.username and u.id == user.id:
				self.users.remove(u)
		self.on_player_leave(user)

	def free_users(self):
		for user in self.users:
			if persistence_controller.is_registered(user):
				self.on_player_leave(user)

	def finish(self):
		self.free_users()
		persistence_controller.save_players()
		return self.finished_callback(self)

class RegistrationEvent(BotEvent):

	steps = [
		"name"
	]

	def __init__(self, finished_callback, user):
		BotEvent.__init__(self, finished_callback, [user])
		self.user = user
		self.current_step = 0
		self.char_points = 3
		self.new_player = persistence_controller.get_ply(user)
		self.greeting_message = 'You can restart the registration at any time by sending "restart".\nLet\'s begin.\nWhat is your name?'

	def handle_command(self, user, command, *args):
		if command == "restart":
			self.current_step = 0
			return("Let's begin. What is your name?")

		if self.current_step == 0:
			self.new_player.name = (command + " " + " ".join([str(arg) for arg in args])).strip().title()
			self.current_step+=1
			msg = "Great. Now let's input your characteristics. Currently they are:\n"
			msg += "".join(["|\t"+str(x)+":" +str(self.new_player.characteristics[x])+"\n" for x in list(self.new_player.characteristics.keys())])
			msg += "Strength affects how much damage you do, how resistant you are to damage.\n"
			msg += "Dexterity affects how fast you act and how accurate you hit.\n"
			msg += "Vitality affects how much health you have.\n"
			msg += "Intelligence affects how likely you are to strike a critial effect, how quickly you level up.\n"
			msg += "Use commands like \"dexterity +\" or \"dex +\" to increase or lower characteristics.\n"
			msg += "Type \"done\" once finished.\n"
			return msg

		elif self.current_step == 1:
			if command in ["dex", "dexterity", "strength", "str", "vitality", "vit", "intelligence", "int"]:
				argument = " ".join(args)
				shortened_to_full = {
					"dex": "dexterity",
					"str": "strength",
					"vit": "vitality",
					"int": "intelligence",
				}
				if not command in ["dexterity", "strength", "vitality", "intelligence"]:
					characteristic = shortened_to_full[command]
				else:
					characteristic = command

				if argument == "+":
					if self.char_points > 0:
						self.new_player.characteristics[characteristic] += 1
						self.char_points -= 1 
						msg = "You have %d points left.\n"%(self.char_points)
						msg += "".join(["|\t"+str(x)+":" +str(self.new_player.characteristics[x])+"\n" for x in list(self.new_player.characteristics.keys())])
						return msg
					else:
						return "You don't have any points left, lower some characteristic to raise %s."%(characteristic)
				elif argument == "-":
					if self.new_player.characteristics[characteristic] > 1:
						self.new_player.characteristics[characteristic] -= 1
						self.char_points += 1 
						msg = "You have %d points left.\n"%(self.char_points)
						msg += "".join(["|\t"+str(x)+":" +str(self.new_player.characteristics[x])+"\n" for x in list(self.new_player.characteristics.keys())])
						return msg
					else:
						return "You can't lower %s any further."%(characteristic)
				else:
					return "Wrong argument, try \"+\" or \"-\"."
			elif command == "done":
				if self.char_points > 0:
					return "You still have unspent points!\nDon't make that mistake, go invest them into something."
				club = get_item_by_name("club")
				self.new_player.inventory = [club]
				self.finish()
				return('Registration complete!\nA club has been added to your inventory, don\'t forget to equip it.\nTry "examine" to see your stats, "inventory" to see your items.\nAlso remember to use "status" and "help" whenever you don\'t know where you are or what to do.')
			else:
				return "Unknown command."
			
			

class InventoryEvent(BotEvent):

	allowed_commands = {
		"examine": "shows your stats and inventory","ex": "shows your stats and inventory","stats": "shows your stats and inventory",
		"list": "lists your inventory","l": "lists your inventory",
		"examine [item]": "shows an item's stats", "ex [item]": "shows an item's stats", 
		"equip [item]": "equips an item","eq [item]": "equips an item",
		"unequip [item]": "equips an item","uneq [item]": "unequips an item",
		"use [item]": "uses an item (such as a potion)", "u [item]": "uses an item (such as a potion)",
		"destroy [item]": "destroys an item","drop [item]": "destroys an item",
		"give [item] [username/playername]": "gives an item to another player",
		"status": "shows where you are and what you are doing",
		"info": "shows help","help": "shows help","h": "shows help",
		"back": "closes inventory","abort": "closes inventory","ab": "closes inventory","b": "closes inventory",
	}

	def __init__(self, finished_callback, user):
		BotEvent.__init__(self, finished_callback, [user])
		self.user = user
		self.player = persistence_controller.get_ply(user)
		self.greeting_message = self.status(user)

	def status(self, user):
		msg = "You are in the inventory screen.\n"
		msg += 'You can use item numbers as arguemnts for commands, for example "equip 1".\n'
		msg += "Your inventory:\n%s\n"%(self.player.examine_inventory())
		msg += "Your equipment:\n%s\n"%(self.player.examine_equipment())
		return msg

	def find_item(self, arg, player, inventory_only = False):
		if not inventory_only:
			if arg in ["primary_weapon", "pweapon", "pw"]:
				if player.primary_weapon:
					return True, player.primary_weapon
				else:
					return False, "Primary weapon not equipped."
			elif arg in ["secondary_weapon", "sweapon", "sw"]:				
				if player.secondary_weapon:
					return True, player.secondary_weapon
				else:
					return False, "Secondary weapon not equipped."
			elif arg in ["armor", "a"]:				
				if player.armor:
					return True, player.armor
				else:
					return False, "Armor not equipped."
			elif arg in ["ring", "r"]:				
				if player.ring:
					return True, player.ring
				else:
					return False, "Ring not equipped."
			elif arg in ["headwear", "h"]:				
				if player.headwear:
					return True, player.headwear
				else:
					return False, "Headwear not equipped."
			elif arg in ["talisamn", "t"]:				
				if player.talisamn:
					return True, player.talisamn
				else:
					return False, "Talisman not equipped."

		if arg.isdigit():
			arg = int(arg)-1
			if int(arg) >= 0 and int(arg) < len(self.player.inventory):
				return True, self.player.inventory[arg]
			return False, "No item under such number in inventory."

		all_items = self.player.inventory.copy()
		if not inventory_only:
			all_items += list(player.equipment.values())

		for i in range(len(all_items)):
			item = all_items[i]
			if item and item.name == arg or arg.isdigit() and i == int(arg):
				return True, item

		error_text = "No such item in your inventory"
		if not inventory_only:
			error_text += "or equipment."
		else:
			error_text += "."
		return False, error_text

	def handle_command(self, user, command, *args):
		if (command in ["help","info","h"]):
			return(print_available_commands(self.allowed_commands))

		elif (command in ["examine","ex","stats","st"]):
			if len(args) == 0:
				desc = self.player.examine_self()+'\n'
				desc += "Equipment:\n"+self.player.examine_equipment()
				desc += "Inventory:\n"+self.player.examine_inventory()
				return desc
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player)
				if found:
					msg = item.examine_self()
					return(msg)
				else:
					return item
		elif (command in ["list","l"]):
			desc = "\n"+self.player.examine_equipment()
			desc += self.player.examine_inventory()
			return desc

		elif (command in ["equip", "eq"]):
			if len(args) == 0:
				return("Specify an item to equip.")
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player, True)
				if found:
					msg = self.player.equip(item)
					return(msg)
				else:
					return item

		elif (command in ["unequip", "uneq"]):
			if len(args) == 0:
				return("Specify an item to unequip.")
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player)
				if found:
					msg = self.player.unequip(item)
					return(msg)
				else:
					return item

		elif (command in["use", "u"]):
			if len(args) == 0:
				return("Specify an item to use.")
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player)
				if found:
					msg = self.player.use(item)
					return(msg)
				else:
					return item

		elif (command in ['destroy', 'drop']):
			if len(args) == 0:
				return("Specify an item to destroy.")
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player)
				if found:
					msg = self.player.destroy(item)
					return(msg)
				else:
					return item
		elif (command in ["status"]):
			msg = self.status(user)
			return msg

		elif (command == "give"):
			return "WIP FEATURE"

		elif (command in ["back", "abort", "ab", "b"]):
			self.finish()
			return "Closed inventory"

		return 'Unknown command, try "help"'

class DungeonLobbyEvent(BotEvent):
	allowed_commands = {
		"start": "starts the dungeon crawl", "st": "starts the dungeon crawl",
		"info": "shows help","help": "shows help","h": "shows help",
		"back": "leaves lobby","abort": "leaves lobby","ab": "leaves lobby","b": "leaves lobby", "leave": "leaves lobby",
		"status": "shows where you are and what you are doing",
	}

	def __init__(self, finished_callback, total_users):
		BotEvent.__init__(self, finished_callback, [])
		self.greeting_message = 'A dungeon crawl will start once there are enough players (%d). Use "abort" to leave, "start" to begin.'%(total_users)
		self.status_message = 'There are %d out of %d players.'
		self.total_users = total_users

	def status(self, user):
		msg = 'You are in lobby %s.\nThere are %d out of %d players in the lobby.\n'%(self.uid, len(self.users), self.total_users)
		msg += 'Players in lobby:%s.\n'%(", ".join([persistence_controller.get_ply(user).name+"(@"+persistence_controller.get_ply(user).username+")" for user in self.users]))
		if self.is_enough_players():
			msg += 'Ready to start the dungeon crawl! Input "start" to begin.\n'
		else:
			msg += 'Not enough players to start the dungeon crawl yet.\n'
		return msg
	
	def handle_command(self, user, command, *args):
		if (command in ["help","info","h"]):
			return(print_available_commands(self.allowed_commands))
		elif (command in ["back","abort","b", "leave", "ab"]):
			return(self.remove_user(user))
		elif (command in ["status"]):
			msg = self.status(user)
			return msg
		elif (command in ["start"]):
			return(self.start_crawl())
		return 'Unknown command, try "help".'

	def is_enough_players(self):
		if len(self.users) < self.total_users:
			return False	
		return True

	def add_user(self, user):
		super(DungeonLobbyEvent, self).add_user(user)
		broadcast = []
		msg = "User %s joined the lobby"%(user.username)

		msg_enough = 'The lobby has enough players to start, use "start" command to proceed.\n'
		msg_not_enough = 'The lobby needs %d more players to start.\n'%( self.total_users - len(self.users) )

		broadcast.append([user, "You were added to lobby %s.\n"%(self.uid)])
		broadcast.append([user, self.greeting_message])
		for u in self.users:
			if u != user:
				broadcast.append([u, msg])
			if self.is_enough_players():
				broadcast.append([u, msg_enough])
			else:
				broadcast.append([u, msg_not_enough])

		return broadcast

	def remove_user(self, user):
		super(DungeonLobbyEvent, self).remove_user(user)
		broadcast = []
		msg_enough = 'The lobby has enough players to start, use "start" command to proceed.\n'
		msg_not_enough = 'The lobby needs %d more players to start.\n'%( self.total_users - len(self.users) )
		msg = "User %s left the lobby.\n"%(user.username)
		broadcast.append([user, "You were removed from lobby %s.\n"%(self.uid)])
		for u in self.users:
			if u != user:
				broadcast.append([u, msg])
				if self.is_enough_players():
					broadcast.append([u, msg_enough])
				else:
					broadcast.append([u, msg_not_enough])

		if len(self.users) == 0:
			self.finish()

		return broadcast

	def move_players_to_dungeon(self, dungeon_event):
		for user in self.users:
			ply = persistence_controller.get_ply(user)
			ply.event = dungeon_event

	def start_crawl(self):
		return self.finished_callback(self)

class DungeonCrawlEvent(BotEvent):
	def __init__(self, finished_callback, users, dungeon):
		BotEvent.__init__(self, finished_callback, users)
		self.greeting_message = 'You are entering %s.\n%s\n'%(dungeon.name, dungeon.description)
		self.dungeon = dungeon
		self.non_combat_events = {} # key: user.username, value: event.uid
		self.combat_event = None

	allowed_commands = {
		"advance": "move to next room", "adv": "move to next room",
		"inventory": "shows your inventory", "inv": "shows your inventory",
		"examine": "shows your stats", "ex": "shows your stats", "stats": "shows your stats","st": "shows your stats",
		"examine [character]": "shows a chracter's stats", "ex [character]": "shows a chracter's stats", "stats [character]": "shows a chracter's stats","st [character]": "shows a chracter's stats",
		"info": "shows help","help": "shows help","h": "shows help",
		"back": "leaves dungeon crawl","abort": "leaves dungeon crawl","ab": "leaves dungeon crawl","b": "leaves dungeon crawl", "leave": "leaves dungeon crawl",
		"say [message]": "sends a message to your fellow dungeon crawlers", "s [message]": "sends a message to your fellow dungeon crawlers", 
		"levelup": "opens the level up dialogue", "lvl": "opens the level up dialogue", 
		"status": "shows where you are and what you are doing",
	}

	def status(self, user=None):
		msg = 'You are in room number %d of %s.'%(self.dungeon.current_room, self.dungeon.name)
		return msg

	def check_if_can_advance(self):
		if len(list(self.non_combat_events.keys())) > 0:
			return False
		return True

	def remove_user(self, user):
		super(DungeonCrawlEvent, self).remove_user(user)
		broadcast = []
		msg = 'Pathetic looser %s ran away from the dungeon like a pussy he is'%(persistence_controller.get_ply(user))

		broadcast.append([user, "You were removed from lobby %s"%(self.uid)])
		for u in self.users:
			if u != user:
				broadcast.append([u, msg])

		if len(self.users) == 0:
			self.finish()

		return broadcast

	def start_combat(self, players, enemies):
		def combat_over_callback(event):
			alive_player = False
			for player in players:
				player.event = self # Free all players from event
				if not player.dead:
					alive_player = True
			if not alive_player:
				return "\nThe players perished in the dungeon.\n" + self.finish()
			return "\nThe players have defeated the pesky enemies and are ready to advance further.\n"

		combat = CombatEvent(combat_over_callback, players, self.users, enemies) #Create an inventory event
		self.combat_event = combat
		combat_logger.debug("Combat event  %s created within dungeon %s."%(combat.uid, self.uid))

		broadcast = []

		for u in self.users:
			broadcast.append([u, combat.greeting_message])
		return(broadcast)

	def advance_room(self):
		if not self.check_if_can_advance():
			msg = "Can't advance, someone is inventory or leveling up"
			broadcast = [(u, msg) for u in self.users]
			return broadcast

		self.dungeon.current_room += 1

		if self.dungeon.current_room > len(self.dungeon.rooms)-1:
			self.finish()
			broadcast = []
			for u in self.users:
				broadcast.append([u, "Dungeon completed"])
			return broadcast

		room = self.dungeon.rooms[self.dungeon.current_room]
		if room.room_type == "combat":
			enemies = room.combat_enemies
			description = room.description

			broadcast = []
			for u in self.users:
				broadcast.append([u, description])
			return broadcast + self.start_combat(self.dungeon.players, enemies)
		return "Room type not done yet."


	def open_levelup(self, user):
		pass

	def open_inventory(self, user):
		def inv_over_callback(event):
			player = persistence_controller.get_ply(user)
			player.event = self # Free all players from event

			for uname in list(self.non_combat_events.keys()):
				if self.non_combat_events[uname] == event:
					del self.non_combat_events[uname]
					break

		inv = InventoryEvent(inv_over_callback, user) #Create an inventory event
		self.non_combat_events[user.username] = inv
		persistence_controller.get_ply(user).event = inv
		combat_logger.debug("Inventory event  %s created within dungeon %s."%(inv.uid, self.uid))

		broadcast = []
		msg = '%s is rummaging in his inventory.'%(persistence_controller.get_ply(user).username.title())

		broadcast.append([user, inv.greeting_message])
		for u in self.users:
			if u.username != user.username:
				broadcast.append([u, msg])
		return(broadcast)

	def handle_command(self, user, command, *args):
		#if user.username in list(self.non_combat_events.keys()):
		#	return self.non_combat_events[user.username].handle_command(user, command, *args)
		#elif self.combat_event:
		#	return self.combat_event.handle_command(user, command, *args)
		if (command in ["help","info","h"]):
			return(print_available_commands(self.allowed_commands))
		elif (command in ["back","abort","b", "leave", "ab"]):
			return(self.remove_user(user))
		elif (command in ["advance","adv"]):
			return(self.advance_room())
		elif (command in ["inventory","inv"]):
			return(self.open_inventory(user))
		elif (command in ["levelup","lvl"]):
			return(self.open_levelup(user))
		elif (command in ["status"]):
			msg = self.status(user)
			return msg
		elif (command in ["examine", "stats", "ex", "st"]):
			if len(args) == 0:
				return  (persistence_controller.get_ply(user)).examine_self()
			if len(args) > 0:
				argument = " ".join(args)
				if argument=="self" or argument == user.username or argument == persistence_controller.get_ply(user).name:
					return (persistence_controller.get_ply(user).examine_self())
				else:
					target_user = None
					for u in self.users:
						target_ply = persistence_controller.get_ply(u)
						if u.username == argument or persistence_controller.get_ply(u).name == argument:
							target_user = u
							return (target_ply.examine_self())
					return "No such player or user in that dungeon"
		return 'Unknown command, try "help"'

class CombatEvent(BotEvent):
	def __init__(self, finished_callback, players, users, enemies):
		BotEvent.__init__(self, finished_callback, users)
		self.players = players
		self.enemies = enemies
		self.turn_qeue = self.update_turn_qeue()

		for creature in self.turn_qeue:
			creature.on_combat_start()

		self.turn = 0
		self.round = 0

		

		self.user_abilities = { #  {user.username:  {ability.name: ability}}

		}

		self.users_to_players =  {

		}
		for user in self.users:
			for ply in self.players:
				if ply.username == user.username:
					self.users_to_players[user.username] = ply

			if not user.username in list(self.user_abilities.keys()):
				self.user_abilities[user.username] = {}

			ply = self.users_to_players[user.username]
			for ability in ply.abilities:
				self.user_abilities[user.username][ability.name] = ability


		combat_logger.info("Started combat %s vs %s"%(", ".join([p.name + "("+p.username+")" for p in players]), ", ".join([e.name for e in enemies])))

		self.greeting_message = 'Combat starts!\n %s vs %s.\n'%(", ".join([p.name for p in players]), ", ".join([e.name for e in enemies]))
		self.greeting_message += self.next_round()

		#if isinstance(self.turn_qeue[self.turn], Enemy):
		#	self.greeting_message += self.ai_turn()

	def status(self, user):
		msg = 'You are fighting %s.\n'%(", ".join([enemy.name for enemy in self.enemies]))
		msg += 'The turn qeue:%s\n'%(self.get_printable_turn_qeue())
		msg += 'You can use creature numbers as arguemnts for commands, for example "smash 1".\n'
		msg += 'You have %d energy and %d health.\n'%(self.users_to_players[user.username].energy, self.users_to_players[user.username].health)
		msg += "It's %s's turn.\n"%(self.turn_qeue[self.turn].name.title())
		return msg

	def next_round(self):
		self.round += 1
		self.turn = 0
		msg = "".join([c.on_round() for c in self.turn_qeue])
		msg += "Round %d.\n"%(self.round)
		self.turn_qeue = self.update_turn_qeue()
		msg += self.get_printable_turn_qeue()
		combat_logger.info("%s"%(msg))
		msg += self.this_turn()
		return msg

	def get_printable_turn_qeue(self):
		return ", ".join(["["+str(i)+"]"+self.turn_qeue[i].name for i in range(len(self.turn_qeue))])+"\n"
	
	def check_winning_conditions(self):
		alive_enemy = False
		alive_player = False
		for c in self.turn_qeue:
			if not c.dead:
				if isinstance(c,Player):
					alive_player = True
				elif isinstance(c, Enemy):
					alive_enemy = True

		if alive_enemy and not alive_player:
			self.winner = "enemies"
			desc = "Players have been defeated!\n"
			return True, desc
		elif alive_player and not alive_enemy:
			self.winner = "players"
			desc = "Players won the battle!\n"
			return True, desc
		elif not alive_player and not alive_enemy:
			self.winner = "the zone" #whatever the hell happened that everyone died
			desc = "Everyone died, thus the players lost. How did you manage it anyway?"
			return True, desc
		return False, ""

	def this_turn(self):
		msg = ""
		if (self.turn_qeue[self.turn].dead):
			return self.next_turn()

		if isinstance(self.turn_qeue[self.turn], Enemy):
			msg += self.ai_turn()
			return msg + self.next_turn()
		else:
			return "It's %s's turn.\n"%(self.turn_qeue[self.turn].name)

	def next_turn(self):
		msg = ""

		self.turn += 1
		if self.turn > len(self.turn_qeue)-1:
			return msg + self.next_round()

		fight_ended, desc = self.check_winning_conditions()
		if fight_ended:
			msg += desc
			return msg + self.finish()

		if (self.turn_qeue[self.turn].dead):
			return self.next_turn()

		for creature in self.turn_qeue:
			msg += creature.on_turn()

		return msg + self.this_turn()

	def update_turn_qeue(self):
		all_creatures = self.players + self.enemies
		for c in all_creatures:
			if c.dead:
				all_creatures.remove(c)
		random.shuffle(all_creatures)
		qeue = sorted(all_creatures, key=lambda x: x.characteristics["dexterity"], reverse=True)
		combat_logger.info("Combat qeue:\n"+", ".join(["["+str(i)+"]"+qeue[i].name for i in range(len(qeue))]))
		return qeue

	def ai_turn(self):
		use_infos = self.turn_qeue[self.turn].act(self.turn_qeue)
		combat_logger.info("   AI(%s) actions:"%(self.turn_qeue[self.turn].name))
		msg = ""
		for use_info in use_infos:
			combat_logger.info("Ability use info:\n---\n%s"%(str(use_info)))
			msg += use_info.description
		#msg += self.next_turn()
		return msg

	allowed_commands = {
		"examine": "shows your stats","ex": "shows your stats","stats": "shows your stats",
		"examine [creature]": "shows a creature's stats", "ex [creature]": "shows a creature's stats", 
		"info": "shows help","help": "shows help","h": "shows help",
		"status": "shows where you are and what you are doing",
		"turn": "ends turn", "t": "ends turn",
	}

	def handle_combat_command(self, user, command, *args):
		combat_logger.info("Command from user %s: %s %s"%(user.username, command, " ".join(args)))
		if self.turn_qeue[self.turn].username == user.username: #current turn is of player who sent command
			if command in list(self.user_abilities[user.username].keys()):
				ability = self.user_abilities[user.username][command]
				ability_class = self.user_abilities[user.username][command].__class__
				granted_by = ability.granted_by
				argument = " ".join(args)
				target = None
				if len(argument) > 0:
					for i in range(len(self.turn_qeue)):
						t = self.turn_qeue[i]
						if t.name == argument or argument.isdigit() and int(argument) == i:
							target = t

					can_use, cant_use_msg = ability_class.can_use( self.users_to_players[user.username], target )
					if can_use:
						use_info = ability_class.use( self.users_to_players[user.username], target, granted_by )
						combat_logger.info("Ability use info:\n---\n%s"%(str(use_info)))
						msg = use_info.description 
						broadcast = []
						for u in self.users:
							broadcast.append([u, msg])
						return broadcast

					else:
						return cant_use_msg

					return "No such target in turn qeue"
				else:
					return "Specify your target"

			return "No such ability!"
		else:
			return "It's not your turn!"


	def handle_command(self, user, command, *args):
		if (command in ["help","info","h"]):
			help_text = print_available_commands(self.allowed_commands)
			help_text += "\n" + print_combat_abilities(self.user_abilities[user.username])
			return help_text
		elif (command in ["examine", "stats", "ex", "st"]):
			if len(args) == 0:
				return  (self.users_to_players[user.username]).examine_self()
			if len(args) > 0:
				argument = " ".join(args)
				if argument=="self" or argument == user.username or argument == self.users_to_players[user.username].name:
					return (self.users_to_players[user.username].examine_self())
				elif argument.isdigit():
					if int(argument) < len(self.turn_qeue):
						return self.turn_qeue[int(argument)].examine_self()
				else:
					for u in self.users:
						target_ply = persistence_controller.get_ply(u)
						if u.username == argument or target_ply.name == argument:
							return target_ply.examine_self()

					for enemy in self.enemies:
						if enemy.name == argument:
							return enemy.examine_self()

					for key in list(self.user_abilities[user.username].keys()):
						if key == argument:
							return self.user_abilities[user.username][key].examine_self(self.user_abilities[user.username][key])

				return "No such player, user, enemy or ability."

		elif (command in ["turn", "t"]):
			#broadcast new turn 
			msg = self.next_turn()
			broadcast = []
			for u in self.users:
				broadcast.append([u, msg])
			return broadcast

		elif (command in ["status"]):
			msg = self.status(user)
			return msg

		else:
			if command in list(self.user_abilities[user.username].keys()): #is it a combat ability?
				return self.handle_combat_command(user, command, *args)
			return "Unknown command, try help."
	
	def finish(self):
		msg = ""
		for creature in self.turn_qeue:
			msg += creature.on_combat_over()

		msg += super(CombatEvent, self).finish()

		return msg


