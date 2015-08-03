import random
import statistics
import logging
from .. import abilities
from ..bot_events import *
from ..util import *
from ..enemies import *
logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test abilities loaded")

def test_attack_abilities(player, enemy = None):
	class MockUser(object):
		def __init__(self, username):
			self.username = username

	def finished_callback(event):
		combat_event = None
		return('Event is over')

	user = MockUser(player.username)
	dummy = enemy or Dummy()

	combat_event = CombatEvent(finished_callback, [player], [user], [dummy])
	
	available_abiltiies = player.abilities
	for testing_ability in available_abiltiies:
		for x in range(1000):
			dummy_pos = next((x for x in range(len(combat_event.turn_qeue)) if combat_event.turn_qeue[x] == dummy), None)
			#ability_pos = next((x for x in range(len(player.abilities)) if player.abilities[x].name == testing_ability ), None)
			command = testing_ability.name
			args = [str(dummy_pos)] 
			#msg = command.strip().lower().split(' ')
			#command, args = msg[0], msg[1:]
			output = combat_event.handle_command(user, command, *args)
			player.energy = player.stats["max_energy"]
			dummy.health = dummy.stats["max_health"]
			dummy.refresh_modifiers()
		all_testing_ability_uses = [use_info for use_info in combat_event.abilities_used if use_info.prototype_class ==testing_ability.__class__ and use_info.inhibitor == player and use_info.ability_type == "attack"]
		if len(all_testing_ability_uses) > 0:
			print("Ability %s used %d times."%(testing_ability.name, len(all_testing_ability_uses)))
			print("Ability did hit  %d times."%(len([u for u in all_testing_ability_uses if u.use_info["did_hit"]])))
			print("Ability average chance to hit %f."%(sum([u.use_info["hit_chance"] for u in all_testing_ability_uses])/len(all_testing_ability_uses)))
			print("Ability average damage dealt %f."%(sum([u.use_info["damage_dealt"] for u in all_testing_ability_uses])/len([u for u in all_testing_ability_uses if u.use_info["did_hit"] ]) ) )
			print("Critical applied %d times."%( len( [u for u in all_testing_ability_uses if len(u.use_info["modifiers_applied"]) >0]) ) )
			print("Critical effects per energy used: %f."%(len( [u for u in all_testing_ability_uses if len(u.use_info["modifiers_applied"]) >0])/ abs(sum([ u.use_info["energy_change"] for u in all_testing_ability_uses]))))
			print("Dmg per energy used: %f."%(sum([u.use_info["damage_dealt"] for u in all_testing_ability_uses]) /abs(sum([ u.use_info["energy_change"] for u in all_testing_ability_uses]))))
			print("")
	combat_event.finish()
		
def controlled_combat_event(players, enemies):
	class MockUser(object):
		def __init__(self, username):
			self.username = username

	def finished_callback(event):
		combat_event = None
		return('Event is over')
	users = []
	for player in players:
		users.append(MockUser(player.username))

	combat_event = CombatEvent(finished_callback, players, users, enemies)
	
	print("Running controlled combat event.")
	print(combat_event.greeting_message)
	while combat_event != None:
		inp = input(">")
		msg = inp.strip().lower().split(' ')
		command, args = msg[0], msg[1:]
		user = next((x for x in combat_event.users if x.username == players[0].username), None)
		output = combat_event.handle_command(user, command, *args)
		if isinstance(output, list):
			output = output[0][1]
		print(output)
		if "Event is over" in output:
			break


def test_abilities():
	ply = Player("testman", "testply")
	items = [x for x in list(item_listing["primary_weapon"].keys())] + [x for x in list(item_listing["secondary_weapon"].keys())]
	dummy = Dummy(100000)
	ply.characteristics["dexterity"] = 10
	#armor = get_item_by_name("plate armor")
	#dummy.inventory.append(armor)
	#dummy.equip(armor)
	for item in items:
		item = get_item_by_name(item)
		ply.inventory.append(item)
		ply.equip(item)
		test_attack_abilities(ply, dummy)
		ply.strip()
		ply.clear_inventory()

def run_tests():
	test_abilities()
	#controlled combat event
	ply = Player("testman", "testply")
	item = "club"
	item = get_item_by_name(item)
	ply.inventory.append(item)
	ply.equip(item)
	enemy = Rat()
	controlled_combat_event([ply], [enemy])