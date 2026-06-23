# Structure: Donjon Demo
# Module: market
# Commands: fill setblock summon chest function
# Origine: 100 60 100
say Construction market - Donjon Demo
fill 112 59 94 126 59 106 cobbled_deepslate
fill 114 60 96 118 60 100 barrel
fill 120 60 96 124 60 100 barrel
fill 114 61 96 118 61 100 red_wool
fill 120 61 96 124 61 100 blue_wool
setblock 116 60 103 standing_sign ["Marché", "Émeraudes"]
summon villager 116 61 98
summon villager 122 61 98
