import uuid
import random 
def get_uid():
	return str(uuid.uuid4())[:8]

def print_available_commands(available_commands):
	help_text += "Available commands:\n"
	allowed_comms_descs = {}
	for command, desc in self.available_commands.iteritems():
		if not desc in allowed_comms_descs:
			commands_for_desc = [command]
			for comm, descr in self.available_commands.iteritems():
				if descr == desc:
					if not comm in commands_for_desc:
						commands_for_desc.append(comm)
			commands_for_desc = ", ".join(commands_for_desc)
			allowed_comms_descs[desc] = commands_for_desc
	allowed_comms = dict(zip(allowed_comms_descs.values(),allowed_comms_descs.keys()))# swap keys and values in dict
	for comms, desc in allowed_comms.iteritems():
		help_text+= "  %s : %s\n"%(comms, desc)
	return help_text

def diceroll(string):
	nums = (int(x) for x in string.split(" "))
	total_sum = 0 
	for i in range(0, nums[0]):
		total_sum += randint(0, num[1])
	return total_sum