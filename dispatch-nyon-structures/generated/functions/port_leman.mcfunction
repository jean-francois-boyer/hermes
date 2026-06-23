# === PORT DU LAC LEMAN ===
# Plan d'eau, quai/promenade en pierre, petit port avec jetees
# Zone lac decalee au sud (origine 0 64 40)
# Grande etendue d'eau — decoupee en tranches pour respecter la limite Bedrock (~32768)
fill -10 60 40 80 60 100 water
fill -10 61 40 80 61 100 water
fill -10 62 40 80 62 100 water
fill -10 63 40 80 63 100 water
# Lit du lac en pierre
fill -10 59 40 80 59 100 stone
# Quai / promenade en pierre le long de la rive nord
fill -10 63 36 80 63 39 stonebrick
fill -10 64 36 80 64 36 cobblestone
# Lampadaires de la promenade
fill 0 64 38 0 67 38 cobblestone
setblock 0 68 38 glowstone
fill 10 64 38 10 67 38 cobblestone
setblock 10 68 38 glowstone
fill 20 64 38 20 67 38 cobblestone
setblock 20 68 38 glowstone
fill 30 64 38 30 67 38 cobblestone
setblock 30 68 38 glowstone
fill 40 64 38 40 67 38 cobblestone
setblock 40 68 38 glowstone
fill 50 64 38 50 67 38 cobblestone
setblock 50 68 38 glowstone
fill 60 64 38 60 67 38 cobblestone
setblock 60 68 38 glowstone
fill 70 64 38 70 67 38 cobblestone
setblock 70 68 38 glowstone
# Jetee 1 en bois de sapin + pilotis
fill 20 63 40 21 63 58 planks spruce
fill 20 61 40 20 63 40 log spruce
fill 20 61 43 20 63 43 log spruce
fill 20 61 46 20 63 46 log spruce
fill 20 61 49 20 63 49 log spruce
fill 20 61 52 20 63 52 log spruce
fill 20 61 55 20 63 55 log spruce
fill 20 61 58 20 63 58 log spruce
# Jetee 2 en bois de sapin + pilotis
fill 50 63 40 51 63 58 planks spruce
fill 50 61 40 50 63 40 log spruce
fill 50 61 43 50 63 43 log spruce
fill 50 61 46 50 63 46 log spruce
fill 50 61 49 50 63 49 log spruce
fill 50 61 52 50 63 52 log spruce
fill 50 61 55 50 63 55 log spruce
fill 50 61 58 50 63 58 log spruce
# Brise-lames / cale en pierre formant le bassin du port
fill 35 63 40 35 64 62 stonebrick
# Barques (cadres en bois flottant)
fill 25 63 48 27 63 52 planks 5
fill 40 63 46 42 63 50 planks 5
