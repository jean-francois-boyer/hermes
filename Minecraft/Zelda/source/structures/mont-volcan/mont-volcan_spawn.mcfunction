# Structure: Mont Volcan
# Module: spawn
# Commands: fill setblock summon chest function
# Origine: 0 80 -240
say Construction spawn - Mont Volcan
fill -8 79 -248 8 79 -232 deepslate_tiles
fill -9 80 -249 9 80 -231 air
fill -7 80 -247 7 80 -233 air
fill -10 80 -250 10 80 -250 iron_bars
fill -10 80 -230 10 80 -230 iron_bars
fill -10 80 -250 -10 80 -230 iron_bars
fill 10 80 -250 10 80 -230 iron_bars
setblock 0 80 -240 bell
setblock -4 80 -244 soul_lantern
setblock 4 80 -244 soul_lantern
setblock -4 80 -236 soul_lantern
setblock 4 80 -236 soul_lantern
setblock 0 80 -248 standing_sign ["Bienvenue", "Agent Minecraft"]
setworldspawn 0 80 -240
title @a title Bienvenue dans Mont Volcan
