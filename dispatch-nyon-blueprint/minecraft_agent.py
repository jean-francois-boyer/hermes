#!/usr/bin/env python3
"""
minecraft_agent.py — Generateur de blueprint Minecraft BEDROCK pour
reconstruire la ville de NYON (Vaud, Suisse, Lac Leman).

Stdlib uniquement. Produit :
  - world_blueprint.md (plan complet du monde)
  - generated/addon/behavior_pack/  (add-on de base Bedrock)
      manifest.json (UUID uuid4 frais)
      functions/start.mcfunction
      functions/quests.mcfunction

Cible : Minecraft Bedrock (Nintendo Switch via Realms). PAS Java.
Aucun asset copyrighte — reconstruction originale et fidele a la vraie ville.

Usage : python3 minecraft_agent.py
"""

import json
import os
import uuid

# --------------------------------------------------------------------------
# Donnees du monde — identite fidele de Nyon
# --------------------------------------------------------------------------

WORLD_NAME = "Nyon Reborn"
SPAWN = (0, 72, 0)  # Esplanade des Marronniers, pres des Colonnes romaines

ZONES = [
    {
        "id": "chateau",
        "nom": "Chateau de Nyon",
        "desc": "Chateau medieval sur la colline, 5 tours rondes blanches "
                "dominant le lac. Toits coniques sombres. Musee historique.",
        "centre": (-40, 80, -30),
        "palette": ["white_concrete", "quartz_block", "polished_diorite",
                    "dark_oak_planks (toits)", "spruce_stairs (charpente)"],
    },
    {
        "id": "esplanade",
        "nom": "Esplanade des Marronniers / Colonnes romaines",
        "desc": "Terrasse plantee de marronniers avec 3 colonnes romaines "
                "reconstruites (vestige de Noviodunum), vue panoramique.",
        "centre": (0, 72, 0),
        "palette": ["sandstone", "smooth_sandstone", "cut_sandstone",
                    "chiseled_sandstone (colonnes)", "grass_block", "oak_leaves"],
    },
    {
        "id": "port",
        "nom": "Port & Rive (Lac Leman)",
        "desc": "Front de lac : port de plaisance, jetees, promenade de la "
                "Rive, bateaux CGN, eau bleue du Leman.",
        "centre": (60, 64, 40),
        "palette": ["blue_concrete", "water", "stone_bricks (quais)",
                    "smooth_stone", "oak_planks (pontons)"],
    },
    {
        "id": "vieille_ville",
        "nom": "Vieille ville",
        "desc": "Ruelles etroites, maisons serrees, place du Marche, "
                "fontaines, toits de tuiles, heritage medieval.",
        "centre": (-10, 74, 20),
        "palette": ["stone_bricks", "cobblestone", "mossy_stone_bricks",
                    "brick_block (toits)", "spruce_planks", "lantern"],
    },
    {
        "id": "gare",
        "nom": "Gare de Nyon",
        "desc": "Gare CFF en hauteur (cote nord, en amont), voies, quais, "
                "depart des trains vers Geneve et Lausanne.",
        "centre": (-30, 78, -80),
        "palette": ["light_gray_concrete", "iron_block", "stone",
                    "rail", "glass", "smooth_stone_slab"],
    },
]

QUESTS = [
    {
        "titre": "1. Les Colonnes de Noviodunum",
        "but": "Rejoins les 3 colonnes romaines de l'Esplanade des Marronniers.",
        "tp": (0, 72, 0),
    },
    {
        "titre": "2. Les Cinq Tours Blanches",
        "but": "Monte au Chateau de Nyon et fais le tour de ses 5 tours rondes.",
        "tp": (-40, 81, -30),
    },
    {
        "titre": "3. La Rive du Leman",
        "but": "Descends au port, marche sur la promenade de la Rive.",
        "tp": (60, 65, 40),
    },
    {
        "titre": "4. Ruelles de la Vieille Ville",
        "but": "Perds-toi dans les ruelles etroites jusqu'a la place du Marche.",
        "tp": (-10, 75, 20),
    },
]


# --------------------------------------------------------------------------
# Generation du blueprint Markdown
# --------------------------------------------------------------------------

def build_blueprint_md():
    sx, sy, sz = SPAWN
    lines = []
    A = lines.append
    A("# %s — Blueprint Minecraft Bedrock\n" % WORLD_NAME)
    A("Reconstruction fidele de la ville de **Nyon** (Vaud, Suisse, Lac Leman).")
    A("Edition cible : **Minecraft Bedrock** (Nintendo Switch via Realms). "
      "Pas Java.\n")
    A("> Reconstruction originale inspiree de la vraie ville — aucun asset "
      "copyrighte.\n")

    A("## 1. Identite de la ville\n")
    A("Nyon (latin *Noviodunum*, fondee par les Romains sous Jules Cesar) "
      "s'etage entre le Lac Leman en bas et la gare CFF en haut. Ses reperes :")
    A("- **Chateau de Nyon** : chateau medieval a **5 tours rondes blanches** "
      "sur la colline, dominant le lac.")
    A("- **Colonnes romaines** : 3 colonnes reconstruites sur l'**Esplanade "
      "des Marronniers** (vestiges de Noviodunum).")
    A("- **Lac Leman / Rive** : port de plaisance, promenade lacustre.")
    A("- **Vieille ville** : ruelles etroites, place du Marche.")
    A("- **Gare** : en amont, au nord de la ville.\n")

    A("## 2. Parametres du monde\n")
    A("- Nom du monde : **%s**" % WORLD_NAME)
    A("- Spawn : `%d %d %d` (Esplanade des Marronniers, pres des colonnes)"
      % (sx, sy, sz))
    A("- Mode conseille : Creatif pour la construction, Aventure pour la "
      "visite/quetes")
    A("- Plat ou personnalise avec une grande etendue d'eau au sud-est "
      "pour le Leman\n")

    A("## 3. Zones & palette de blocs\n")
    for z in ZONES:
        cx, cy, cz = z["centre"]
        A("### %s" % z["nom"])
        A(z["desc"])
        A("- Centre approx. : `%d %d %d`" % (cx, cy, cz))
        A("- Palette : %s\n" % ", ".join(z["palette"]))

    A("## 4. Checklist de construction\n")
    A("- [ ] Aplanir/poser le terrain en pente (lac au sud-est, gare au nord)")
    A("- [ ] Creuser et remplir le bassin du Lac Leman (eau bleue)")
    A("- [ ] Batir les quais du port et la promenade de la Rive")
    A("- [ ] Elever le Chateau : donjon + **5 tours rondes blanches** a toits "
      "coniques")
    A("- [ ] Tracer l'Esplanade des Marronniers et dresser les **3 colonnes "
      "romaines** (sandstone)")
    A("- [ ] Construire la vieille ville : ruelles etroites, place du Marche, "
      "fontaines")
    A("- [ ] Poser la gare CFF en hauteur + voies ferrees")
    A("- [ ] Relier les zones par escaliers/rues (la ville est en pente)")
    A("- [ ] Planter marronniers et vegetation lacustre")
    A("- [ ] Installer les panneaux/PNJ de quetes\n")

    A("## 5. Commandes Bedrock utiles\n")
    A("```mcfunction")
    A("## Spawn & regles")
    A("setworldspawn %d %d %d" % (sx, sy, sz))
    A("gamerule doDaylightCycle false")
    A("gamerule doWeatherCycle false")
    A("gamerule keepInventory true")
    A("gamerule showcoordinates true")
    A("time set day")
    A("")
    A("## Exemple : bassin du Leman (eau)")
    A("fill 40 60 20 90 63 70 water")
    A("")
    A("## Exemple : base d'une tour blanche du chateau")
    A("fill -45 80 -35 -41 95 -31 white_concrete hollow")
    A("")
    A("## Exemple : poser une colonne romaine")
    A("setblock 0 72 0 chiseled_sandstone")
    A("fill 0 72 0 0 78 0 chiseled_sandstone")
    A("")
    A("## Teleportation vers le chateau")
    A("tp @s -40 81 -30")
    A("")
    A("## Titre de bienvenue")
    A("title @a title Nyon Reborn")
    A('titleraw @a subtitle {"rawtext":[{"text":"Bienvenue a Nyon"}]}')
    A("")
    A("## Message dans le chat")
    A('tellraw @a {"rawtext":[{"text":"Explore la vieille ville !"}]}')
    A("```\n")

    A("## 6. Quetes de decouverte\n")
    for q in QUESTS:
        tx, ty, tz = q["tp"]
        A("- **%s** — %s (`/tp @s %d %d %d`)"
          % (q["titre"], q["but"], tx, ty, tz))
    A("")

    A("## 7. Import sur Nintendo Switch via Realms\n")
    A("1. Construis/teste le monde sur Minecraft Bedrock (PC/mobile) avec "
      "l'add-on active.")
    A("2. Cree un **Realms** (abonnement Minecraft Realms Plus).")
    A("3. Dans le menu Realms, choisis **Remplacer le monde** et televerse "
      "ce monde Bedrock.")
    A("4. Sur la **Switch**, connecte-toi au meme compte Microsoft.")
    A("5. Ouvre Minecraft -> onglet **Realms** -> rejoins *Nyon Reborn*.")
    A("6. Pour l'add-on : applique le behavior_pack au monde AVANT le "
      "televersement (Parametres -> Packs de comportement).")
    A("7. Lance `/function start` une fois en jeu pour fixer spawn + regles, "
      "puis `/function quests` pour la visite.\n")

    A("## 8. Structure de l'add-on genere\n")
    A("```")
    A("generated/addon/behavior_pack/")
    A("  manifest.json")
    A("  functions/start.mcfunction")
    A("  functions/quests.mcfunction")
    A("```")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Generation de l'add-on Bedrock
# --------------------------------------------------------------------------

def build_manifest():
    return {
        "format_version": 2,
        "header": {
            "name": "%s Behavior Pack" % WORLD_NAME,
            "description": "Add-on de reconstruction de Nyon (Suisse) — "
                           "spawn, regles et visite des landmarks.",
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": "data",
                "uuid": str(uuid.uuid4()),
                "version": [1, 0, 0],
            }
        ],
    }


def build_start_mcfunction():
    sx, sy, sz = SPAWN
    out = [
        "# start.mcfunction — Nyon Reborn",
        "# Fixe le spawn, les regles et affiche le titre de bienvenue.",
        "setworldspawn %d %d %d" % (sx, sy, sz),
        "gamerule doDaylightCycle false",
        "gamerule doWeatherCycle false",
        "gamerule keepInventory true",
        "gamerule showcoordinates true",
        "gamerule commandblockoutput false",
        "time set day",
        "weather clear",
        "title @a title Nyon Reborn",
        'titleraw @a subtitle {"rawtext":[{"text":"Bienvenue dans la ville de Nyon"}]}',
        'tellraw @a {"rawtext":[{"text":"Tape /function quests pour la visite des landmarks."}]}',
    ]
    return "\n".join(out) + "\n"


def build_quests_mcfunction():
    out = [
        "# quests.mcfunction — Visite des landmarks de Nyon",
        'tellraw @a {"rawtext":[{"text":"=== Visite de Nyon ==="}]}',
    ]
    for q in QUESTS:
        tx, ty, tz = q["tp"]
        out.append(
            'tellraw @a {"rawtext":[{"text":"%s -> /tp @s %d %d %d"}]}'
            % (q["titre"] + " : " + q["but"], tx, ty, tz)
        )
    out.append("title @a actionbar Suis les quetes pour decouvrir Nyon !")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Ecriture
# --------------------------------------------------------------------------

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    bp = os.path.join(base, "generated", "addon", "behavior_pack")
    fn = os.path.join(bp, "functions")
    os.makedirs(fn, exist_ok=True)

    with open(os.path.join(base, "world_blueprint.md"), "w", encoding="utf-8") as f:
        f.write(build_blueprint_md())

    with open(os.path.join(bp, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(build_manifest(), f, indent=2, ensure_ascii=False)

    with open(os.path.join(fn, "start.mcfunction"), "w", encoding="utf-8") as f:
        f.write(build_start_mcfunction())
    with open(os.path.join(fn, "quests.mcfunction"), "w", encoding="utf-8") as f:
        f.write(build_quests_mcfunction())

    print("Genere :")
    print("  world_blueprint.md")
    print("  generated/addon/behavior_pack/manifest.json")
    print("  generated/addon/behavior_pack/functions/start.mcfunction")
    print("  generated/addon/behavior_pack/functions/quests.mcfunction")
    print("Monde : %s | Spawn : %s" % (WORLD_NAME, str(SPAWN)))


if __name__ == "__main__":
    main()
