#!/usr/bin/env python3
import json
import logging
import random
import datetime
from . import persistence
from . import util
from . import items
from . import creatures
from . import abilities
from . import level_perks

from .persistence import PersistenceController
from .util import *
from .abilities import *
from .creatures import *
from .items import *
from .level_perks import *


combat_logger = logging.getLogger('dungeon_bot_combat')
logger = logging.getLogger('dungeon_bot')
persistence_controller = PersistenceController.get_instance()
class BotEvent(object):
	def __init__(self, finished_callback, users, players = None):
		self.finished_callback = finished_callback
		self.finished = False
		self.users = users
		self.uid = get_uid()

		self.last_activity = datetime.datetime.now()
		if not players:
			self.players = []
			for user in users:
				player = persistence_controller.get_ply(user)
				player.event = self
				self.players.append(player)
		else:
			self.players = players
			for player in players:
				player.event = self

	def handle_command(self, user, command, *args):
		self.last_activity = datetime.datetime.now()
		return ""

	def add_user(self, user):
		self.users.append(user)
		player = persistence_controller.get_ply(user)
		player.event = self

	def on_player_leave(self, user):
		player = persistence_controller.get_ply(user)
		player.event = None

	def remove_user(self, user):
		for u in self.users:
			if u.id == user.id and u.id == user.id:
				self.users.remove(u)
		self.on_player_leave(user)

	def free_users(self):
		for user in self.users:
			if persistence_controller.is_registered(user):
				self.on_player_leave(user)

	def finish(self):
		self.finished = True
		self.free_users()
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

	def format_characteristics(self, chars):
		characteristics = []
		characteristics.append("|\t"+"Strength"+":" +str(chars["strength"]) +"\n")
		characteristics.append("|\t"+"Dexterity"+":" +str(chars["dexterity"]) +"\n")
		characteristics.append("|\t"+"Vitality"+":" +str(chars["vitality"]) +"\n")
		characteristics.append("|\t"+"Intelligence"+":" +str(chars["intelligence"]) +"\n")
		return ''.join(characteristics)

	def handle_command(self, user, command, *args):
		super(RegistrationEvent, self).handle_command(user, command, *args)
		if command == "restart":
			self.current_step = 0
			return("Let's begin. What is your name?")

		if self.current_step == 0:
			self.new_player.name = (command + " " + " ".join([str(arg) for arg in args])).strip().title()
			self.current_step+=1
			msg = "Great. Now let's input your characteristics. Currently they are:\n"
			msg += self.format_characteristics(self.new_player.base_characteristics)
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
						self.new_player.base_characteristics[characteristic] += 1
						self.char_points -= 1 
						msg = "You have %d points left.\n"%(self.char_points)
						msg += self.format_characteristics(self.new_player.base_characteristics)
						return msg
					else:
						return "You don't have any points left, lower some characteristic to raise %s."%(characteristic)
				elif argument == "-":
					if self.new_player.base_characteristics[characteristic] > 1:
						self.new_player.base_characteristics[characteristic] -= 1
						self.char_points += 1 
						msg = "You have %d points left.\n"%(self.char_points)
						msg += self.format_characteristics(self.new_player.base_characteristics)
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
				self.new_player.refresh_derived()
				self.finish()
				return('Registration complete!\nA club has been added to your inventory, don\'t forget to equip it.\nTry "examine" to see your stats, "inventory" to see your items.\nAlso remember to use "status" and "help" whenever you don\'t know where you are or what to do.')
			else:
				return "Unknown command."
			
class LevelUpEvent(BotEvent):
	def __init__(self, finished_callback, user):
		BotEvent.__init__(self, finished_callback, [user])
		self.user = user
		self.player = persistence_controller.get_ply(user)
		self.current_step = 0
		self.perk_step_msg = ""

		self.greeting_message = "In this dialogue you can level up your character.\nYou get a perk every 3 turns and a characteristic point every 5 turns.\nYou can save points for later by typing 'done'.\n"

		if self.player.perk_points > 0:
			self.perk_step_msg = "Choose a perk by typing it's number:\n"
			self.available_perks = [level_perks_listing[key] for key in level_perks_listing if self.player.fits_perk_requirements(level_perks_listing[key].requirements)]
			self.perk_step_msg += "\n".join([str(i+1) + ". " +self.available_perks[i].name + "-" + self.available_perks[i].description for i in range(len(self.available_perks)) ])

		if self.player.level_up_points <= 0:
			if self.player.perk_points > 0:
				self.current_step = 1
				self.greeting_message = 'You can choose %d new perks.\n'%(self.player.perk_points)
				self.greeting_message += self.perk_step_msg
			else:
				self.greeting_message = "You don't have any perk points or characteristic points to spend."
				return self.finish() 
		else:
			self.greeting_message = 'You have %d characteristics points.\nLet\'s begin.\n'%(self.player.level_up_points)
			self.greeting_message += "Currently your characteristics are:\n"
			self.greeting_message += "You can save points for later by using 'done'.\n"
			self.greeting_message += self.format_characteristics(self.player.base_characteristics)
			self.greeting_message += "You can raise your characteristics with commands like \"dex +\", but you can't lower them.\n.\n"



	def format_characteristics(self, chars):
		characteristics = []
		characteristics.append("|\t"+"Strength"+":" +str(chars["strength"]) +"\n")
		characteristics.append("|\t"+"Dexterity"+":" +str(chars["dexterity"]) +"\n")
		characteristics.append("|\t"+"Vitality"+":" +str(chars["vitality"]) +"\n")
		characteristics.append("|\t"+"Intelligence"+":" +str(chars["intelligence"]) +"\n")
		return ''.join(characteristics)

	def handle_command(self, user, command, *args):
		super(LevelUpEvent, self).handle_command(user, command, *args)
		if command == "done":
			return "Done leveling up." + (self.finish() or "")

		if self.current_step == 0:
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
					if self.player.level_up_points > 0:
						self.player.base_characteristics[characteristic] += 1
						self.player.level_up_points -= 1 
						
						msg = self.format_characteristics(self.player.base_characteristics)

						if self.player.level_up_points <= 0:
							msg += "You have no points left to spend.\n"
							self.current_step += 1
							if self.player.perk_points < 0:
								msg += "Done leveling up.\n"
								return msg + self.finish()
							else:
								if len(self.available_perks) <= 0:
									msg += "No perks available."
									msg += "Done leveling up.\n"
									return msg + self.finish()
								else:
									msg += self.perk_step_msg
							return msg
						msg = "You have %d points left.\n"%(self.player.level_up_points)
						return msg
				else:
					return "Wrong argument, try only \"+\" is allowed."
		elif self.current_step == 1:
			if command.isdigit():
				if int(command) > 0 and int(command) <= len(self.available_perks):
					perk = self.available_perks[int(command)-1]
					self.player.level_perks.append(perk(self.player))
					msg = "Added perk %s.\n"%(perk.name)
					self.player.perk_points -= 1
					if self.player.perk_points <= 0 or len(self.available_perks) <= 0:
						msg += "Done leveling up.\n"
						return msg + self.finish()
					msg = "You still have %d perk points to spend.\n"%(self.player.perk_points)
				else:
					return "No perk under such number."
			else:
				return "Input a number!"

class InventoryEvent(BotEvent):

	allowed_commands = {
		"examine": "shows your stats and inventory","ex": "shows your stats and inventory","stats": "shows your stats and inventory",
		"list": "lists your inventory","l": "lists your inventory",
		"examine [item]": "shows an item's stats", "ex [item]": "shows an item's stats", 
		"equip [item]": "equips an item","eq [item]": "equips an item",
		"unequip [item]": "equips an item","uneq [item]": "unequips an item",
		"use [item]": "uses an item (such as a potion)", "u [item]": "uses an item (such as a potion)",
		"destroy [item]": "destroys an item","drop [item]": "destroys an item",
		"give [item] [userid/playername]": "gives an item to another player",
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
		super(InventoryEvent, self).handle_command(user, command, *args)
		if (command in ["help","info","h"]):
			return(print_available_commands(self.allowed_commands))

		elif (command in ["examine","ex","stats","st"]):
			if len(args) == 0:
				desc = self.player.examine_self()+'\n'
				#desc += "Equipment:\n"+self.player.examine_equipment()
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
		"say [message]": "sends a message to your fellow dungeon crawlers", "s [message]": "sends a message to your fellow dungeon crawlers", 

	}

	def __init__(self, finished_callback, total_users):
		BotEvent.__init__(self, finished_callback, [])
		self.greeting_message = 'A dungeon crawl will start once there are enough players (%d). Use "abort" to leave, "start" to begin.'%(total_users)
		self.status_message = 'There are %d out of %d players.'
		self.total_users = total_users

	def status(self, user):
		msg = 'You are in lobby %s.\nThere are %d out of %d players in the lobby.\n'%(self.uid, len(self.users), self.total_users)
		msg += 'Players in lobby:%s.\n'%(", ".join([persistence_controller.get_ply(user).name+"(@"+persistence_controller.get_ply(user).userid+")" for user in self.users]))
		if self.is_enough_players():
			msg += 'Ready to start the dungeon crawl! Input "start" to begin.\n'
		else:
			msg += 'Not enough players to start the dungeon crawl yet.\n'
		return msg
	
	def handle_command(self, user, command, *args):
		super(DungeonLobbyEvent, self).handle_command(user, command, *args)
		if (command in ["help","info","h"]):
			return(print_available_commands(self.allowed_commands))
		elif (command in ["back","abort","b", "leave", "ab"]):
			return(self.remove_user(user))
		elif (command in ["status"]):
			msg = self.status(user)
			return msg
		elif (command in ["say", "s"]):
			if len(args)>0:
				msg = " ".join(args)
				broadcast = []
				broadcast.append([user, "You said:"+msg])
				for u in self.users:
					if user.id != u.id:
						broadcast.append([u, "%s said:%s"%(user.id.title(), msg)])
				return broadcast
			return "Specify what you want to say."
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
		msg = "User %s joined the lobby"%(user.id)

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
		msg = "User %s left the lobby.\n"%(user.id)
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
		self.non_combat_events = {} # key: user.id, value: event.uid
		self.combat_event = None

	allowed_commands = {
		"advance": "move to next room", "adv": "move to next room",
		"inventory": "shows your inventory", "inv": "shows your inventory",
		"examine": "shows your stats", "ex": "shows your stats", "stats": "shows your stats","st": "shows your stats",
		"examine [character]": "shows a chracter's stats", "ex [character]": "shows a chracter's stats", "stats [character]": "shows a chracter's stats","st [character]": "shows a chracter's stats",
		"info": "shows help","help": "shows help","h": "shows help",
		"back": "leaves dungeon crawl","abort": "leaves dungeon crawl","ab": "leaves dungeon crawl","b": "leaves dungeon crawl", "leave": "leaves dungeon crawl",
		"say [message]": "sends a message to your fellow dungeon crawlers", "s [message]": "sends a message to your fellow dungeon crawlers", 
		"level up": "opens the level up dialogue", "lvl": "opens the level up dialogue", 
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
		if self.dungeon:
			self.dungeon.players.remove(persistence_controller.get_ply(user))
		super(DungeonCrawlEvent, self).remove_user(user)
		broadcast = []
		msg = 'Pathetic looser %s ran away from the dungeon like a pussy he is.'%(user.id)

		broadcast.append([user, "You were removed from lobby %s."%(self.uid)])
		for u in self.users:
			if u != user:
				broadcast.append([u, msg])

		if len(self.users) == 0:
			self.finish()

		return broadcast

	def start_combat(self, players, enemies):
		def combat_over_callback(event):
			persistence_controller.save_players()
			alive_player = False
			for player in players:
				player.event = self # Free all players from event
				if not player.dead:
					alive_player = True
			if not alive_player:
				return "\nThe players perished in the dungeon.\n" +self.finish() 
			return "\nThe players have defeated the enemies and are ready to advance further.\n"

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


	def open_level_up(self, user):
		if persistence_controller.get_ply(user).level_up_points > 0 or persistence_controller.get_ply(user).perk_points >0 :

			def lvl_over_callback(event):
				persistence_controller.save_players()
				player = persistence_controller.get_ply(user)
				player.event = self # Free all players from event
				for uname in list(self.non_combat_events.keys()):
					if self.non_combat_events[uname] == event:
						del self.non_combat_events[uname]

			level_up = LevelUpEvent(lvl_over_callback, user)
			self.non_combat_events[user.id] = level_up
			persistence_controller.get_ply(user).event = level_up
			logger.debug("Levelup event %s created within dungeon %s."%(level_up.uid, self.uid))

			broadcast = []
			msg = '%s is leveling up.'%(persistence_controller.get_ply(user).userid.title())

			broadcast.append([user, level_up.greeting_message])
			for u in self.users:
				if u.id != user.id:
					broadcast.append([u, msg])
			return(broadcast)
		return "You don't have any perk points or characteristic points to spend."



	def open_inventory(self, user):
		def inv_over_callback(event):
			persistence_controller.save_players()
			player = persistence_controller.get_ply(user)
			player.event = self # Free all players from event

			for uname in list(self.non_combat_events.keys()):
				if self.non_combat_events[uname] == event:
					del self.non_combat_events[uname]
					break

		inv = InventoryEvent(inv_over_callback, user) #Create an inventory event
		self.non_combat_events[user.id] = inv
		persistence_controller.get_ply(user).event = inv
		combat_logger.debug("Inventory event  %s created within dungeon %s."%(inv.uid, self.uid))

		broadcast = []
		msg = '%s is rummaging in his inventory.'%(user.id.title())

		broadcast.append([user, inv.greeting_message])
		for u in self.users:
			if u.id != user.id:
				broadcast.append([u, msg])
		return(broadcast)

	def handle_command(self, user, command, *args):
		super(DungeonCrawlEvent, self).handle_command(user, command, *args)
		#if user.id in list(self.non_combat_events.keys()):
		#	return self.non_combat_events[user.id].handle_command(user, command, *args)
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
			return(self.open_level_up(user))
		elif (command in ["say", "s"]):
			if len(args)>0:
				msg = " ".join(args)
				broadcast = []
				broadcast.append([user, "You said:"+msg])
				for u in self.users:
					if user.id != u.id:
						broadcast.append([u, "%s said:%s"%(user.id.title(), msg)])
				return broadcast
			return "Specify what you want to say."
		elif (command in ["status"]):
			msg = self.status(user)
			return msg
		elif (command in ["examine", "stats", "ex", "st"]):
			if len(args) == 0:
				return  (persistence_controller.get_ply(user)).examine_self()
			if len(args) > 0:
				argument = " ".join(args)
				if argument=="self" or argument == user.id or argument == persistence_controller.get_ply(user).name:
					return (persistence_controller.get_ply(user).examine_self())
				else:
					target_user = None
					for u in self.users:
						target_ply = persistence_controller.get_ply(u)
						if u.id == argument or persistence_controller.get_ply(u).name == argument:
							target_user = u
							return (target_ply.examine_self())
					return "No such player or user in that dungeon"
		return 'Unknown command, try "help"'

	def finish(self):
		for key in list(self.non_combat_events.keys()):
			self.non_combat_events[key].finish()
		if self.combat_event:
			if not self.combat_event.finished:
				self.combat_event.finish()
		return super(DungeonCrawlEvent, self).finish() or ""

class CombatEvent(BotEvent):
	def __init__(self, finished_callback, players, users, enemies):
		BotEvent.__init__(self, finished_callback, users, players)
		self.players = players
		self.enemies = enemies
		self.turn_qeue = []
		for creature in self.turn_qeue:
			creature.on_combat_start()

		self.turn = 0
		self.round = 0

		self.abilities_used = []

		self.user_abilities = { #  {user.id:  {ability.name: ability}}

		}

		self.users_to_players =  {

		}
		for user in self.users:
			for ply in self.players:
				if ply.userid == user.id:
					self.users_to_players[user.id] = ply

			if not user.id in list(self.user_abilities.keys()):
				self.user_abilities[user.id] = {}

			ply = self.users_to_players[user.id]
			for ability in ply.abilities:
				self.user_abilities[user.id][ability.name] = ability

		combat_logger.info("Started combat %s vs %s"%(", ".join([p.name + "("+p.userid+")" for p in players]), ", ".join([e.name for e in enemies])))

		self.greeting_message = 'Combat starts!\n %s vs %s.\n'%(", ".join([p.name for p in players]), ", ".join([e.name for e in enemies]))
		self.greeting_message += self.next_round()

		#if isinstance(self.turn_qeue[self.turn], Enemy):
		#	self.greeting_message += self.ai_turn()

	def status(self, user):
		msg = 'You are fighting %s.\n'%(", ".join([enemy.name for enemy in self.enemies]))
		msg += 'The turn qeue:%s\n'%(self.get_printable_turn_qeue())
		msg += 'You can use creature numbers as arguemnts for commands, for example "smash 1".\n'
		msg += 'You have %d energy and %d health.\n'%(self.users_to_players[user.id].energy, self.users_to_players[user.id].health)
		msg += "It's %s's turn.\n"%(self.turn_qeue[self.turn].name.title())
		return msg

	def next_round(self):
		self.round += 1
		self.turn = 0
		msg = "".join([c.on_round() for c in self.turn_qeue if not c.dead])
		msg += "Round %d.\n"%(self.round)
		self.turn_qeue = self.update_turn_qeue()
		msg += self.get_printable_turn_qeue()
		combat_logger.info("%s"%(msg))
		msg += self.this_turn()
		return msg

	def get_printable_turn_qeue(self):
		return ", ".join([str(i)+"."+self.turn_qeue[i].short_desc for i in range(len(self.turn_qeue))])+"\n"
	
	def check_winning_conditions(self):
		alive_enemy = False
		alive_player = False
		all_creatures = self.players + self.enemies
		for c in all_creatures:
			if not c.dead:
				#print("%s not dead yet"%(c.name) )
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
			self.winner = "enemies" #whatever the hell happened that everyone died
			desc = "Everyone died, thus the players lost. How did you manage it anyway?"
			return True, desc
		return False, ""

	def this_turn(self):
		msg = ""
		if (self.turn_qeue[self.turn].dead):
			return self.next_turn()

		if isinstance(self.turn_qeue[self.turn], Enemy):
			#print( "%s's turn"%(self.turn_qeue[self.turn]) ) 
			msg += self.ai_turn()
			return msg + self.next_turn()
		else:
			return "It's %s's turn.\n"%(self.turn_qeue[self.turn].name)

	def next_turn(self):
		msg = ""

		fight_ended, desc = self.check_winning_conditions()
		if fight_ended:
			msg += desc
			return msg + self.finish()

		self.turn += 1
		if self.turn > len(self.turn_qeue)-1:
			return msg + self.next_round()

		if (self.turn_qeue[self.turn].dead):
			return self.next_turn()

		for creature in self.turn_qeue:
			if not creature.dead:
				msg += creature.on_turn()
		return msg + self.this_turn()

	def update_turn_qeue(self):
		alive_enemies =  list(filter(lambda c: not c.dead, self.enemies.copy()))
		alive_players =  list(filter(lambda c: not c.dead, self.players.copy()))
		alive_creatures = alive_enemies + alive_players
		qeue = sorted(alive_creatures, key=lambda x: x.characteristics["dexterity"], reverse=True)
		combat_logger.info("Combat qeue:\n"+", ".join(["["+str(i)+"]"+qeue[i].name for i in range(len(qeue))]))
		return qeue

	def ai_turn(self):
		use_infos = self.turn_qeue[self.turn].act(self)
		combat_logger.info("   AI(%s) actions:"%(self.turn_qeue[self.turn].name))
		msg = ""
		for use_info in use_infos:
			combat_logger.info("Ability use info:\n---\n%s"%(str(use_info)))
			msg += use_info.description
		return msg

	allowed_commands = {
		"examine": "shows your stats","ex": "shows your stats","stats": "shows your stats",
		"examine [creature]": "shows a creature's stats", "ex [creature]": "shows a creature's stats", 
		"info": "shows help","help": "shows help","h": "shows help",
		"status": "shows where you are and what you are doing",
		"turn": "ends turn", "t": "ends turn",
	}

	def handle_combat_command(self, user, command, *args):
		combat_logger.info("Command from user %s: %s %s"%(user.id, command, " ".join(args)))
		if hasattr(self.turn_qeue[self.turn],"userid") and self.turn_qeue[self.turn].userid == user.id: #current turn is of player who sent command
			if command in list(self.user_abilities[user.id].keys()):
				ability = self.user_abilities[user.id][command]
				ability_class = self.user_abilities[user.id][command].__class__
				granted_by = ability.granted_by
				argument = " ".join(args)
				target = None
				if len(argument) > 0:
					for i in range(len(self.turn_qeue)):
						t = self.turn_qeue[i]
						if t.name == argument or argument.isdigit() and int(argument) == i:
							target = t

					can_use, cant_use_msg = ability_class.can_use( self.users_to_players[user.id], target )
					if can_use:
						use_info = ability_class.use( self.users_to_players[user.id], target, granted_by, self )
						combat_logger.info("Ability use info:\n---\n%s"%(str(use_info)))
						self.abilities_used.append(use_info)
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
		super(CombatEvent, self).handle_command(user, command, *args)
		if (command in ["help","info","h"]):
			help_text = print_available_commands(self.allowed_commands)
			help_text += "\n" + print_combat_abilities(self.user_abilities[user.id])
			return help_text
		elif (command in ["examine", "stats", "ex", "st"]):
			if len(args) == 0:
				return  (self.users_to_players[user.id]).examine_self()
			if len(args) > 0:
				argument = " ".join(args)
				if argument=="self" or argument == user.id or argument == self.users_to_players[user.id].name:
					return (self.users_to_players[user.id].examine_self())
				elif argument.isdigit():
					if int(argument) < len(self.turn_qeue):
						return self.turn_qeue[int(argument)].examine_self()
				else:
					for u in self.users:
						target_ply = self.users_to_players[u.id]
						if u.id == argument or target_ply.name == argument:
							return target_ply.examine_self()

					for enemy in self.enemies:
						if enemy.name == argument:
							return enemy.examine_self()

					for key in list(self.user_abilities[user.id].keys()):
						if key == argument:
							return self.user_abilities[user.id][key].description

				return "No such player, user, enemy or ability."

		elif (command in ["say", "s"]):
			if len(args)>0:
				msg = " ".join(args)
				broadcast = []
				broadcast.append([user, "You said:"+msg])
				for u in self.users:
					if user.id != u.id:
						broadcast.append([u, "%s said:%s"%(user.id.title(), msg)])
				return broadcast
			return "Specify what you want to say."

		elif (command in ["turn", "t"]):
			if hasattr(self.turn_qeue[self.turn],"userid") and self.turn_qeue[self.turn].userid == user.id:
				
				msg = self.next_turn()
				msg_others = "%s ends turn.\n"%(self.users_to_players[user.id].name.title()) + msg
				broadcast = []
				broadcast.append([user, msg])
				for u in self.users:
					if u.id != user.id:
						broadcast.append([u, msg_others])
				return broadcast
			return "It's not your turn!"

		elif (command in ["status"]):
			msg = self.status(user)
			return msg

		else:
			if command in list(self.user_abilities[user.id].keys()): #is it a combat ability?
				return self.handle_combat_command(user, command, *args)
			return "Unknown command, try help."
	
	def finish(self):
		msg = ""
		for creature in self.turn_qeue:
			msg += creature.on_combat_over()

		msg += super(CombatEvent, self).finish()

		return msg


