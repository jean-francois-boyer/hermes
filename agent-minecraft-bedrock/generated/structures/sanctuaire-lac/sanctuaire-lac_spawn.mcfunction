# Structure: Sanctuaire Lac
# Module: spawn
# Commands: fill setblock summon chest function
# Origine: -220 68 0
say Construction spawn - Sanctuaire Lac
fill -228 67 -8 -212 67 8 stone_bricks
fill -229 68 -9 -211 68 9 air
fill -227 68 -7 -213 68 7 air
fill -230 68 -10 -210 68 -10 oak_fence
fill -230 68 10 -210 68 10 oak_fence
fill -230 68 -10 -230 68 10 oak_fence
fill -210 68 -10 -210 68 10 oak_fence
setblock -220 68 0 bell
setblock -224 68 -4 lantern
setblock -216 68 -4 lantern
setblock -224 68 4 lantern
setblock -216 68 4 lantern
setblock -220 68 -8 standing_sign ["Bienvenue", "Agent Minecraft"]
setworldspawn -220 68 0
title @a title Bienvenue dans Sanctuaire Lac
