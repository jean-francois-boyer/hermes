# Structure: Sanctuaire Lac
# Module: dungeon
# Commands: fill setblock summon chest function
# Origine: -220 68 0
say Construction dungeon - Sanctuaire Lac
fill -232 66 18 -208 66 42 stone_bricks
fill -232 67 18 -208 73 42 oak_planks
fill -230 67 20 -210 72 40 air
fill -232 74 18 -208 74 42 spruce_stairs
fill -221 67 18 -219 71 18 air
setblock -220 67 21 stone_pressure_plate
setblock -220 66 22 tnt
setblock -228 67 25 spawner
setblock -212 67 25 spawner
summon zombie -226 67 30
summon skeleton -214 67 30
summon zombie -220 67 37
setblock -220 67 40 chest
tellraw @a {"rawtext":[{"text":"Donjon Sanctuaire Lac: coffre récompense placé."}]}
