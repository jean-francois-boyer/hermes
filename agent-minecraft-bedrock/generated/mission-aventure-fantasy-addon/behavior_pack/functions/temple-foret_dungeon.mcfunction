# Structure: Temple Foret
# Module: dungeon
# Commands: fill setblock summon chest function
# Origine: 220 70 0
say Construction dungeon - Temple Foret
fill 208 68 18 232 68 42 deepslate_tiles
fill 208 69 18 232 75 42 cracked_deepslate_bricks
fill 210 69 20 230 74 40 air
fill 208 76 18 232 76 42 blackstone
fill 219 69 18 221 73 18 air
setblock 220 69 21 stone_pressure_plate
setblock 220 68 22 tnt
setblock 212 69 25 spawner
setblock 228 69 25 spawner
summon zombie 214 69 30
summon skeleton 226 69 30
summon zombie 220 69 37
setblock 220 69 40 chest
tellraw @a {"rawtext":[{"text":"Donjon Temple Foret: coffre récompense placé."}]}
