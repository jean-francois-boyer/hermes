# Blueprint de monde Minecraft Bedrock — Les Îles du Port d’Émeraude

Généré le : 2026-06-20 17:22

> Agent local basé sur `agent_prompt.md`, `world_brief_template.md` et `output_format.md` du workspace.

## 1. Concept du monde

- Nom du monde : **Les Îles du Port d’Émeraude**
- Genre : Aventure RPG médiéval-fantasy
- Résumé : Exemple de demande Crée un monde Minecraft Bedrock compatible Switch via Realm. Je veux un village médiéval fantasy avec : - une zone de spawn dans une petite place de village - un château en ruine au nord - une forêt magique à l’ouest - une mine abandonnée au sud - un port marchand à l’est - 5 PNJ avec dialogues - 5 quêtes principales - 2 donjons - une économie avec émeraudes - des commandes Bedrock simples - une checklist pour construire le monde Le monde doit être jouable en solo ou à 2 joueurs, sans mods Java, avec command blocks autorisés.
- Objectif principal : explorer les zones, terminer les quêtes, vaincre le défi final et préparer le monde pour un Realm jouable sur Switch.
- Durée estimée : 1 à 3 heures selon la construction
- Nombre de joueurs : Solo
- Public : Famille / YouTube / aventure accessible

## 2. Paramètres Minecraft Bedrock

- Mode recommandé : Survie préparée avec commandes de setup
- Difficulté : Normale
- Coordonnée du spawn : `0 70 0`
- Command blocks : activés
- Keep inventory : oui
- Mob griefing : non
- Accès Switch : via Minecraft Realms

## 3. Carte textuelle

- Centre : Spawn + place de départ + panneau des quêtes
- Nord : Zone de combat / donjon principal
- Sud : Zone ressources / mine / survie
- Est : Commerce / port / marché
- Ouest : Exploration / forêt / énigmes
- Sous-sol : salle finale ou coffre secret

## 4. Zones

### Zone 1 — Ville de départ sécurisée
- Coordonnées approximatives : `0 70 0`
- Taille conseillée : 60x60 blocs minimum
- Biome conseillé : plaines, forêt ou biome proche du thème
- Matériaux : bois, pierre, lanternes, barrières, panneaux, coffres
- Fonction gameplay : progression, exploration, combat ou commerce
- Secret : coffre caché avec émeraudes + indice vers la zone suivante
### Zone 2 — Château en ruine au nord
- Coordonnées approximatives : `0 78 -220`
- Taille conseillée : 60x60 blocs minimum
- Biome conseillé : plaines, forêt ou biome proche du thème
- Matériaux : bois, pierre, lanternes, barrières, panneaux, coffres
- Fonction gameplay : progression, exploration, combat ou commerce
- Secret : coffre caché avec émeraudes + indice vers la zone suivante
### Zone 3 — Forêt magique à l’ouest
- Coordonnées approximatives : `-220 70 0`
- Taille conseillée : 60x60 blocs minimum
- Biome conseillé : plaines, forêt ou biome proche du thème
- Matériaux : bois, pierre, lanternes, barrières, panneaux, coffres
- Fonction gameplay : progression, exploration, combat ou commerce
- Secret : coffre caché avec émeraudes + indice vers la zone suivante
### Zone 4 — Mine abandonnée au sud
- Coordonnées approximatives : `0 54 220`
- Taille conseillée : 60x60 blocs minimum
- Biome conseillé : plaines, forêt ou biome proche du thème
- Matériaux : bois, pierre, lanternes, barrières, panneaux, coffres
- Fonction gameplay : progression, exploration, combat ou commerce
- Secret : coffre caché avec émeraudes + indice vers la zone suivante
### Zone 5 — Port marchand à l’est
- Coordonnées approximatives : `220 64 0`
- Taille conseillée : 60x60 blocs minimum
- Biome conseillé : plaines, forêt ou biome proche du thème
- Matériaux : bois, pierre, lanternes, barrières, panneaux, coffres
- Fonction gameplay : progression, exploration, combat ou commerce
- Secret : coffre caché avec émeraudes + indice vers la zone suivante

## 5. Spawn

- Description : place centrale sécurisée, claire, avec panneaux et coffres de départ.
- Construction : plateforme 25x25, fontaine centrale, panneau « règles », panneau « quêtes ».
- Message de bienvenue : `Bienvenue dans Les Îles du Port d’Émeraude`
- Commandes de base : voir section 10.

## 6. PNJ

### Maire
- Rôle : PNJ de progression
- Apparence suggérée : villageois nommé ou NPC Bedrock si disponible
- Position : `4 70 4`
- Dialogue : « Bienvenue aventurier ! Ta prochaine mission : Bienvenue au village. »
- Quête associée : Bienvenue au village
### Forgeronne
- Rôle : PNJ de progression
- Apparence suggérée : villageois nommé ou NPC Bedrock si disponible
- Position : `4 78 -216`
- Dialogue : « Bienvenue aventurier ! Ta prochaine mission : La ressource manquante. »
- Quête associée : La ressource manquante
### Cartographe
- Rôle : PNJ de progression
- Apparence suggérée : villageois nommé ou NPC Bedrock si disponible
- Position : `-216 70 4`
- Dialogue : « Bienvenue aventurier ! Ta prochaine mission : Le secret de la forêt. »
- Quête associée : Le secret de la forêt
### Marchande
- Rôle : PNJ de progression
- Apparence suggérée : villageois nommé ou NPC Bedrock si disponible
- Position : `4 54 224`
- Dialogue : « Bienvenue aventurier ! Ta prochaine mission : Le marché du port. »
- Quête associée : Le marché du port
### Gardien
- Rôle : PNJ de progression
- Apparence suggérée : villageois nommé ou NPC Bedrock si disponible
- Position : `224 64 4`
- Dialogue : « Bienvenue aventurier ! Ta prochaine mission : Le boss du château. »
- Quête associée : Le boss du château

## 7. Quêtes

### Quête 1 — Bienvenue au village
- Donneur de quête : Maire
- Objectif : terminer l’objectif de la zone 1
- Étapes :
  1. Lire le panneau de quête.
  2. Aller à la coordonnée indiquée.
  3. Récupérer l’objet/preuve dans un coffre.
  4. Revenir au PNJ ou au panneau central.
- Récompense : 16 pains + 16 torches
- Commandes utiles : `/scoreboard players set @p quete 1`
### Quête 2 — La ressource manquante
- Donneur de quête : Forgeronne
- Objectif : terminer l’objectif de la zone 2
- Étapes :
  1. Lire le panneau de quête.
  2. Aller à la coordonnée indiquée.
  3. Récupérer l’objet/preuve dans un coffre.
  4. Revenir au PNJ ou au panneau central.
- Récompense : épée en fer
- Commandes utiles : `/scoreboard players set @p quete 2`
### Quête 3 — Le secret de la forêt
- Donneur de quête : Cartographe
- Objectif : terminer l’objectif de la zone 3
- Étapes :
  1. Lire le panneau de quête.
  2. Aller à la coordonnée indiquée.
  3. Récupérer l’objet/preuve dans un coffre.
  4. Revenir au PNJ ou au panneau central.
- Récompense : potion de soin
- Commandes utiles : `/scoreboard players set @p quete 3`
### Quête 4 — Le marché du port
- Donneur de quête : Marchande
- Objectif : terminer l’objectif de la zone 4
- Étapes :
  1. Lire le panneau de quête.
  2. Aller à la coordonnée indiquée.
  3. Récupérer l’objet/preuve dans un coffre.
  4. Revenir au PNJ ou au panneau central.
- Récompense : 8 émeraudes
- Commandes utiles : `/scoreboard players set @p quete 4`
### Quête 5 — Le boss du château
- Donneur de quête : Gardien
- Objectif : terminer l’objectif de la zone 5
- Étapes :
  1. Lire le panneau de quête.
  2. Aller à la coordonnée indiquée.
  3. Récupérer l’objet/preuve dans un coffre.
  4. Revenir au PNJ ou au panneau central.
- Récompense : arc + 32 flèches
- Commandes utiles : `/scoreboard players set @p quete 5`

## 8. Donjons et défis

### Donjon 1 — Le défi de la zone nord
- Thème : ruines, couloirs, pièges simples
- Entrée : proche de `0 78 -220`
- Salles : entrée, salle mobs, salle coffre, salle mini-boss
- Ennemis : zombies, squelettes, pillards, araignées
- Boss : entité nommée avec équipement amélioré
- Récompense : clé finale / diamant / émeraudes

### Donjon 2 — La salle secrète
- Thème : sous-sol caché sous le spawn
- Entrée : trappe ou escalier à `0 65 0`
- Salles : énigme de leviers + coffre final
- Récompense : trophée symbolique et message de fin

## 9. Économie

- Monnaie : émeraudes
- Boutiques : nourriture, armes, potions, cartes, indices
- Prix conseillés :
  - Pain x8 : 1 émeraude
  - Torches x16 : 1 émeraude
  - Épée en fer : 5 émeraudes
  - Potion de soin : 4 émeraudes
  - Indice secret : 3 émeraudes

## 10. Commandes Bedrock

```mcfunction
setworldspawn 0 70 0
gamerule keepinventory true
gamerule mobgriefing false
scoreboard objectives add quete dummy Quêtes
scoreboard players set @a quete 0
title @a title Bienvenue dans Les Îles du Port d’Émeraude
give @a bread 16
give @a torch 32
tellraw @a {"rawtext":[{"text":"Quête 1: Bienvenue au village"}]}
tellraw @a {"rawtext":[{"text":"Quête 2: La ressource manquante"}]}
tellraw @a {"rawtext":[{"text":"Quête 3: Le secret de la forêt"}]}
tellraw @a {"rawtext":[{"text":"Quête 4: Le marché du port"}]}
tellraw @a {"rawtext":[{"text":"Quête 5: Le boss du château"}]}
```

## 11. Add-on Bedrock optionnel

Un add-on de base est généré dans `generated/addon/` avec un behavior pack et des fonctions `.mcfunction`.

Fichiers générés utiles :
- `generated/addon/behavior_pack/functions/start.mcfunction`
- `generated/addon/behavior_pack/functions/quests.mcfunction`
- `generated/les-iles-du-port-demeraude.mcaddon`

## 12. Checklist de construction

- [ ] Créer un monde Bedrock sur PC/mobile.
- [ ] Activer cheats + command blocks.
- [ ] Exécuter les commandes de `start.mcfunction` ou les recopier dans le chat/command blocks.
- [ ] Construire le spawn.
- [ ] Construire chaque zone aux coordonnées proposées.
- [ ] Placer panneaux, coffres, récompenses et PNJ.
- [ ] Tester chaque quête dans l’ordre.
- [ ] Préparer l’upload Realm.

## 13. Test Bedrock

- Tester sur PC/mobile Bedrock avant la Switch.
- Vérifier que les commandes Bedrock sont acceptées.
- Vérifier le spawn, les règles, les coffres et la progression scoreboard.
- Vérifier que le monde reste jouable sans ressource pack spécial si tu veux une compatibilité maximale.

## 14. Mise sur Realm pour Switch

1. Ouvrir Minecraft Bedrock sur PC/mobile.
2. Importer ou ouvrir le monde.
3. Aller dans Realms.
4. Remplacer le monde du Realm par ce monde.
5. Ouvrir Minecraft sur Switch.
6. Se connecter au même compte Microsoft/Xbox.
7. Rejoindre le Realm depuis l’onglet Amis / Realms.
