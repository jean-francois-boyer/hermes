# Structure: Donjon Demo
# Module: spawn
# Commands: fill setblock summon chest function
# Origine: 100 60 100
say Construction spawn - Donjon Demo
fill 92 59 92 108 59 108 deepslate_tiles
fill 91 60 91 109 60 109 air
fill 93 60 93 107 60 107 air
fill 90 60 90 110 60 90 iron_bars
fill 90 60 110 110 60 110 iron_bars
fill 90 60 90 90 60 110 iron_bars
fill 110 60 90 110 60 110 iron_bars
setblock 100 60 100 bell
setblock 96 60 96 soul_lantern
setblock 104 60 96 soul_lantern
setblock 96 60 104 soul_lantern
setblock 104 60 104 soul_lantern
setblock 100 60 92 standing_sign ["Bienvenue", "Agent Minecraft"]
setworldspawn 100 60 100
title @a title Bienvenue dans Donjon Demo
