# Structure: Village Kokiri Original
# Module: dungeon
# Commands: fill setblock summon chest function
# Origine: 0 70 0
say Construction dungeon - Village Kokiri Original
fill -12 68 18 12 68 42 deepslate_tiles
fill -12 69 18 12 75 42 cracked_deepslate_bricks
fill -10 69 20 10 74 40 air
fill -12 76 18 12 76 42 blackstone
fill -1 69 18 1 73 18 air
setblock 0 69 21 stone_pressure_plate
setblock 0 68 22 tnt
setblock -8 69 25 spawner
setblock 8 69 25 spawner
summon zombie -6 69 30
summon skeleton 6 69 30
summon zombie 0 69 37
setblock 0 69 40 chest
tellraw @a {"rawtext":[{"text":"Donjon Village Kokiri Original: coffre récompense placé."}]}
