This guide will walk you through creating items, modifiers, enemies, perks.

### Cloning and making pull requests
Contributing requires making pull requests so reading the [contributing to open source guide](https://guides.github.com/activities/contributing-to-open-source/) is required if you are new.


## Making an item

Making an item consists of following steps: 
* adding the item to the item table
* adding the item to loot drop tables.

Let's add a rapier, a primary weapon utilising existing abilities. 

#### Adding
Open `items.py`.

A rapier is quite accurate, but it doesn't deal much damage.
Go the bottom of `items.py`, to `item_listing`.
Taking analogy from sword let's make a rapier entry in the "primary_weapon" category.
```
item_listing: {
	"primary_weapon":{
		"rapier": {
        	"stats": {
        		"damage" : ["1d6","2d6"],
        		"accuracy" : ["2d6","7d6"]
        	},
        	"args":{
            	"name":"rapier",
           		"description":"Steel rapier!",
            	"abilities_granted":["stab"]
            }
        }
        #other primary weapons
	},
	#other item categories
}
```
After the item has been added to the item listing, let's make it so undead soldier enemies will sometimes spawn with rapiers.

Open `enemies.py` and find class `UndeadSoldier`. In the constructor of the class find line
```
		items = [get_item_by_name( random.choice(["club", "sword", "dagger", "mace"]), 0 )]
```
These are the weapons an undead soldier can spawn with. Change it to:
```
		items = [get_item_by_name( random.choice(["club", "sword", "dagger", "mace", "rapier"]), 0 )]
```
Done, now let's make them drop rapiers too.

Find the `drop_table` propery of the `UndeadSoldier` class.
```
drop_table = {
	"chainmail" : 3,
	#other items
	"random": 3,
}
```

Add `"rapier": 5,` to the top.
```
drop_table = {
	"rapier": 5,
	"chainmail" : 3,
	#other items
	"random": 3,
}
```
Done! Now UndeadSoldiers will drop rapiers with 5% chance!

#### Explanation

**Item listing explained.**

You can see the 5 basic prototypes for items: *PrimaryWeapon, SecondaryWeapon, Armor, Helmet, Ring, Talisman*.
`item_listing` contains all the parameters for items in the game.
Let's take, for example, club.
```
"club": {
	"stats": {
		"damage" : ["1d3","2d6"],
    	"accuracy" : ["1d6","2d6"]},
    }
    "args":{
    		"name":"club",
    		"description":"A rough wooden club, good enough to break a skull!", 
    		"abilities_granted":["smash"]
    }
    
}
```
That info means that if we call `get_item_by_name("club")` (that function is called every time loot is dropped and items are given to enemies on spawn) we will get a PrimaryWeapon object with `"damage"` stat somewhere between `"1d3"` and `"2d6"`. So it could be anything among *"1d3", "1d4, "1d5", "1d6", "2d1", "2d2", "2d3", "2d4", "2d5", "2d6"*.

The right range boundary is considered the best possible condition. 

Range values can be negative, for example:
`"accuracy" : ["-1d6","2d6"]`.

Ranges can be inverse, from max to min, like armor evasion ranges:
`"evasion": ["-3d4","-1d2"]`

Mind that absolute dice value decides if the range will be inverse or not. In the case above *"-3d4"* will be considered the absolute worst outcome, *"-1d2"* will be considered the absolute best. That's useful if you want an item that applies an evasion penalty and you want the best item to have *the smallest penalty*.


`"abilities_granted"` specifies names of abilities a creature will be given when it's equipped. The actual class of the available ability can be found in `abilities.py`. You can see that `"smash"` will be mapped to the `"Smash"` class.
Abilities are exactly the combat commands a creature will be able to use in a fight.
Other available options to `"stats"` are fields `"modifiers_granted"` and `"tags_granted"`.

`"modifiers_granted"` work just like abilities, modifier (temporary or permanent effects, such as bleeding or getting 10% more experience every experience gain) names are specified. You can see what modifiers exist in `modifiers.py`, `modifier_listing` dictionary.

`"tags_granted"` are just strings that will be appended to a creature's `.tags` list when the item is equipped. For example equipping *chainmail* will add the tag `"armor"`. Tags are used by various ability formulas to change effectiveness of attacks. For example `Smash` is more likely to knockdown an enemy with `"armor"` tag.

An item's `"stats"` can also have various bonuses. For example:
```
"ring of thievery": {
	"stats": {
		"stats_change": {
			"evasion": ["1d6", "3d6"]
		},
			"characteristics_change": {
		"dexterity" : [0, 2]
		}
	},
	"args":{
		"name":"ring of more thievery",
		"description":"Gives a dex bonus and an evasion bonus."
	}
 },
```
This item gives a bonus  *characteristics* and to *evasion*.
Note that characteristics also come in ranges, but in regular numbers. Notation above means that the ring of thievery can have a dex bonus of 0, 1 or 2.

That's can also contain values that will be used by various modifiers. Take a look at `"amulet of healing"` or `"ring of fire"`.

**Drop tables explained.**

Each key of a drop table is either an item name, item type or `"random"`. The value is the drop chance in percents.
* `"chainmail": 3` means that there is a 3% chance this enemy will drop a chainmail on death.
* `"armor": 3` means that there is a 3% chance this enemy will drop a random item from the armor category.
* `"random": 3` means that there is a 3% chance this enemy will drop a random item from any category.

The function `get_item_by_name` accepts `coolity` as a second argument. Coolity can be a number between 0 and 1. More coolity means more chance that ranges will tilt towards the right boundary. 
For example for item:
```
"ring of fire": {
		"stats": {
		"fire_damage" : ["1d3","2d6"],
		"fire_chance" : ["1d4", "6d6"]
	},
	"args":{"name":"ring of fire", "description":"Has a chance to cause fire damage on attack.",
		"modifiers_granted": [
			{
				"name":"fire_attack", 
				"params":{}
			} 
		]
	}
},
```
If you call `get_item_by_name("ring of fire", 1)` (coolity = 1) there will be an almost 30 percent chance to get `"fire_chance": "6d6"`. If you call `get_item_by_name("ring of fire", 0)` there will be an almost 30 percent chance to get `"fire_chance": "1d4"`.

So, more coolity means cooler loot.

Every enemy class has a `loot_coolity` property. That's the coolity used when an enemy of that class drops loot and items are spawned.
This way if you want an enemy to drop mostly cool loot you should set it to 1. 
A generic rat usually drops bad items because it has `loot_coolity = 0`.

## Making an enemy

Making an enemy consists of following steps: 
* creating the enemy class
* adding the enemy to dungeon tables
 
Let's add a thug, a human enemy with high vitality and strength.

#### Adding
Open `enemies.py`.

Go the section marked by a comment:
```
""" human enemies below """
```

Taking analogy from peasant let's make a `Thug` class.
Add the following:
```
thug_characteristics = {
	"strength": 7,
	"vitality": 6,
	"dexterity": 4, 
	"intelligence": 4,
}

class Thug(Enemy):
	drop_table = {
		"club" : 7,
		"mace": 4,
		"primary_weapon": 3,
		"armor": 4,
		"ring of more strength" : 5,
		"ring of more intelligence" : 2,
		"ring" : 3,
		"talisman": 4,
		"helmet": 3,
		"headwear": 5,
		"random": 3,
	}
	loot_coolity = 0.5
	def __init__(self, level=1, name="thug", characteristics = thug_characteristics, stats=None, description="A thug, strong and massive, but quite slow.", inventory=[], equipment=default_equipment, tags=["animate", "humanoid", "slow", "big"],abilities=[],modifiers=[], exp_value=200):
		Enemy.__init__(self, name, level, characteristics, stats, description, inventory, equipment, tags, abilities, modifiers, exp_value)
		items = [get_item_by_name( random.choice(["club", "sword", "mace"]), 0 )]
		for item in items:
			self.inventory.append(item)
			self.equip(item)

	def act(self, combat_event):
		attack_infos = []

		if not self.target or self.target.dead:
			self.select_target(combat_event)
		if self.target and not self.target.dead:
			for ability in self.abilities:
				while self.energy >= ability.energy_required:
					attack_infos.append(ability.__class__.use(self, self.target, ability.granted_by, combat_event))
					if not self.target or self.target.dead:
						break
				if not self.target or self.target.dead:
						break

		return attack_infos
```

We have added the class, but it won't spawn in the world yet.
head to `enemy_tables` at the bottom of the document. Add the following entry to the `"human"` category:
```
enemy_tables: {
#other categories
	"human":{
		"1": (thugs, []),
		"5": (thugs, ["small"]),
		"10": (thugs, ["medium"]),
        #other human enemy functions
	}
}
```
Now directly above `enemy_tables` add the `thugs` function:

```
def thugs(size):
	description = "A thug.\n"
	levels = list(range(1,5))
	amount = 1
	if size == "small":
		amount = random.randint(2, 3)
		if amount != 1:
			description = "A small group of thugs.\n"
	elif size == "medium":
		description = "A group of thugs.\n"
		amount = random.randint(3, 5)

	elif size == "big":
		description = "A hoard of thugs.\n"
		amount = random.randint(5, 8)

	elif size == "huge":
		description = "thugs are everywhere.\n"
		amount = random.randint(8, 15)
	thugs = [ Thug(random.choice(levels)) for x in range(amount+1)]
	return thugs, description
 ```
    
Done! Now in dungeons with difficulty approximately 1 to 13 thugs of levels 1 to 5 will spawn. Either a lone thug, a small group of thugs or a medium group of thugs.

#### Explanation

Creating the enemy class has some quirks to it.

**Enemy classes explained.**

Enemies gain combat abilities just like players: from equipment and modifiers.
That means if you want an enemy to swing a sword you have got to give that enemy a sword.
This is why in the constructor, right after initializing the enemy, we give the enemy items and equip them:
```
items = [get_item_by_name( random.choice(["chainmail", "plate armor"], 0), get_item_by_name( random.choice(["club", "sword", "mace"]), 0 )]
for item in items:
	self.inventory.append(item)
    self.equip(item)
```

If you want your enemy to do something special, not covered by current items, you should add a special item for it.
This way `Rat` and `BigRat` have a special item `rodent_teeth` dedicaded to give them the `RodentBite` ability.
Say you are making a mage that throws fireball. The logical way is to create an ability `Fireball`, an item `fire staff` that grants ability `fireball`, and give a `fire staff` to each mage on creation.

How the enemies will use their abilities is defined in the `act` method. It's called every turn, the method has to return an list of abilities used (more on `ability_info` later).

It can be simple as the one we used for thugs, which basically means "use available abilities until I run out of energy", or it can be something complex and tactical. 
The method accepts `combat_event` instance (see `bot_events.py`) that has such properties as `turn_qeue`, `players`, `enemies`. It allows you to get all the information about the combat situation so the enemy can make tactical decisions, change targets and use specific abilities.

Optionally the method `select_target` of the `Enemy` class can be overriden to specify how an enemy will pick it's targets. By default enemies pick random targets from among the living players.

**Enemy tables explained.**

If you take a look at the `dungeons` dictionary  in `dungeon.py` you will see the current types of dungeons, for example:
```
dungeons = {
	"Bandit den" : {
		"description": "All kinds of scum find shelter in these caves.", 
		"enemy_types":["common", "human"]
	},
}
```
`enemy_types` here are a list of keys for `enemy_table`. 

Basically it specifies from where will a dungeon draw enemies when generating rooms. 

Back to `enemies.py` `enemy_tables`. We want some enemies appear in numbers (like rats), we wants some enemies to appear alone, we want some enemies to appear high leveled and others low leveled.
That's where enemy functions come in.
In `enemy_tables` the keys are difficulty ratings and values are tuples of enemy function and it's arguments.
```
enemy_tables = { # 
	"common": { 
		"1": (rat_pack, [] ),
		"1": (rat_pack,["small"] ),
		"5": (rat_pack, ["medium"] ),
     }
}
```
Difficulty rating is a number 1 to 100 that represents what dungeon difficulty that enemy should appear in. A dungeon difficulty is calculated as average of players levels. 

A difficulty rating of 6 means that dungeons with difficulty from 3 to 9 has a chance of spawning this group of enemies. See `retrieve_enemies_for_difficulty` in `enemies.py` for more information.
Yes, that means there is always a chance to get an enemy that's dedicated for higher difficulty then the current difficulty. That's made so that players will face some challange.

Enemy functions like `rat_pack` and `thugs` are functions that return a list of enemy objects and a description for the encounter. 
It doesn't matter how you create  the objects inside the function. It's only known that if you put a function in an enemy
 table and a list of arguments for it, it  will be called with that list of arguments unpacked.
 
 You can make your own functions with any kind of arguments:
 ```
def ouch(fruit):
	rat = Rat(random.randint(100, 10000))
    description = "You are witnessing a huge rat that got really big by eating %s."%(fruit)
    return [rat], description #return a list of enemies even if there is just one enemy
"common": { 
  "50": (ouch, ["bananas"] ),
}
 ```
 