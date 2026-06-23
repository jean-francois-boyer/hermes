# Structure: Donjon Demo
# Module: dungeon
# Commands: fill setblock summon chest function
# Origine: 100 60 100
say Construction dungeon - Donjon Demo
fill 88 58 118 112 58 142 deepslate_tiles
fill 88 59 118 112 65 142 cracked_deepslate_bricks
fill 90 59 120 110 64 140 air
fill 88 66 118 112 66 142 blackstone
fill 99 59 118 101 63 118 air
setblock 100 59 121 stone_pressure_plate
setblock 100 58 122 tnt
setblock 92 59 125 spawner
setblock 108 59 125 spawner
summon zombie 94 59 130
summon skeleton 106 59 130
summon zombie 100 59 137
setblock 100 59 140 chest
tellraw @a {"rawtext":[{"text":"Donjon Donjon Demo: coffre récompense placé."}]}
