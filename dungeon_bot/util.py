import uuid
import json
import random
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

def clamp(value, range_min, range_max):
	return max(range_min, min(value, range_max))