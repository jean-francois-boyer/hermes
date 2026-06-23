# Structure: Mont Volcan
# Module: dungeon
# Commands: fill setblock summon chest function
# Origine: 0 80 -240
say Construction dungeon - Mont Volcan
fill -12 78 -222 12 78 -198 deepslate_tiles
fill -12 79 -222 12 85 -198 cracked_deepslate_bricks
fill -10 79 -220 10 84 -200 air
fill -12 86 -222 12 86 -198 blackstone
fill -1 79 -222 1 83 -222 air
setblock 0 79 -219 stone_pressure_plate
setblock 0 78 -218 tnt
setblock -8 79 -215 spawner
setblock 8 79 -215 spawner
summon zombie -6 79 -210
summon skeleton 6 79 -210
summon zombie 0 79 -203
setblock 0 79 -200 chest
tellraw @a {"rawtext":[{"text":"Donjon Mont Volcan: coffre récompense placé."}]}
