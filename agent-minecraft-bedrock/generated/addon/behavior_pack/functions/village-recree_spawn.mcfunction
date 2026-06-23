# Structure: Village Recree
# Module: spawn
# Commands: fill setblock summon chest function
# Origine: 0 70 0
say Construction spawn - Village Recree
fill -8 69 -8 8 69 8 deepslate_tiles
fill -9 70 -9 9 70 9 air
fill -7 70 -7 7 70 7 air
fill -10 70 -10 10 70 -10 iron_bars
fill -10 70 10 10 70 10 iron_bars
fill -10 70 -10 -10 70 10 iron_bars
fill 10 70 -10 10 70 10 iron_bars
setblock 0 70 0 bell
setblock -4 70 -4 soul_lantern
setblock 4 70 -4 soul_lantern
setblock -4 70 4 soul_lantern
setblock 4 70 4 soul_lantern
setblock 0 70 -8 standing_sign ["Bienvenue", "Agent Minecraft"]
setworldspawn 0 70 0
title @a title Bienvenue dans Village Recree
