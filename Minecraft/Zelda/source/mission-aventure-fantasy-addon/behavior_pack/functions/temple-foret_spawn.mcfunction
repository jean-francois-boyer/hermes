# Structure: Temple Foret
# Module: spawn
# Commands: fill setblock summon chest function
# Origine: 220 70 0
say Construction spawn - Temple Foret
fill 212 69 -8 228 69 8 deepslate_tiles
fill 211 70 -9 229 70 9 air
fill 213 70 -7 227 70 7 air
fill 210 70 -10 230 70 -10 iron_bars
fill 210 70 10 230 70 10 iron_bars
fill 210 70 -10 210 70 10 iron_bars
fill 230 70 -10 230 70 10 iron_bars
setblock 220 70 0 bell
setblock 216 70 -4 soul_lantern
setblock 224 70 -4 soul_lantern
setblock 216 70 4 soul_lantern
setblock 224 70 4 soul_lantern
setblock 220 70 -8 standing_sign ["Bienvenue", "Agent Minecraft"]
setworldspawn 220 70 0
title @a title Bienvenue dans Temple Foret
