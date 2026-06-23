# start.mcfunction — Nyon Reborn
# Fixe le spawn, les regles et affiche le titre de bienvenue.
setworldspawn 0 72 0
gamerule doDaylightCycle false
gamerule doWeatherCycle false
gamerule keepInventory true
gamerule showcoordinates true
gamerule commandblockoutput false
time set day
weather clear
title @a title Nyon Reborn
titleraw @a subtitle {"rawtext":[{"text":"Bienvenue dans la ville de Nyon"}]}
tellraw @a {"rawtext":[{"text":"Tape /function quests pour la visite des landmarks."}]}
