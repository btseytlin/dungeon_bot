#!/usr/bin/env python3
import uuid
import json
import random
import math
import unicodedata as ud
def get_uid():
	return str(uuid.uuid4())[:8]

def get_health_for_level(vit, level):
		return int(vit*10 + ((vit + level) * math.log(clamp(vit, 1.5, 10))*5))

def clamp(value, range_min, range_max):
	# if isinstance(range_min, float) or isinstance(range_max, float):
	# 	if value > range_max:
	# 		return range_max
	# 	elif value < range_min:
	# 		return range_min
	# 	return value
	return max(range_min, min(value, range_max))

def print_combat_abilities(combat_abilities):
	help_text = "Available combat commands:\n"
	help_text += " command | energy_required | item used\n"
	for key in list(combat_abilities.keys()):
		ability = combat_abilities[key]
		help_text += "%s | %s | %s\n"%(key, ability.energy_required, ability.granted_by.name )
	return help_text

def parse_command(text):
	words = text.strip().lower().split(' ')
	if len(words) > 1:
		command = " ".join(words[:-1])
		args = [words[-1]]
	else:
		command = words[0]
		args = []
	command = " ".join(words)
	args = []
	return command,args

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

def diceroll(string, form_uniform=False, mode_loc = 0.9):
	negative = False
	if string[0] == "-":
		negative = True
		string = string[1:]
	nums = [int(x) for x in string.split("d")]
	total_sum = 0 
	for i in range(0, nums[0]):
		if form_uniform:
			total_sum += int(random.randint(1, nums[1]))
		else:
			if nums[1] <= 1:
				total_sum += 1
			else:
				total_sum += int(random.triangular(1.0, nums[1], mode_loc*nums[1]))

	if negative:
		total_sum *= -1

	return total_sum

def triangular(low=0.0, high=1.0, mode=None): #dont ask
	u = random.random()
	if mode is None:
		c = 0.5
	elif mode == high:
		c = 1
	else:
		c = (mode - low) / (high - low)
	if u > c:
			u = 1.0 - u
			c = 1.0 - c
			low, high = high, low
	return low + (high - low) * (u * c) ** 0.5

def random_in_range_for_coolity(left, right, mode_pos=0.5):
	if left == right:
		return left
	mode = clamp( mode_pos * right, left, right )
	return triangular( left, right, mode )

def get_dice_in_range(dice_range, coolity, inverse = False): #returns dice in range. Coolity is 0..1, more means values are more likely to be closer to right boundary

	#If inverse = true then smaller numbers will be at the right border. So the numbers to pick from will be sorted from max to min, "smaller is better"
	#If inverse = false then numbers are sorted from min to max, "bigger is better"
	d_range = dice_range.copy()
	negative = False
	if d_range[0][0] == "-" and d_range[1][0] == "-":
		negative = True
		d_range[0] = d_range[0][1:]
		d_range[1] = d_range[1][1:]

	dice_one = [int(x) for x in d_range[0].split("d")]
	dice_two = [int(x) for x in d_range[1].split("d")]
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

	if len(dice_amount_range) <= 1:
		random_for_coolity = 0
	else:
		random_for_coolity = random_in_range_for_coolity(0, len(dice_amount_range)-1, coolity)
	random_amount_index = int( math.ceil(random_for_coolity ))
	dice_amount = dice_amount_range[random_amount_index]

	if len(dice_nominal_range) <= 1:
		random_nominal_index = 0
	else:
		random_nominal_index = int( math.ceil(random_in_range_for_coolity(0, len(dice_nominal_range)-1, coolity)) )
	dice_nominal = dice_nominal_range[random_nominal_index]

	if negative:
		return "-"+str(dice_amount) + "d" + str(dice_nominal)
	return str(dice_amount) + "d" + str(dice_nominal)



def get_number_in_range(number_range, coolity, inverse = False): #returns dice in range. Coolity is 0..1, more means values are more likely to be closer to right boundary

	#If inverse = true then smaller numbers will be at the right border. So the numbers to pick from will be sorted from max to min, "smaller is better"
	#If inverse = false then numbers are sorted from min to max, "bigger is better"
	negative = False
	if number_range[0] < 0 and number_range[1] < 0:
		negative = True

	if number_range[0] > number_range[1]:
		inverse = True

	if not inverse:
		left = min(number_range[0], number_range[1])
		right = max(number_range[0], number_range[1])
		number_range = range(left, right+1)

	else:
		left = max(number_range[0], number_range[1])
		right = min(number_range[0], number_range[1])
		number_range = range(left, right-1, -1)

	if len(number_range) <= 1:
		random_for_coolity = 0
	else:
		random_for_coolity = random_in_range_for_coolity(0, len(number_range)-1, coolity)
	random_ind = int( math.ceil(random_for_coolity ))
	number = number_range[random_ind]

	return number
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



latin_letters= {}

def is_latin(uchr):
	try: return latin_letters[uchr]
	except KeyError:
		return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

def only_roman_chars(unistr):
	return all(is_latin(uchr)
			for uchr in unistr
			if uchr.isalpha()) # isalpha suggested by John Machin