# Dice notation explained

If you are asking what does `"1d6"` mean you are in the right place.
"1d6" means *"roll one dice of 6 sides"*, or in other words it means a random number between 1 and 6.
"2d6" means a random number between 2 and 12.

A negative dice, like "-1d6" means a negative number between 1 and 6. Usually if you see a negative range it's a penalty, for example an armor's penalty to evasion.

# Combat explained

Combat is turn based. At the beginning of each round a turn qeue is formed out of alive creatures, creatures with most dexterity first, creatures with least dexterity.

All creatures begin combat with their maximum energy. All abilities drain some amount of energy. 
Each round energy regenerates by the amount of the creature's `energy_regen`.

Creatures use whatever abilities they have, then they end their turn and it's passed to the next creature in qeue.

Most things are calculated via dice rolls. 

Attacks differ in their effectivity against different enemies thanks to the tags system.
For example you are more likely to cause `knockdown` to a an armored enemy because of the `armor` tag.  


## Formulas
Here you can see how different things are counted.

Health:
```
max_health = vitality*10 + vitality*self.level*4
```

Energy formulas:
```
max_energy = dexterity + int(level / 10)
energy_regen = clamp(int(dexterity / 3) + int(level / 10), 2, 10)
```

Damage differs from ability to ability, but the main formula is:
```
damage =  weapon_dmg * strength - defence
```
Damage can never be lower than `strength/2`.

Chance to hit:
```
chance_to_hit = accuracy - evasion
```
Can never be lower than 5 or higher than 95.

Critical effects chances differ from ability to ability, so see ability classes in `abilities.py`.

## Derived stats
Derived stats are not stored, they are calculated on demand. Usually because they are randomized.

Accuracy is calculated on the go every time it's needed, so just see the method `get_accuracy` of `Creature` in `creatures.py`.
The basic formula:
```
base_accuracy = diceroll( str(2*intelligence) + "d" + str(2*dexterity") )
accuracy = base_accuracy + weapon_accuracy + sum_of_equipment_accuracy + sum_of_modifier_accuracy + sum_of_perks_accuracy
```

Defence, see `defence` property of `Creature`:
```
base_defence = diceroll("1d1")
defence = base_defence +  sum_of_equipment_defence + sum_of_modifier_defence + sum_of_perks_defence 
```

Evasion, see `evasion` property of `Creature`:
```
base_evasion = diceroll(str(["dexterity"])+"d6")
evasion = base_evasion +  sum_of_equipment_evasion + sum_of_modifier_evasion + sum_of_perks_evasion 
```