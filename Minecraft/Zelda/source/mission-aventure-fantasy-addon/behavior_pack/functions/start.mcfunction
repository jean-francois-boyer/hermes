setworldspawn 0 70 0
gamerule keepinventory true
gamerule mobgriefing false
scoreboard objectives add quete dummy Quêtes
scoreboard players set @a quete 0
title @a title Bienvenue dans Le Royaume des Blocs Oubliés
give @a bread 16
give @a torch 32
tellraw @a {"rawtext":[{"text":"Quête 1: Bienvenue au village"}]}
tellraw @a {"rawtext":[{"text":"Quête 2: La ressource manquante"}]}
tellraw @a {"rawtext":[{"text":"Quête 3: Le secret de la forêt"}]}
tellraw @a {"rawtext":[{"text":"Quête 4: Le marché du port"}]}
tellraw @a {"rawtext":[{"text":"Quête 5: Le boss du château"}]}
