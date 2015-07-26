from util import *
class Modifier(object):
	def __init__(self, name, description, on_applied, on_lifted, turns_left):
		self.uid = get_uid()
		self.name = name
		self.description = description
		self.on_applied = on_applied
		self.on_lifted = on_lifted
		self.turns_left = turns_left #duration in turns

	def apply(self, target):
		self.on_applied(target)

	def lift(self, target):
		self.on_lifted(target)


