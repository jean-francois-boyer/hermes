#!/usr/bin/env python3
"""mcaddon_export_agent.py — Build a self-contained Minecraft BEDROCK add-on
for the world 'Nyon Reborn' (rebuild of the Swiss city of Nyon).

Stdlib-only. No pip. Targets Bedrock Edition (NOT Java).

By default it builds into the directory that contains this script, so it can be
dropped into /tmp/dispatch-nyon-addon and run with plain `python3
mcaddon_export_agent.py`. You may override the output root with the env var
NYON_ROOT or the first CLI argument.

Pipeline:
  1. Build a behavior_pack (manifest.json with FRESH uuid4 header+module,
     functions for start/quests/nyon and the Nyon landmarks).
  2. Zip the behavior_pack into a .mcpack.
  3. Wrap the .mcpack inside exports/nyon-reborn.mcaddon (a zip), and also
     include behavior_pack/ at the .mcaddon root for maximum compatibility.
  4. Write README.md with import + Switch-via-Realms instructions.
"""
import json
import os
import shutil
import sys
import uuid
import zipfile

ROOT = os.environ.get("NYON_ROOT") or (
    sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
)
ROOT = os.path.abspath(ROOT)
BUILD = os.path.join(ROOT, "build")
BP = os.path.join(BUILD, "behavior_pack")
FUNCTIONS = os.path.join(BP, "functions")
EXPORTS = os.path.join(ROOT, "exports")

# ---------------------------------------------------------------------------
# Fresh UUIDs — never placeholders.
# ---------------------------------------------------------------------------
HEADER_UUID = str(uuid.uuid4())
MODULE_UUID = str(uuid.uuid4())


def reset_dirs():
    if os.path.exists(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(FUNCTIONS, exist_ok=True)
    os.makedirs(EXPORTS, exist_ok=True)


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# manifest.json (Bedrock behavior pack)
# ---------------------------------------------------------------------------
def build_manifest():
    manifest = {
        "format_version": 2,
        "header": {
            "name": "Nyon Reborn",
            "description": "Reconstruction de la ville suisse de Nyon (Bedrock).",
            "uuid": HEADER_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": "data",
                "description": "Fonctions de construction et quetes de Nyon.",
                "uuid": MODULE_UUID,
                "version": [1, 0, 0],
            }
        ],
    }
    write(os.path.join(BP, "manifest.json"),
          json.dumps(manifest, indent=4, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------
def build_functions():
    # start.mcfunction
    write(os.path.join(FUNCTIONS, "start.mcfunction"), """\
# Nyon Reborn -- initialisation du monde
gamerule doDaylightCycle true
gamerule doWeatherCycle true
gamerule keepInventory true
gamerule showCoordinates true
gamerule commandBlockOutput false
setworldspawn 0 65 0
title @a title Bienvenue a Nyon
title @a subtitle Perle du Lac Leman - Reconstruction Bedrock
tellraw @a {"rawtext":[{"text":"Nyon Reborn chargee. Tapez /function nyon pour construire la ville."}]}
""")

    # quests.mcfunction -- landmark tour quest
    write(os.path.join(FUNCTIONS, "quests.mcfunction"), """\
# Nyon Reborn -- quete: la tournee des monuments
title @a title Quete: La Tournee de Nyon
title @a subtitle Visitez les 4 monuments emblematiques
tellraw @a {"rawtext":[{"text":"=== Quete: La Tournee de Nyon ==="}]}
tellraw @a {"rawtext":[{"text":"1. Le Chateau de Nyon et ses tours blanches"}]}
tellraw @a {"rawtext":[{"text":"2. Les Colonnes romaines (forum antique)"}]}
tellraw @a {"rawtext":[{"text":"3. Le Port et les rives du Lac Leman"}]}
tellraw @a {"rawtext":[{"text":"4. La Vieille Ville et ses ruelles pavees"}]}
tellraw @a {"rawtext":[{"text":"Bonne visite a Nyon !"}]}
""")

    # chateau.mcfunction -- white castle with towers
    write(os.path.join(FUNCTIONS, "chateau.mcfunction"), """\
# Chateau de Nyon -- tours blanches dominant le lac
# Corps principal du chateau
fill -10 64 -10 10 64 10 stonebrick
fill -10 65 -10 10 78 10 quartz_block hollow
# Toiture
fill -11 79 -11 11 79 11 stonebrick
# Cinq tours blanches (les tours emblematiques)
fill -12 65 -12 -8 88 -8 quartz_block hollow
fill 8 65 -12 12 88 -8 quartz_block hollow
fill -12 65 8 -8 88 12 quartz_block hollow
fill 8 65 8 12 88 12 quartz_block hollow
fill -2 79 -2 2 92 2 quartz_block hollow
# Toits coniques des tours (terre cuite rouge)
fill -13 88 -13 -7 90 -7 red_glazed_terracotta
fill 7 88 -13 13 90 -7 red_glazed_terracotta
fill -13 88 7 -7 90 13 red_glazed_terracotta
fill 7 88 7 13 90 13 red_glazed_terracotta
""")

    # colonnes_romaines.mcfunction -- roman columns / forum
    write(os.path.join(FUNCTIONS, "colonnes_romaines.mcfunction"), """\
# Colonnes romaines -- vestiges du forum antique de Noviodunum
fill 30 64 -6 44 64 6 smooth_quartz
# Trois colonnes corinthiennes
fill 32 65 0 32 75 0 quartz_pillar
fill 37 65 0 37 75 0 quartz_pillar
fill 42 65 0 42 75 0 quartz_pillar
# Chapiteaux
setblock 32 76 0 quartz_block
setblock 37 76 0 quartz_block
setblock 42 76 0 quartz_block
# Architrave reliant les colonnes
fill 32 77 0 42 77 0 smooth_quartz
""")

    # port_leman.mcfunction -- Lake Geneva port
    write(os.path.join(FUNCTIONS, "port_leman.mcfunction"), """\
# Port et rives du Lac Leman
# Plan d'eau du lac
fill -40 60 -20 -20 63 20 water
# Quai en pierre
fill -20 63 -20 -18 64 20 stonebrick
# Ponton de bois s'avancant sur le lac
fill -28 64 -2 -20 64 2 planks
# Lampadaires du quai
setblock -19 65 -16 sea_lantern
setblock -19 65 0 sea_lantern
setblock -19 65 16 sea_lantern
""")

    # vieille_ville.mcfunction -- old town
    write(os.path.join(FUNCTIONS, "vieille_ville.mcfunction"), """\
# Vieille Ville -- ruelles pavees et maisons a colombages
# Place pavee centrale
fill 10 64 30 30 64 50 stone_slab
# Quatre maisons bordant la place
fill 12 65 32 18 70 38 planks hollow
fill 22 65 32 28 70 38 planks hollow
fill 12 65 42 18 70 48 planks hollow
fill 22 65 42 28 70 48 planks hollow
# Toits en terre cuite
fill 11 70 31 19 71 39 brick_block
fill 21 70 31 29 71 39 brick_block
fill 11 70 41 19 71 49 brick_block
fill 21 70 41 29 71 49 brick_block
# Fontaine de la place
fill 19 64 39 21 64 41 stonebrick
setblock 20 65 40 water
""")

    # nyon.mcfunction -- main builder calling all landmarks
    write(os.path.join(FUNCTIONS, "nyon.mcfunction"), """\
# Nyon Reborn -- construction complete de la ville
title @a title Construction de Nyon...
tellraw @a {"rawtext":[{"text":"Construction de Nyon en cours..."}]}
function chateau
function colonnes_romaines
function port_leman
function vieille_ville
tellraw @a {"rawtext":[{"text":"Nyon a ete reconstruite ! Explorez la ville."}]}
title @a title Nyon est prete !
""")


# ---------------------------------------------------------------------------
# pack icon (optional, generated locally — original 1x1 PNG)
# ---------------------------------------------------------------------------
def build_pack_icon():
    png = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x08, 0xD7, 0x63, 0x60, 0xA0, 0xF8, 0x0F,
        0x00, 0x01, 0x04, 0x01, 0x00, 0x9A, 0x9C, 0x18,
        0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,
        0xAE, 0x42, 0x60, 0x82,
    ])
    with open(os.path.join(BP, "pack_icon.png"), "wb") as f:
        f.write(png)


# ---------------------------------------------------------------------------
# Packaging
# ---------------------------------------------------------------------------
def zip_dir(src_dir, zip_path, arc_prefix=""):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for base, _dirs, files in os.walk(src_dir):
            for name in files:
                full = os.path.join(base, name)
                rel = os.path.relpath(full, src_dir)
                arc = os.path.join(arc_prefix, rel) if arc_prefix else rel
                zf.write(full, arc)


def package():
    # 1. behavior_pack -> .mcpack (pack contents at root of the mcpack)
    mcpack_path = os.path.join(BUILD, "nyon-reborn.mcpack")
    zip_dir(BP, mcpack_path)

    # 2. .mcpack -> .mcaddon (robust shape: .mcpack inside .mcaddon AND
    #    behavior_pack/ at root for maximum import compatibility).
    mcaddon_path = os.path.join(EXPORTS, "nyon-reborn.mcaddon")
    with zipfile.ZipFile(mcaddon_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(mcpack_path, "nyon-reborn.mcpack")
        for base, _dirs, files in os.walk(BP):
            for name in files:
                full = os.path.join(base, name)
                rel = os.path.relpath(full, BP)
                zf.write(full, os.path.join("behavior_pack", rel))
    return mcaddon_path


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------
def build_readme():
    readme = """# Nyon Reborn -- Add-on Minecraft Bedrock

Reconstruction de la ville suisse de **Nyon** (rives du Lac Leman) sous forme
d'add-on pour **Minecraft Bedrock Edition** (PAS Java).

- Fichier d'export : `exports/nyon-reborn.mcaddon`
- Header UUID : `%s`
- Module UUID : `%s`

## Contenu

Behavior pack << Nyon Reborn >> contenant :

- `functions/start.mcfunction` -- gamerules, point d'apparition, titre de bienvenue.
- `functions/quests.mcfunction` -- quete << La Tournee de Nyon >> (4 monuments).
- `functions/nyon.mcfunction` -- construit toute la ville (appelle les 4 fonctions ci-dessous).
- `functions/chateau.mcfunction` -- le Chateau de Nyon et ses tours blanches.
- `functions/colonnes_romaines.mcfunction` -- les colonnes romaines (forum antique).
- `functions/port_leman.mcfunction` -- le port et les rives du Lac Leman.
- `functions/vieille_ville.mcfunction` -- la vieille ville pavee.

## Import sous Minecraft Bedrock

1. Copiez `nyon-reborn.mcaddon` sur votre appareil.
2. **Ouvrez le fichier `.mcaddon` avec Minecraft Bedrock** (double-clic / << Ouvrir avec >>).
   Minecraft importe automatiquement le behavior pack.
3. Creez ou editez un monde -> **Parametres du monde** -> **Packs de comportement**
   -> **activez** << Nyon Reborn >>.
4. Activez l'option **<< Activer les triches / cheats >>** pour pouvoir lancer les fonctions.
5. Entrez dans le monde, puis dans le chat tapez :
   - `/function start` -- initialise le monde et affiche le message de bienvenue.
   - `/function nyon` -- construit toute la ville de Nyon.
   - `/function quests` -- affiche la quete de la tournee des monuments.

   (Vous pouvez aussi appeler chaque monument separement :
   `/function chateau`, `/function colonnes_romaines`,
   `/function port_leman`, `/function vieille_ville`.)

## Jouer sur Nintendo Switch via Realms

La Switch ne permet pas d'importer directement un `.mcaddon`, mais on peut y
acceder via un **Realm** synchronise depuis un autre appareil :

1. Sur un appareil **Windows / Android / iOS**, importez le `.mcaddon` (etapes ci-dessus)
   et activez le behavior pack << Nyon Reborn >> dans un monde.
2. Lancez la commande `/function nyon` pour construire la ville dans ce monde.
3. Depuis ce meme appareil, ouvrez le monde -> **... (Plus)** -> **<< Publier sur un Realm >>**
   (ou creez un Realm puis **<< Remplacer le monde >>** par le monde de Nyon).
   Le pack de comportement est televerse avec le monde sur le Realm.
4. Sur la **Nintendo Switch**, connectez-vous au **meme compte Microsoft**.
5. Dans Minecraft Switch -> onglet **Jouer** -> **Realms** -> rejoignez le Realm << Nyon >>.
   Le monde et son add-on sont charges automatiquement par le serveur Realm.
6. Si les triches sont activees par le proprietaire, relancez `/function quests`
   pour suivre la tournee des monuments.

> Astuce : sur le Realm, le proprietaire doit avoir active les triches pour que
> les commandes `/function` restent utilisables.

## Faithful Nyon

Tous les assets sont originaux et generes localement (commandes `/fill` Bedrock-valides).
Les monuments refletent le vrai Nyon : chateau a cinq tours, colonnes romaines,
port sur le Leman et vieille ville historique.
""" % (HEADER_UUID, MODULE_UUID)
    write(os.path.join(ROOT, "README.md"), readme)


def main():
    reset_dirs()
    build_manifest()
    build_functions()
    build_pack_icon()
    mcaddon_path = package()
    build_readme()

    # Self-verification: open the .mcaddon and parse a manifest.
    with zipfile.ZipFile(mcaddon_path) as zf:
        names = zf.namelist()
        assert any("manifest.json" in n for n in names), names
        assert any("start.mcfunction" in n for n in names), names
        man_name = next(n for n in names if n.endswith("behavior_pack/manifest.json"))
        data = json.loads(zf.read(man_name))
        assert data["header"]["uuid"] == HEADER_UUID
        assert data["modules"][0]["uuid"] == MODULE_UUID

    print("OK -> %s" % mcaddon_path)
    print("Header UUID:", HEADER_UUID)
    print("Module UUID:", MODULE_UUID)
    print("Entries:", len(names))


if __name__ == "__main__":
    main()
