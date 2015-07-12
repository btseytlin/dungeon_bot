class Item(object):
	def __init__(self, name, description, item_type, requirements = None, stats = {},  abilities_granted = [], modifiers_granted = []):
		self.name = name
		self.description = description
		self.requirements = requirement
		self.item_type = item_type

		self.abilities_granted = abilities_granted
		self.stats = stats
		self.modifiers_granted = modifiers_granted

default_weapon_stats= {
	"damage" = 0,
	"accuracy" = 0,
}

default_weapon_requirements = {
	"strength": 0, 
	"vitality": 0, 
	"dexterity": 0,
	"intelligence": 0, 
	"faith": 0, 
}	

default_weapon_abilities = ["attack"]
class Weapon(Item):
	def __init__(self, name, description, item_type="weapon", requirements = default_weapon_requirements,  stats=default_weapon_stats, abilities_granted = default_weapon_abilities, modifiers_granted = []):
		Item().__init__(self, name, description, item_type, requirements, stats, stats, abilities_granted, modifiers_granted)

	def equip(self, target):
		return "succesfully equipped"
		

	def unequip(self, target):
		return "succesfully unequipped"
		