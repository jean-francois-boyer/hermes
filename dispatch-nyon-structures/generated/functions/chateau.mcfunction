# === CHATEAU DE NYON ===
# Donjon rectangulaire blanc + 5 tours rondes blanches + cour interieure
# Origine 0 64 0 — cible Minecraft BEDROCK
# Socle / terrasse en pierre taillee
fill -2 63 -2 34 63 26 stonebrick
# Murs exterieurs (beton blanc) — coques creuses pour menager la cour
fill 0 64 0 32 76 1 concrete white
fill 0 64 23 32 76 24 concrete white
fill 0 64 0 1 76 24 concrete white
fill 31 64 0 32 76 24 concrete white
# Cour interieure : pavage + evidement
fill 2 63 2 30 63 22 cobblestone
fill 2 64 2 30 76 22 air
# Creneaux du chemin de ronde
fill 0 77 0 32 77 0 concrete white outline
fill 0 77 24 32 77 24 concrete white outline
fill 0 77 0 0 77 24 concrete white outline
fill 32 77 0 32 77 24 concrete white outline
# Porche d'entree au sud
fill 14 64 23 18 68 24 air
# --- TOUR RONDE NORD-OUEST (centre 0,0) r=4 h=16 (anneaux empiles via fill hollow) ---
fill -4 64 -4 4 79 4 concrete white hollow
setblock -3 64 -3 air
setblock 3 64 -3 air
setblock -3 64 3 air
setblock 3 64 3 air
# couronne + toit conique quartz
fill -3 80 -3 3 80 3 quartz_block
fill -2 81 -2 2 81 2 quartz_block
fill -1 82 -1 1 82 1 quartz_block
setblock 0 83 0 quartz_block
# --- TOUR RONDE NORD-EST (centre 32,0) ---
fill 28 64 -4 36 79 4 concrete white hollow
fill 29 80 -3 35 80 3 quartz_block
fill 30 81 -2 34 81 2 quartz_block
fill 31 82 -1 33 82 1 quartz_block
setblock 32 83 0 quartz_block
# --- TOUR RONDE SUD-OUEST (centre 0,24) ---
fill -4 64 20 4 79 28 concrete white hollow
fill -3 80 21 3 80 27 quartz_block
fill -2 81 22 2 81 26 quartz_block
fill -1 82 23 1 82 25 quartz_block
setblock 0 83 24 quartz_block
# --- TOUR RONDE SUD-EST (centre 32,24) ---
fill 28 64 20 36 79 28 concrete white hollow
fill 29 80 21 35 80 27 quartz_block
fill 30 81 22 34 81 26 quartz_block
fill 31 82 23 33 82 25 quartz_block
setblock 32 83 24 quartz_block
# --- TOUR MAITRESSE CENTRALE (centre 16,12) r=5 h=22, plus haute ---
fill 11 64 7 21 85 17 concrete white hollow
setblock 11 64 7 air
setblock 21 64 7 air
setblock 11 64 17 air
setblock 21 64 17 air
fill 12 86 8 20 86 16 quartz_block
fill 13 87 9 19 87 15 quartz_block
fill 14 88 10 18 88 14 quartz_block
fill 15 89 11 17 89 13 quartz_block
setblock 16 90 12 quartz_block
# Drapeau (point lumineux) au faite de la tour maitresse
setblock 16 92 12 glowstone
# Fenetres en verre
setblock 0 68 4 glass
setblock 32 68 4 glass
setblock 0 68 8 glass
setblock 32 68 8 glass
setblock 0 68 12 glass
setblock 32 68 12 glass
setblock 0 68 16 glass
setblock 32 68 16 glass
setblock 0 68 20 glass
setblock 32 68 20 glass
# Torches de la cour
setblock 4 65 4 torch
setblock 28 65 20 torch
