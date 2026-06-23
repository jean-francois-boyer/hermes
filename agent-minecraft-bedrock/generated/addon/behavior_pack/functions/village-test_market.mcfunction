# Structure: Village Test
# Module: market
# Commands: fill setblock summon chest function
# Origine: 0 70 0
say Construction market - Village Test
fill 12 69 -6 26 69 6 cobbled_deepslate
fill 14 70 -4 18 70 0 barrel
fill 20 70 -4 24 70 0 barrel
fill 14 71 -4 18 71 0 red_wool
fill 20 71 -4 24 71 0 blue_wool
setblock 16 70 3 standing_sign ["Marché", "Émeraudes"]
summon villager 16 71 -2
summon villager 22 71 -2
