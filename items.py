class Item(object):
	def __init__(self, name, description, item_type,  stats = {},  abilities_granted = [], modifiers_granted = [], requirements = None,):
		self.name = name
		self.description = description
		self.requirements = requirement
		self.item_type = item_type

		self.abilities_granted = abilities_granted
		self.stats = stats
		self.modifiers_granted = modifiers_granted

	def use(self, target):
		return "Can't use %s."%(self.name)

	def equip(self, target):
		return "Can't equip %s."%(self.name)

	def unequip(self, target):
		return "Can't unequip %s."%(self.name)

	def destroy(self, target):
		self.unequip(target)
		del self
		return "Succesfully destroyed."

	def examine_self(self):
		desc = "%s, a %s."%(self.name.title(), self.item_type )
		if requirements:
			desc += "Requirements to use:\n"+str(self.requirements)
		desc += "Stats:\n"+str(self.stats)
		desc += "Abilities:\n"+str(self.abilities_granted)
		desc += "Modifiers granted:\n"+str(self.modifiers_granted)

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
class PrimaryWeapon(Item):
	def __init__(self, name, description, item_type="primary_weapon", stats=default_weapon_stats, abilities_granted = default_weapon_abilities, modifiers_granted = [], requirements = default_weapon_requirements):
		Item().__init__(self, name, description, item_type, stats, stats, abilities_granted, modifiers_granted, requirements)

	def equip(self, target):
		if target.equipment.primary_weapon == self:
			return "Already equipped %s."%(self.name)

		if target.equipment.primary_weapon:
			temp = target.equipment.primary_weapon
			temp.unequip(target)

		target.equipment.primary_weapon = self
		target.refresh_abilities()
		return "Succesfully equipped %s."%(self.name)
		

	def unequip(self, target):
		if target.primary_weapon == self:
			target.primary_weapon = None
			target.inventory.append(self)
			target.refresh_abilities()
			return "Succesfully unequipped %."%(self.name)
		return "Not equipped!"
	