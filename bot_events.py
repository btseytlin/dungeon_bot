import persistence
import logging
import items
persistence_controller = persistence.get_persistence_controller_instance()


class BotEvent(object):
	def __init__(self, finished_callback, uid, users):
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

	def __init__(self, finished_callback, uid, user):
		BotEvent.__init__(self, finished_callback, uid, [user])
		self.user = user
		self.current_step = 0
		self.new_player = persistence_controller.get_ply(user)
		return('You can restart the registration at any time by sending "restart".\nLet\'s begin.\nWhat is your name?')

	def handle_command(self, command, *args):
		if command == "restart":
			self.current_step == 0
			return("Let's begin. What is your name?")

		if self.current_step == 0:
			self.new_player.name = (command + " " + " ".join([str(arg) for arg in args])).strip().title()
			self.current_step+=1
			return("What is your race?")

		elif self.current_step == 1:
			self.new_player.race = command
			return("What is your class?")
			self.current_step+=1

		elif self.current_step == 2:
			self.new_player.combat_class = command
			self.new_player.inventory = [PrimaryWeapon("club", "A rough wooden club, good enough to break a skull!", "blunt", {"damage" = "1d3", "accuracy" = "3d6"}, ["swing"]]
			return('Registration complete! Try "examine" to see your stats, "inventory" to see your items.')
			
			self.finish()

class Inventory(BotEvent):

	allowed_commands = {
		"examine": "shows your stats and inventory","ex": "shows your stats and inventory","stats": "shows your stats and inventory",
		"examine [item]": "shows an item's stats", "ex [item]": "shows an item's stats", 
		"equip [item]": "equips an item","eq [item]": "equips an item",
		"use [item]": "uses an item (such as a potion)", "u [item]": "uses an item (such as a potion)",
		"destroy [item]": "destroys an item","drop [item]": "destroys an item",
		"give [item] [username/playername]": "gives an item to another player",

		"info": "shows help","help": "shows help","h": "shows help",
		"back": "closes inventory","abort": "closes inventory","ab": "closes inventory","b": "closes inventory",
	}

	def __init__(self, finished_callback, uid, user):
		BotEvent.__init__(self, finished_callback, uid, [user])
		self.user = user
		self.player = persistence_controller.get_ply(user)
		return('You can close inventory at any time by sending "back" or "abort".')

	def find_item(self, itemname, player, inventory_only = False):
		all_items = self.player.inventory
		if not inventory_only:
			all_items += player.equipment.values()

		for item in all_items:
			if item.name == itemname:
				return True, item

		error_text = "No such item in your inventory"
		if not inventory_only:
			error_text += "or equipment."
		else 
			error_text += "."
		return False, error_text


	def handle_command(self, command, *args):
		if not command in allowed_commands.keys():
			return self.bot.reply_error(self.user)

		if (command in ["help","info","h"]):
			return(util.print_available_commands(allowed_commands))

		if (command in ["examine","ex","stats","st"]) and len(args) == 0:
			if len(args) == 0:
				self.bot.handle_command(command, args)
				self.player.examine_inventory()
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player)
				if found:
					msg = item.examine_self()
					return(msg)
				else:
					return item

		elif (command in ["equip", "eq"]):
			if len(args) == 0:
				return("Specify an item to equip.")
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player, True)
				if found:
					msg = item.equip(user)
					return(msg)
				else:
					return item

		elif (command in["use", "u"]):
			if len(args) == 0:
				return("Specify an item to use.")
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player)
				if found:
					msg = item.use(user)
					return(msg)
				else:
					return item

		elif (command in ['destroy', 'drop']):
			if len(args) == 0:
				return("Specify an item to destroy.")
			elif len(args) > 0:
				found, item = self.find_item(" ".join(args), self.player)
				if found:
					msg = item.destroy(user)
					return(msg)
				else:
					return item

		elif (command == "give"):
			return "WIP FEATURE"

		elif (command in ["back", "abort", "ab", "b"]):
			self.finish()
