import random
import statistics
import logging
from .. import abilities
from ..bot_events import *
from ..util import *
from ..enemies import *
from ..level_perks import *
logger = logging.getLogger("dungeon_bot_test_log")
logger.debug("Test abilities loaded")

class MockUser(object):
		def __init__(self, userid):
			self.userid = userid
			self.username = userid
			self.id = userid

def test_attack_abilities(player, enemy = None):

	def finished_callback(event):
		combat_event = None
		return('Event is over')

	user = MockUser(player.userid)
	dummy = enemy or Dummy()

	combat_event = CombatEvent(finished_callback, [player], [user], [dummy])
	
	available_abiltiies = player.abilities
	for testing_ability in available_abiltiies:
		for x in range(1000):
			dummy_pos = next((x for x in range(len(combat_event.turn_queue)) if combat_event.turn_queue[x] == dummy), None)
			#ability_pos = next((x for x in range(len(player.abilities)) if player.abilities[x].name == testing_ability ), None)
			command = testing_ability.name
			args = [str(dummy_pos+1)] 
			#msg = command.strip().lower().split(' ')
			#command, args = msg[0], msg[1:]
			output = combat_event.handle_command(user, command, *args)
			player.energy = player.stats["max_energy"]
			dummy.health = dummy.stats["max_health"]
			dummy.refresh_modifiers()
		all_testing_ability_uses = [use_info for use_info in combat_event.abilities_used if use_info.prototype_class ==testing_ability.__class__ and use_info.inhibitor == player and use_info.ability_type == "attack"]
		
		if len(all_testing_ability_uses) > 0:
			logger.info("Ability %s with item %s."%(testing_ability.name,testing_ability.granted_by.short_desc))
			logger.info("Used %d times."%(len(all_testing_ability_uses)))
			logger.info("Ability did hit  %d times."%(len([u for u in all_testing_ability_uses if u.use_info["did_hit"]])))
			logger.info("Ability average chance to hit %f."%(sum([u.use_info["hit_chance"] for u in all_testing_ability_uses])/len(all_testing_ability_uses)))
			logger.info("Ability average damage dealt %f."%(sum([u.use_info["damage_dealt"] for u in all_testing_ability_uses])/len([u for u in all_testing_ability_uses if u.use_info["did_hit"] ]) ) )
			logger.info("Critical applied %d times."%( len( [u for u in all_testing_ability_uses if len(u.use_info["modifiers_applied"]) >0]) ) )
			logger.info("Critical effects per energy used: %f."%(len( [u for u in all_testing_ability_uses if len(u.use_info["modifiers_applied"]) >0])/ abs(sum([ u.use_info["energy_change"] for u in all_testing_ability_uses]))))
			logger.info("Dmg per energy used: %f."%(sum([u.use_info["damage_dealt"] for u in all_testing_ability_uses]) /abs(sum([ u.use_info["energy_change"] for u in all_testing_ability_uses]))))
			logger.info("")
		else:
			logger.info("ability %s werent used one time."%(testing_ability.name))
			logger.info("output %s, ability uses \n-----\n%s\n-----\n."%(output,all_testing_ability_uses))
	combat_event.finish()
		
def controlled_combat_event(players, enemies):

	def finished_callback(event):
		combat_event = None
		return('Event is over')
	users = []
	for player in players:
		users.append(MockUser(player.userid))

	combat_event = CombatEvent(finished_callback, players, users, enemies)
	
	print("Running controlled combat event.")
	logger.info(combat_event.greeting_message)
	while combat_event != None:
		inp = input(">")
		msg = inp.strip().lower().split(' ')
		

		user = next((x for x in combat_event.users if x.userid == combat_event.turn_queue[combat_event.turn].userid), None)
		command, args = parse_command(inp)
		output = combat_event.handle_command(user, command, *args)
		for player in combat_event.players:
			player.energy = player.stats["max_energy"]

		if isinstance(output, list):
			for msg in output:
				print("%s received:\n-%s-\n"%(msg[0].userid, msg[1] ))
				if "Event is over" in msg[1]:
					return
		else:
			print(output)
		if "Event is over" in output:
			return


def test_weapon_abilities():


	ply = Player("testman", "testply")
	items = [x for x in list(item_listing["primary weapon"].keys())] + [x for x in list(item_listing["secondary weapon"].keys())]
	dummy = Dummy(100000)
	dummy.tags = []
	ply.characteristics["dexterity"] = 5
	ply.characteristics["intelligence"] = 5
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
	ply = Player("player1", "testply1 the ply", 20)
	# itemname = "hermit cloak"
	# ply.level_perks.append(Knight(ply))
	# while(True):
	# 	item = get_item_by_name(itemname, 0.5)
	# 	print(item)
	# 	ply.add_to_inventory(item)
	# 	ply.equip(item)
	# 	ply.unequip(item)
	# 	inp = input("type stop to stop")
	# 	if inp == "stop":
	# 		break

	for enemy_table in list(enemy_tables.keys()):
		for diff in list(enemy_tables[enemy_table].keys()):
			enemies = enemy_tables[enemy_table][diff]
			en, desc = enemies[0](*enemies[1])
			print(en, desc)


	#test_weapon_abilities()
	#controlled combat event
	
	#ply1 = Player("player2", "testply2")

	item = "hermit cloak"
	item = get_item_by_name(item, 1)
	logger.info(item.examine_self())
	#item.stats["accuracy"] = "100d10"
	#item.stats["damage"] = "7d1"
	ply.inventory.append(item)
	ply.equip(item, True)
	
	ply.base_characteristics["intelligence"] = 6

	
	dummy = Dummy(10)

	#ply.refresh_derived()
	# item = "dagger"
	# item = get_item_by_name(item)
	# ply.add_to_inventory(item)
	# ply.equip(item)

	#enemies = mercenary_pack
	enemies, desc = mercenary_pack("medium")
	controlled_combat_event([ply], enemies)