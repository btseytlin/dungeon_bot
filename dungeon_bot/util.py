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

def random_in_range_for_coolity(left, right, mode_pos=0.5):
	mode = clamp( mode_pos * right, left, right )
	return random.triangular( left, right, mode )

def get_dice_in_range(dice_range, coolity, inverse = False): #returns dice in range. Coolity is 0..1, more means values are more likely to be closer to right boundary

	#If inverse = true then smaller numbers will be at the right border. So the numbers to pick from will be sorted from max to min, "smaller is better"
	#If inverse = false then numbers are sorted from min to max, "bigger is better"
	negative = False
	if dice_range[0][0] == "-" and dice_range[1][0] == "-":
		negative = True
		dice_range[0] = dice_range[0][1:]
		dice_range[1] = dice_range[1][1:]

	dice_one = [int(x) for x in dice_range[0].split("d")]
	dice_two = [int(x) for x in dice_range[1].split("d")]
	if dice_one[0] > dice_two[0] or dice_one[0] == dice_two[0] and dice_one[1] > dice_two[1]:
		inverse = True

	if not inverse:
		left = min(dice_one[0], dice_two[0])
		right = max(dice_one[0], dice_two[0])
		dice_amount_range = range(left, right+1)

		left = min(dice_one[1], dice_two[1])
		right = max(dice_one[1], dice_two[1])
		dice_nominal_range = range(left, right+1)
	else:
		left = max(dice_one[0], dice_two[0])
		right = min(dice_one[0], dice_two[0])
		dice_amount_range = range(left, right-1, -1)

		left = max(dice_one[1], dice_two[1])
		right = min(dice_one[1], dice_two[1])
		dice_nominal_range = range(left, right-1, -1)

	random_for_coolity = random_in_range_for_coolity(0, len(dice_amount_range)-1, coolity)
	random_amount_index = int( math.ceil(random_for_coolity ))
	dice_amount = dice_amount_range[random_amount_index]

	
	random_nominal_index = int( math.ceil(random_in_range_for_coolity(0, len(dice_nominal_range)-1, coolity)) )
	dice_nominal = dice_nominal_range[random_nominal_index]

	if negative:
		return "-"+str(dice_amount) + "d" + str(dice_nominal)
	return str(dice_amount) + "d" + str(dice_nominal)

def clamp(value, range_min, range_max):
	return max(range_min, min(value, range_max))

def round_to_base(x, base=10):
	return int(base * round(float(x)/base))
	
level_table = {
	"1": 400,
}

def max_exp_for_level(x):
	prev_lvl_exp = level_table["1"]
	if str(x) in level_table.keys():
		return level_table[str(x)]

	if str(x-1) in level_table.keys():
		prev_lvl_exp = level_table[str(x-1)]
		
	cur_level_exp = round_to_base(prev_lvl_exp+prev_lvl_exp*0.05+math.pow(2, (x/5)))
	level_table[str(x)] = cur_level_exp
	return cur_level_exp