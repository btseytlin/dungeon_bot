import uuid
import json
import random
import math
def get_uid():
	return str(uuid.uuid4())[:8]

def print_combat_abilities(combat_abilities):
	help_text = "Available combat commands:\n"
	help_text += " name | energy_required\n"
	for key in list(combat_abilities.keys()):
		ability = combat_abilities[key]
		help_text += "%s | %s\n"%(ability.name, ability.energy_required )

	return help_text

def print_available_commands(available_commands):
	help_text = "Available commands:\n"
	allowed_comms_descs = {}
	for command in available_commands.keys():
		desc = available_commands[command]
		if not desc in allowed_comms_descs:
			commands_for_desc = [command]
			for comm in available_commands.keys():
				descr = available_commands[comm]
				if descr == desc:
					if not comm in commands_for_desc:
						commands_for_desc.append(comm)
			commands_for_desc = ", ".join(commands_for_desc)
			allowed_comms_descs[desc] = commands_for_desc
	allowed_comms = dict(zip(allowed_comms_descs.values(),allowed_comms_descs.keys()))# swap keys and values in dict
	lines = []
	for comms in allowed_comms.keys():
		desc = allowed_comms[comms]
		lines.append("  %s : %s\n"%(comms, desc))
	lines.sort()
	help_text+= "".join(lines)
	return help_text

def diceroll(string):
	negative = False
	if string[0] == "-":
		negative = True
		string = string[1:]
	nums = [int(x) for x in string.split("d")]
	total_sum = 0 
	for i in range(0, nums[0]):
		total_sum += random.randint(0, nums[1])

	if negative:
		total_sum *= -1

	return total_sum

def random_in_range_for_coolity(left, right, coolity, mode_divider=3, coolity_multiplier = 2):
	coolity_effect = random.uniform(0, coolity) * coolity_multiplier * 3
	mode_divider = clamp( mode_divider - coolity_effect, 1, 999)
	mode = clamp( int( (right) / mode_divider), left, right )
	return random.triangular( left, right, mode )

def get_dice_in_range(dice_range, coolity): #returns dice in range. Coolity is 0..1, more means values are more likely to be closer to right boundary
	dice_amount_range = range(int(dice_range[0][0]), int(dice_range[1][0])+1)
	random_for_coolity = random_in_range_for_coolity(0, len(dice_amount_range)-1, coolity)
	random_amount_index = int( math.ceil(random_for_coolity ))
	dice_amount = dice_amount_range[random_amount_index]

	dice_nominal_range = range(int(dice_range[0][2]), int(dice_range[1][2])+1)
	random_nominal_index = int( math.ceil(random_in_range_for_coolity(0, len(dice_nominal_range)-1, coolity)) )
	dice_nominal = dice_nominal_range[random_nominal_index]

	return str(dice_amount) + "d" + str(dice_nominal)

def clamp(value, range_min, range_max):
	return max(range_min, min(value, range_max))

