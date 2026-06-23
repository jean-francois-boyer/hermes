# Nyon Reborn — Blueprint Minecraft Bedrock

Reconstruction fidele de la ville de **Nyon** (Vaud, Suisse, Lac Leman).
Edition cible : **Minecraft Bedrock** (Nintendo Switch via Realms). Pas Java.

> Reconstruction originale inspiree de la vraie ville — aucun asset copyrighte.

## 1. Identite de la ville

Nyon (latin *Noviodunum*, fondee par les Romains sous Jules Cesar) s'etage entre le Lac Leman en bas et la gare CFF en haut. Ses reperes :
- **Chateau de Nyon** : chateau medieval a **5 tours rondes blanches** sur la colline, dominant le lac.
- **Colonnes romaines** : 3 colonnes reconstruites sur l'**Esplanade des Marronniers** (vestiges de Noviodunum).
- **Lac Leman / Rive** : port de plaisance, promenade lacustre.
- **Vieille ville** : ruelles etroites, place du Marche.
- **Gare** : en amont, au nord de la ville.

## 2. Parametres du monde

- Nom du monde : **Nyon Reborn**
- Spawn : `0 72 0` (Esplanade des Marronniers, pres des colonnes)
- Mode conseille : Creatif pour la construction, Aventure pour la visite/quetes
- Plat ou personnalise avec une grande etendue d'eau au sud-est pour le Leman

## 3. Zones & palette de blocs

### Chateau de Nyon
Chateau medieval sur la colline, 5 tours rondes blanches dominant le lac. Toits coniques sombres. Musee historique.
- Centre approx. : `-40 80 -30`
- Palette : white_concrete, quartz_block, polished_diorite, dark_oak_planks (toits), spruce_stairs (charpente)

### Esplanade des Marronniers / Colonnes romaines
Terrasse plantee de marronniers avec 3 colonnes romaines reconstruites (vestige de Noviodunum), vue panoramique.
- Centre approx. : `0 72 0`
- Palette : sandstone, smooth_sandstone, cut_sandstone, chiseled_sandstone (colonnes), grass_block, oak_leaves

### Port & Rive (Lac Leman)
Front de lac : port de plaisance, jetees, promenade de la Rive, bateaux CGN, eau bleue du Leman.
- Centre approx. : `60 64 40`
- Palette : blue_concrete, water, stone_bricks (quais), smooth_stone, oak_planks (pontons)

### Vieille ville
Ruelles etroites, maisons serrees, place du Marche, fontaines, toits de tuiles, heritage medieval.
- Centre approx. : `-10 74 20`
- Palette : stone_bricks, cobblestone, mossy_stone_bricks, brick_block (toits), spruce_planks, lantern

### Gare de Nyon
Gare CFF en hauteur (cote nord, en amont), voies, quais, depart des trains vers Geneve et Lausanne.
- Centre approx. : `-30 78 -80`
- Palette : light_gray_concrete, iron_block, stone, rail, glass, smooth_stone_slab

## 4. Checklist de construction

- [ ] Aplanir/poser le terrain en pente (lac au sud-est, gare au nord)
- [ ] Creuser et remplir le bassin du Lac Leman (eau bleue)
- [ ] Batir les quais du port et la promenade de la Rive
- [ ] Elever le Chateau : donjon + **5 tours rondes blanches** a toits coniques
- [ ] Tracer l'Esplanade des Marronniers et dresser les **3 colonnes romaines** (sandstone)
- [ ] Construire la vieille ville : ruelles etroites, place du Marche, fontaines
- [ ] Poser la gare CFF en hauteur + voies ferrees
- [ ] Relier les zones par escaliers/rues (la ville est en pente)
- [ ] Planter marronniers et vegetation lacustre
- [ ] Installer les panneaux/PNJ de quetes

## 5. Commandes Bedrock utiles

```mcfunction
## Spawn & regles
setworldspawn 0 72 0
gamerule doDaylightCycle false
gamerule doWeatherCycle false
gamerule keepInventory true
gamerule showcoordinates true
time set day

## Exemple : bassin du Leman (eau)
fill 40 60 20 90 63 70 water

## Exemple : base d'une tour blanche du chateau
fill -45 80 -35 -41 95 -31 white_concrete hollow

## Exemple : poser une colonne romaine
setblock 0 72 0 chiseled_sandstone
fill 0 72 0 0 78 0 chiseled_sandstone

## Teleportation vers le chateau
tp @s -40 81 -30

## Titre de bienvenue
title @a title Nyon Reborn
titleraw @a subtitle {"rawtext":[{"text":"Bienvenue a Nyon"}]}

## Message dans le chat
tellraw @a {"rawtext":[{"text":"Explore la vieille ville !"}]}
```

## 6. Quetes de decouverte

- **1. Les Colonnes de Noviodunum** — Rejoins les 3 colonnes romaines de l'Esplanade des Marronniers. (`/tp @s 0 72 0`)
- **2. Les Cinq Tours Blanches** — Monte au Chateau de Nyon et fais le tour de ses 5 tours rondes. (`/tp @s -40 81 -30`)
- **3. La Rive du Leman** — Descends au port, marche sur la promenade de la Rive. (`/tp @s 60 65 40`)
- **4. Ruelles de la Vieille Ville** — Perds-toi dans les ruelles etroites jusqu'a la place du Marche. (`/tp @s -10 75 20`)

## 7. Import sur Nintendo Switch via Realms

1. Construis/teste le monde sur Minecraft Bedrock (PC/mobile) avec l'add-on active.
2. Cree un **Realms** (abonnement Minecraft Realms Plus).
3. Dans le menu Realms, choisis **Remplacer le monde** et televerse ce monde Bedrock.
4. Sur la **Switch**, connecte-toi au meme compte Microsoft.
5. Ouvre Minecraft -> onglet **Realms** -> rejoins *Nyon Reborn*.
6. Pour l'add-on : applique le behavior_pack au monde AVANT le televersement (Parametres -> Packs de comportement).
7. Lance `/function start` une fois en jeu pour fixer spawn + regles, puis `/function quests` pour la visite.

## 8. Structure de l'add-on genere

```
generated/addon/behavior_pack/
  manifest.json
  functions/start.mcfunction
  functions/quests.mcfunction
```
