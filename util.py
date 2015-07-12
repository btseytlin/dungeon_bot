import uuid
import random 
import json
def get_uid():
	return str(uuid.uuid4())[:8]

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
	nums = (int(x) for x in string.split(" "))
	total_sum = 0 
	for i in range(0, nums[0]):
		total_sum += randint(0, num[1])
	return total_sum
"""
def deep_jsonify(target):
	print("")
	print("Jsonifying ", target)
	try:
		print("Success, return as it is")
		return target
	except:
		print("Unserializable!")
		if hasattr(target, '__dict__'): 
			print("a class")
			target = target.__dict__
			return deep_jsonify(target)
		if isinstance(target, dict):
			print("a dict")
			for key in target.keys():
				value = target[key]
				print("Now parsing", value)
				try:
					json.dumps(value)
				except (Exception, TypeError):
					print("Unserializable dict val!")
					target[key] = deep_jsonify(value)
			return deep_jsonify(target)

		if hasattr(target, '__iter__'): #if its a list-kinda thing iterate over list
			print("A list", target)
			new_list = []
			for item in target:
				new_list.append(deep_jsonify(item))
			print("Newlist is ", new_list)
			return new_list

"""
