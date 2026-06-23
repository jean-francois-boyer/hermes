#!/usr/bin/env python3
"""Agent local de création de mondes Minecraft Bedrock compatibles Switch.

Cet agent reprend les fichiers du workspace :
- agent_prompt.md
- world_brief_template.md
- output_format.md
- examples/*.md
- bedrock-addon-template/

Il génère un blueprint markdown + des fonctions Bedrock (.mcfunction) + un add-on
importable en .mcaddon, sans API externe.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import textwrap
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
TEMPLATE_DIR = ROOT / "bedrock-addon-template"


@dataclass
class WorldSpec:
    idea: str
    name: str
    genre: str
    audience: str
    difficulty: str
    players: str
    add_on_allowed: bool
    command_blocks: bool
    zones: list[str]
    npcs: list[str]
    quests: list[str]
    enemies: list[str]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüçñ -]", "", text)
    text = text.translate(str.maketrans("àâäéèêëîïôöùûüçñ", "aaaeeeeiioouuucn"))
    text = re.sub(r"\s+", "-", text)
    return text[:60].strip("-") or "monde-minecraft"


def read_workspace_context() -> dict[str, str]:
    """Charge les fichiers déjà créés pour que l'agent respecte le cadre initial."""
    files = ["agent_prompt.md", "world_brief_template.md", "output_format.md"]
    context = {}
    for filename in files:
        path = ROOT / filename
        context[filename] = path.read_text(encoding="utf-8") if path.exists() else ""
    return context


def parse_brief(raw: str) -> WorldSpec:
    """Parse un brief libre ou markdown. Si le brief est vague, crée des valeurs par défaut."""
    lower = raw.lower()

    def has_any(words: list[str]) -> bool:
        return any(word in lower for word in words)

    genre = "Aventure RPG médiéval-fantasy"
    if has_any(["futur", "cyber", "space", "sci-fi", "science-fiction"]):
        genre = "Aventure futuriste"
    elif has_any(["horror", "horreur", "hanté", "zombie"]):
        genre = "Horreur douce Bedrock"
    elif has_any(["skyblock", "île volante", "iles volantes"]):
        genre = "Skyblock aventure"
    elif has_any(["parc", "attraction", "mini-jeu", "minijeu"]):
        genre = "Mini-jeu / parc d’attractions"

    difficulty = "Normale"
    if has_any(["facile", "enfant", "famille"]):
        difficulty = "Facile"
    elif has_any(["difficile", "hard", "survie hardcore"]):
        difficulty = "Difficile"

    players = "Solo ou 2 à 4 joueurs"
    if has_any(["solo"]):
        players = "Solo"
    elif has_any(["2", "3", "4", "multi", "coop"]):
        players = "2 à 4 joueurs"

    audience = "Famille / YouTube / aventure accessible"
    if has_any(["youtube", "tournage", "vidéo", "video"]):
        audience = "YouTube / tournage vidéo"

    add_on_allowed = not has_any(["sans addon", "sans add-on", "addon non", "add-on non"])
    command_blocks = not has_any(["sans command", "command blocks non", "command block non"])

    zones = extract_list_after(raw, ["zones souhaitées", "zones", "lieux"])
    if not zones:
        zones = [
            "Ville de départ sécurisée",
            "Château en ruine au nord",
            "Forêt magique à l’ouest",
            "Mine abandonnée au sud",
            "Port marchand à l’est",
        ]

    npcs = extract_list_after(raw, ["pnj souhaités", "pnj"])
    if not npcs:
        npcs = ["Maire", "Forgeronne", "Cartographe", "Marchande", "Gardien"]

    quests = extract_list_after(raw, ["quêtes souhaitées", "quetes souhaitées", "quêtes", "quetes"])
    if not quests:
        quests = [
            "Bienvenue au village",
            "La ressource manquante",
            "Le secret de la forêt",
            "Le marché du port",
            "Le boss du château",
        ]

    enemies = extract_list_after(raw, ["mobs", "ennemis"])
    if not enemies:
        enemies = ["zombies", "squelettes", "pillards", "araignées", "mini-boss nommé"]

    name = suggest_name(raw, genre)
    idea = raw.strip() or "Créer un monde aventure Minecraft Bedrock compatible Switch via Realm."

    return WorldSpec(
        idea=idea,
        name=name,
        genre=genre,
        audience=audience,
        difficulty=difficulty,
        players=players,
        add_on_allowed=add_on_allowed,
        command_blocks=command_blocks,
        zones=zones[:7],
        npcs=npcs[:7],
        quests=quests[:8],
        enemies=enemies[:8],
    )


def extract_list_after(raw: str, headings: list[str]) -> list[str]:
    lines = raw.splitlines()
    capture = False
    items: list[str] = []
    for line in lines:
        clean = line.strip()
        normalized = clean.lower().strip("# :")
        is_heading = clean.startswith("#") or clean.endswith(":")
        if is_heading and any(h in normalized for h in headings):
            capture = True
            continue
        if capture and (clean.startswith("##") or (clean and not clean.startswith(("-", "*")) and not re.match(r"^\d+[.)]", clean))):
            break
        if capture:
            match = re.match(r"^(?:[-*]|\d+[.)])\s*(.+)$", clean)
            if match and match.group(1).strip(" -"):
                items.append(match.group(1).strip())
    return items


def compact_text(text: str, max_len: int = 700) -> str:
    """Transforme un brief libre/markdown en résumé affichable dans une ligne markdown."""
    cleaned = re.sub(r"\s+", " ", text.replace("#", "")).strip()
    if len(cleaned) > max_len:
        return cleaned[: max_len - 1].rstrip() + "…"
    return cleaned


def normalize_markdown(text: str) -> str:
    """Retire l'indentation du bloc f-string sans casser le markdown généré."""
    return "\n".join(line[4:] if line.startswith("    ") else line for line in text.splitlines()).strip() + "\n"


def suggest_name(raw: str, genre: str) -> str:
    lower = raw.lower()
    if "dragon" in lower:
        return "Le Royaume du Dragon Endormi"
    if "pirate" in lower or "port" in lower:
        return "Les Îles du Port d’Émeraude"
    if "futur" in lower or "cyber" in lower:
        return "Néo-Blocs 2077"
    if "hant" in lower or "zombie" in lower:
        return "Le Village des Brumes"
    if "skyblock" in lower:
        return "Les Îles Suspendues"
    if "med" in lower or "fantasy" in lower or "royaume" in lower:
        return "Le Royaume des Blocs Oubliés"
    return "L’Archipel des Aventuriers"


def zone_coordinates(index: int) -> tuple[int, int, int]:
    coords = [
        (0, 70, 0),
        (0, 78, -220),
        (-220, 70, 0),
        (0, 54, 220),
        (220, 64, 0),
        (-180, 72, -180),
        (180, 45, 180),
    ]
    return coords[index % len(coords)]


def build_blueprint(spec: WorldSpec, context: dict[str, str]) -> str:
    zones_md = []
    for idx, zone in enumerate(spec.zones):
        x, y, z = zone_coordinates(idx)
        zones_md.append(textwrap.dedent(f"""
        ### Zone {idx + 1} — {zone}
        - Coordonnées approximatives : `{x} {y} {z}`
        - Taille conseillée : 60x60 blocs minimum
        - Biome conseillé : plaines, forêt ou biome proche du thème
        - Matériaux : bois, pierre, lanternes, barrières, panneaux, coffres
        - Fonction gameplay : progression, exploration, combat ou commerce
        - Secret : coffre caché avec émeraudes + indice vers la zone suivante
        """).strip())

    npc_md = []
    for idx, npc in enumerate(spec.npcs):
        x, y, z = zone_coordinates(idx % len(spec.zones))
        quest = spec.quests[idx % len(spec.quests)]
        npc_md.append(textwrap.dedent(f"""
        ### {npc}
        - Rôle : PNJ de progression
        - Apparence suggérée : villageois nommé ou NPC Bedrock si disponible
        - Position : `{x + 4} {y} {z + 4}`
        - Dialogue : « Bienvenue aventurier ! Ta prochaine mission : {quest}. »
        - Quête associée : {quest}
        """).strip())

    quest_md = []
    for idx, quest in enumerate(spec.quests):
        npc = spec.npcs[idx % len(spec.npcs)]
        reward = ["16 pains + 16 torches", "épée en fer", "potion de soin", "8 émeraudes", "arc + 32 flèches", "diamant", "clé finale"][idx % 7]
        quest_md.append(textwrap.dedent(f"""
        ### Quête {idx + 1} — {quest}
        - Donneur de quête : {npc}
        - Objectif : terminer l’objectif de la zone {idx + 1}
        - Étapes :
          1. Lire le panneau de quête.
          2. Aller à la coordonnée indiquée.
          3. Récupérer l’objet/preuve dans un coffre.
          4. Revenir au PNJ ou au panneau central.
        - Récompense : {reward}
        - Commandes utiles : `/scoreboard players set @p quete {idx + 1}`
        """).strip())

    commands = build_commands(spec)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return normalize_markdown(textwrap.dedent(f"""
    # Blueprint de monde Minecraft Bedrock — {spec.name}

    Généré le : {now}

    > Agent local basé sur `agent_prompt.md`, `world_brief_template.md` et `output_format.md` du workspace.

    ## 1. Concept du monde

    - Nom du monde : **{spec.name}**
    - Genre : {spec.genre}
    - Résumé : {compact_text(spec.idea)}
    - Objectif principal : explorer les zones, terminer les quêtes, vaincre le défi final et préparer le monde pour un Realm jouable sur Switch.
    - Durée estimée : 1 à 3 heures selon la construction
    - Nombre de joueurs : {spec.players}
    - Public : {spec.audience}

    ## 2. Paramètres Minecraft Bedrock

    - Mode recommandé : Survie préparée avec commandes de setup
    - Difficulté : {spec.difficulty}
    - Coordonnée du spawn : `0 70 0`
    - Command blocks : {'activés' if spec.command_blocks else 'désactivés'}
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

    {chr(10).join(zones_md)}

    ## 5. Spawn

    - Description : place centrale sécurisée, claire, avec panneaux et coffres de départ.
    - Construction : plateforme 25x25, fontaine centrale, panneau « règles », panneau « quêtes ».
    - Message de bienvenue : `Bienvenue dans {spec.name}`
    - Commandes de base : voir section 10.

    ## 6. PNJ

    {chr(10).join(npc_md)}

    ## 7. Quêtes

    {chr(10).join(quest_md)}

    ## 8. Donjons et défis

    ### Donjon 1 — Le défi de la zone nord
    - Thème : ruines, couloirs, pièges simples
    - Entrée : proche de `0 78 -220`
    - Salles : entrée, salle mobs, salle coffre, salle mini-boss
    - Ennemis : {', '.join(spec.enemies[:4])}
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
    {commands}
    ```

    ## 11. Add-on Bedrock optionnel

    {'Un add-on de base est généré dans `generated/addon/` avec un behavior pack et des fonctions `.mcfunction`.' if spec.add_on_allowed else 'Non nécessaire : le brief demande de rester sans add-on.'}

    Fichiers générés utiles :
    - `generated/addon/behavior_pack/functions/start.mcfunction`
    - `generated/addon/behavior_pack/functions/quests.mcfunction`
    - `generated/{slugify(spec.name)}.mcaddon`

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
    """))


def build_commands(spec: WorldSpec) -> str:
    lines = [
        "setworldspawn 0 70 0",
        "gamerule keepinventory true",
        "gamerule mobgriefing false",
        "scoreboard objectives add quete dummy Quêtes",
        "scoreboard players set @a quete 0",
        f"title @a title Bienvenue dans {spec.name}",
        "give @a bread 16",
        "give @a torch 32",
    ]
    for idx, quest in enumerate(spec.quests, start=1):
        safe = quest.replace('"', "'")[:80]
        lines.append(f'tellraw @a {{"rawtext":[{{"text":"Quête {idx}: {safe}"}}]}}')
    return "\n".join(lines)


def write_addon(spec: WorldSpec) -> Path:
    addon_dir = GENERATED / "addon"
    if addon_dir.exists():
        shutil.rmtree(addon_dir)
    shutil.copytree(TEMPLATE_DIR, addon_dir)

    behavior_manifest = addon_dir / "behavior_pack" / "manifest.json"
    resource_manifest = addon_dir / "resource_pack" / "manifest.json"
    for manifest_path, pack_type in [(behavior_manifest, "Behavior Pack"), (resource_manifest, "Resource Pack")]:
        if manifest_path.exists():
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        else:
            data = {"format_version": 2, "header": {}, "modules": [{}]}
        data["header"]["name"] = f"{spec.name} - {pack_type}"
        data["header"]["description"] = "Pack généré par l’agent Minecraft Bedrock local"
        data["header"]["uuid"] = str(uuid.uuid4())
        data["header"]["version"] = [1, 0, 0]
        data["header"].setdefault("min_engine_version", [1, 20, 0])
        data.setdefault("modules", [{}])[0]["uuid"] = str(uuid.uuid4())
        data["modules"][0]["version"] = [1, 0, 0]
        if pack_type == "Behavior Pack":
            data["modules"][0]["type"] = "data"
        else:
            data["modules"][0]["type"] = "resources"
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    functions_dir = addon_dir / "behavior_pack" / "functions"
    functions_dir.mkdir(parents=True, exist_ok=True)
    (functions_dir / "start.mcfunction").write_text(build_commands(spec) + "\n", encoding="utf-8")
    (functions_dir / "quests.mcfunction").write_text(build_quest_function(spec), encoding="utf-8")
    (functions_dir / "README.md").write_text(textwrap.dedent(f"""
    # Fonctions Bedrock générées

    Dans Minecraft Bedrock, avec le behavior pack activé :

    ```mcfunction
    /function start
    /function quests
    ```

    Monde : {spec.name}
    """).strip() + "\n", encoding="utf-8")

    mcaddon = GENERATED / f"{slugify(spec.name)}.mcaddon"
    if mcaddon.exists():
        mcaddon.unlink()
    with zipfile.ZipFile(mcaddon, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in addon_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(addon_dir))
    return mcaddon


def build_quest_function(spec: WorldSpec) -> str:
    lines = [f'tellraw @a {{"rawtext":[{{"text":"=== Quêtes — {spec.name} ==="}}]}}']
    for idx, quest in enumerate(spec.quests, start=1):
        lines.append(f'tellraw @a {{"rawtext":[{{"text":"{idx}. {quest}"}}]}}')
    return "\n".join(lines) + "\n"


def run_agent(brief: str) -> dict[str, Path]:
    GENERATED.mkdir(parents=True, exist_ok=True)
    context = read_workspace_context()
    spec = parse_brief(brief)
    blueprint = build_blueprint(spec, context)

    blueprint_path = GENERATED / "world_blueprint.md"
    named_blueprint_path = GENERATED / f"{slugify(spec.name)}-blueprint.md"
    blueprint_path.write_text(blueprint, encoding="utf-8")
    named_blueprint_path.write_text(blueprint, encoding="utf-8")
    mcaddon = write_addon(spec)
    return {
        "blueprint": blueprint_path,
        "named_blueprint": named_blueprint_path,
        "mcaddon": mcaddon,
        "addon_dir": GENERATED / "addon",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent local Minecraft Bedrock compatible Switch")
    parser.add_argument("brief", nargs="*", help="Brief libre du monde à créer")
    parser.add_argument("--brief-file", type=Path, help="Fichier markdown contenant le brief")
    args = parser.parse_args()

    if args.brief_file:
        brief = args.brief_file.read_text(encoding="utf-8")
    else:
        brief = " ".join(args.brief).strip()

    if not brief:
        example = ROOT / "examples" / "village_medieval.md"
        brief = example.read_text(encoding="utf-8") if example.exists() else "Village médiéval fantasy avec quêtes"

    outputs = run_agent(brief)
    print("Agent Minecraft terminé ✅")
    for key, path in outputs.items():
        print(f"- {key}: {path}")


if __name__ == "__main__":
    main()
