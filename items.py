class Item(object):
	def __init__(self, name, description, requirements = None, item_type):
		self.name = name
		self.description = description
		self.requirements = requirement
		self.item_type = item_type

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
	def __init__(self, name, description, requirements = default_weapon_requirements, item_type="weapon", stats=default_weapon_stats, abilities_granted = default_weapon_abilities):
		Item().__init__(self, name, description, requirements, item_type)
		self.abilities_granted = abilities_granted

	def equip(self, target):
		return "succesfully equipped"
		

	def unequip(self, target):
		return "succesfully unequipped"
		