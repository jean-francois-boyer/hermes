#!/usr/bin/env python3
"""Agent de génération de structures Minecraft Bedrock en `.mcfunction`.

Objectif : créer des constructions reproductibles dans Minecraft Bedrock avec des
commandes compatibles : `/fill`, `/setblock`, `/summon`, `/title`, `/function`.

L'agent ne produit pas de `.mcstructure` binaire : il génère des fonctions Bedrock
faciles à importer dans le behavior pack puis à lancer dans un monde/Realm/Switch.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "generated" / "structures"
ADDON_FUNCTIONS = ROOT / "generated" / "addon" / "behavior_pack" / "functions"
EXPORT_DIR = ROOT / "exports" / "structures"


@dataclass
class StructureSpec:
    name: str
    slug: str
    kind: str
    brief: str
    origin: tuple[int, int, int]
    palette: dict[str, str]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüçñ -]", "", text)
    text = text.translate(str.maketrans("àâäéèêëîïôöùûüçñ", "aaaeeeeiioouuucn"))
    text = re.sub(r"\s+", "-", text)
    return text[:70].strip("-") or "structure"


def detect_kind(brief: str) -> str:
    lower = brief.lower()
    if any(word in lower for word in ["donjon", "dungeon", "boss", "piège", "piege"]):
        return "dungeon"
    if any(word in lower for word in ["spawn", "départ", "depart", "hub"]):
        return "village"
    if any(word in lower for word in ["marché", "marche", "shop", "boutique"]):
        return "village"
    if any(word in lower for word in ["maison", "village", "médiéval", "medieval"]):
        return "village"
    if any(word in lower for word in ["tour", "tower"]):
        return "tower"
    return "village"


def palette_for(brief: str, kind: str) -> dict[str, str]:
    lower = brief.lower()
    if "futur" in lower or "cyber" in lower:
        return {
            "floor": "smooth_quartz",
            "wall": "gray_concrete",
            "roof": "cyan_stained_glass",
            "accent": "sea_lantern",
            "path": "light_gray_concrete",
            "fence": "iron_bars",
        }
    if kind == "dungeon" or any(word in lower for word in ["sombre", "hant", "ruine"]):
        return {
            "floor": "deepslate_tiles",
            "wall": "cracked_deepslate_bricks",
            "roof": "blackstone",
            "accent": "soul_lantern",
            "path": "cobbled_deepslate",
            "fence": "iron_bars",
        }
    if "désert" in lower or "desert" in lower:
        return {
            "floor": "smooth_sandstone",
            "wall": "sandstone",
            "roof": "cut_sandstone",
            "accent": "lantern",
            "path": "sandstone",
            "fence": "acacia_fence",
        }
    return {
        "floor": "stone_bricks",
        "wall": "oak_planks",
        "roof": "spruce_stairs",
        "accent": "lantern",
        "path": "cobblestone",
        "fence": "oak_fence",
    }


def parse_origin(value: str | None) -> tuple[int, int, int]:
    if not value:
        return (0, 70, 0)
    parts = [int(p) for p in re.split(r"[, ]+", value.strip()) if p]
    if len(parts) != 3:
        raise SystemExit("--origin doit contenir 3 nombres, exemple: --origin '0 70 0'")
    return (parts[0], parts[1], parts[2])


def make_spec(brief: str, name: str | None, origin: tuple[int, int, int]) -> StructureSpec:
    kind = detect_kind(brief)
    final_name = name or {
        "village": "Village Agent Minecraft",
        "dungeon": "Donjon Agent Minecraft",
        "tower": "Tour Agent Minecraft",
    }.get(kind, "Structure Agent Minecraft")
    return StructureSpec(
        name=final_name,
        slug=slugify(final_name),
        kind=kind,
        brief=brief,
        origin=origin,
        palette=palette_for(brief, kind),
    )


def rel(spec: StructureSpec, dx: int, dy: int, dz: int) -> tuple[int, int, int]:
    x, y, z = spec.origin
    return x + dx, y + dy, z + dz


def fill(spec: StructureSpec, a: tuple[int, int, int], b: tuple[int, int, int], block: str) -> str:
    x1, y1, z1 = rel(spec, *a)
    x2, y2, z2 = rel(spec, *b)
    return f"fill {x1} {y1} {z1} {x2} {y2} {z2} {block}"


def setblock(spec: StructureSpec, p: tuple[int, int, int], block: str) -> str:
    x, y, z = rel(spec, *p)
    return f"setblock {x} {y} {z} {block}"


def summon(spec: StructureSpec, entity: str, p: tuple[int, int, int], extra: str = "") -> str:
    x, y, z = rel(spec, *p)
    suffix = f" {extra}" if extra else ""
    return f"summon {entity} {x} {y} {z}{suffix}"


def header(spec: StructureSpec, title: str) -> list[str]:
    return [
        f"# Structure: {spec.name}",
        f"# Module: {title}",
        "# Commands: fill setblock summon chest function",
        f"# Origine: {spec.origin[0]} {spec.origin[1]} {spec.origin[2]}",
        f"say Construction {title} - {spec.name}",
    ]


def build_spawn(spec: StructureSpec) -> list[str]:
    p = spec.palette
    lines = header(spec, "spawn")
    lines += [
        fill(spec, (-8, -1, -8), (8, -1, 8), p["floor"]),
        fill(spec, (-9, 0, -9), (9, 0, 9), "air"),
        fill(spec, (-7, 0, -7), (7, 0, 7), "air"),
        fill(spec, (-10, 0, -10), (10, 0, -10), p["fence"]),
        fill(spec, (-10, 0, 10), (10, 0, 10), p["fence"]),
        fill(spec, (-10, 0, -10), (-10, 0, 10), p["fence"]),
        fill(spec, (10, 0, -10), (10, 0, 10), p["fence"]),
        setblock(spec, (0, 0, 0), "bell"),
        setblock(spec, (-4, 0, -4), p["accent"]),
        setblock(spec, (4, 0, -4), p["accent"]),
        setblock(spec, (-4, 0, 4), p["accent"]),
        setblock(spec, (4, 0, 4), p["accent"]),
        setblock(spec, (0, 0, -8), 'standing_sign ["Bienvenue", "Agent Minecraft"]'),
        "setworldspawn " + " ".join(str(v) for v in spec.origin),
        f'title @a title Bienvenue dans {spec.name}',
    ]
    return lines


def build_house(spec: StructureSpec, ox: int, oz: int, label: str) -> list[str]:
    p = spec.palette
    lines = [f"# Maison {label}"]
    # floor/walls/roof
    lines += [
        fill(spec, (ox, 0, oz), (ox + 6, 0, oz + 6), p["floor"]),
        fill(spec, (ox, 1, oz), (ox + 6, 4, oz + 6), p["wall"]),
        fill(spec, (ox + 1, 1, oz + 1), (ox + 5, 3, oz + 5), "air"),
        fill(spec, (ox - 1, 5, oz - 1), (ox + 7, 5, oz + 7), "spruce_planks"),
        setblock(spec, (ox + 3, 1, oz), "air"),
        setblock(spec, (ox + 3, 1, oz - 1), "oak_door"),
        setblock(spec, (ox + 1, 2, oz), "glass_pane"),
        setblock(spec, (ox + 5, 2, oz), "glass_pane"),
        setblock(spec, (ox + 3, 1, oz + 5), "chest"),
        setblock(spec, (ox + 2, 1, oz + 5), "crafting_table"),
        setblock(spec, (ox + 4, 1, oz + 5), "furnace"),
    ]
    return lines


def build_market(spec: StructureSpec) -> list[str]:
    p = spec.palette
    lines = header(spec, "market")
    lines += [
        fill(spec, (12, -1, -6), (26, -1, 6), p["path"]),
        fill(spec, (14, 0, -4), (18, 0, 0), "barrel"),
        fill(spec, (20, 0, -4), (24, 0, 0), "barrel"),
        fill(spec, (14, 1, -4), (18, 1, 0), "red_wool"),
        fill(spec, (20, 1, -4), (24, 1, 0), "blue_wool"),
        setblock(spec, (16, 0, 3), 'standing_sign ["Marché", "Émeraudes"]'),
        summon(spec, "villager", (16, 1, -2)),
        summon(spec, "villager", (22, 1, -2)),
    ]
    return lines


def build_dungeon(spec: StructureSpec) -> list[str]:
    p = spec.palette
    lines = header(spec, "dungeon")
    lines += [
        fill(spec, (-12, -2, 18), (12, -2, 42), p["floor"]),
        fill(spec, (-12, -1, 18), (12, 5, 42), p["wall"]),
        fill(spec, (-10, -1, 20), (10, 4, 40), "air"),
        fill(spec, (-12, 6, 18), (12, 6, 42), p["roof"]),
        fill(spec, (-1, -1, 18), (1, 3, 18), "air"),
        setblock(spec, (0, -1, 21), "stone_pressure_plate"),
        setblock(spec, (0, -2, 22), "tnt"),
        setblock(spec, (-8, -1, 25), "spawner"),
        setblock(spec, (8, -1, 25), "spawner"),
        summon(spec, "zombie", (-6, -1, 30)),
        summon(spec, "skeleton", (6, -1, 30)),
        summon(spec, "zombie", (0, -1, 37)),
        setblock(spec, (0, -1, 40), "chest"),
        f'tellraw @a {{"rawtext":[{{"text":"Donjon {spec.name}: coffre récompense placé."}}]}}',
    ]
    return lines


def build_tower(spec: StructureSpec) -> list[str]:
    p = spec.palette
    lines = header(spec, "tower")
    lines += [
        fill(spec, (-4, 0, 14), (4, 14, 22), p["wall"]),
        fill(spec, (-3, 1, 15), (3, 13, 21), "air"),
        fill(spec, (-5, 15, 13), (5, 15, 23), p["roof"]),
        setblock(spec, (0, 1, 14), "air"),
        setblock(spec, (0, 1, 13), "oak_door"),
        setblock(spec, (0, 14, 18), p["accent"]),
        summon(spec, "villager", (0, 1, 18)),
    ]
    return lines


def build_main(spec: StructureSpec) -> list[str]:
    lines = header(spec, "main")
    lines += [
        f"function {spec.slug}_spawn",
        f"function {spec.slug}_market",
    ]
    if spec.kind == "dungeon":
        lines.append(f"function {spec.slug}_dungeon")
    elif spec.kind == "tower":
        lines.append(f"function {spec.slug}_tower")
    else:
        lines += [
            f"function {spec.slug}_houses",
            f"function {spec.slug}_dungeon",
        ]
    lines.append(f'tellraw @a {{"rawtext":[{{"text":"Structure {spec.name} terminée."}}]}}')
    return lines


def build_houses(spec: StructureSpec) -> list[str]:
    lines = header(spec, "houses")
    lines += build_house(spec, -24, -8, "ouest")
    lines += build_house(spec, -24, 6, "sud-ouest")
    lines += build_house(spec, 14, 8, "est")
    return lines


def write_function(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def copy_to_addon(outputs: dict[str, Path]) -> None:
    if not ADDON_FUNCTIONS.exists():
        return
    for key, path in outputs.items():
        if path.suffix == ".mcfunction":
            shutil.copy2(path, ADDON_FUNCTIONS / path.name)


def export_zip(spec: StructureSpec, output_dir: Path) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = EXPORT_DIR / f"{spec.slug}-structures.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(output_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(output_dir))
    return zip_path


def write_guide(spec: StructureSpec, outputs: dict[str, Path], output_dir: Path) -> Path:
    guide = output_dir / f"{spec.slug}-GUIDE.md"
    functions = "\n".join(f"- `{path.name}`" for key, path in outputs.items() if path.suffix == ".mcfunction")
    guide.write_text(
        f"""# Guide Structure — {spec.name}

Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Brief

{spec.brief}

## Origine

`{spec.origin[0]} {spec.origin[1]} {spec.origin[2]}`

## Fichiers `.mcfunction`

{functions}

## Import dans Bedrock

1. Copie les fichiers `.mcfunction` dans le behavior pack :
   `behavior_pack/functions/`
2. Réexporte le `.mcaddon` avec :

```bash
python3 mcaddon_export_agent.py --regenerate-uuids
```

3. Dans Minecraft Bedrock, active le behavior pack.
4. Lance :

```mcfunction
/function {spec.slug}
```

Tu peux aussi lancer les modules séparés :

```mcfunction
/function {spec.slug}_spawn
/function {spec.slug}_market
/function {spec.slug}_houses
/function {spec.slug}_dungeon
```

## Attention

Les commandes utilisent `/fill` et `/setblock`. Teste d'abord dans une copie du monde.
""",
        encoding="utf-8",
    )
    return guide


def generate_structure(
    brief: str,
    name: str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT,
    origin: tuple[int, int, int] = (0, 70, 0),
    install_to_addon: bool = True,
) -> dict[str, Path]:
    output_dir = Path(output_dir)
    spec = make_spec(brief, name, origin)
    structure_dir = output_dir / spec.slug
    if structure_dir.exists():
        shutil.rmtree(structure_dir)
    structure_dir.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, Path] = {}
    outputs["main"] = structure_dir / f"{spec.slug}.mcfunction"
    outputs["spawn"] = structure_dir / f"{spec.slug}_spawn.mcfunction"
    outputs["market"] = structure_dir / f"{spec.slug}_market.mcfunction"
    outputs["dungeon"] = structure_dir / f"{spec.slug}_dungeon.mcfunction"

    write_function(outputs["main"], build_main(spec))
    write_function(outputs["spawn"], build_spawn(spec))
    write_function(outputs["market"], build_market(spec))
    write_function(outputs["dungeon"], build_dungeon(spec))

    if spec.kind == "tower":
        outputs["tower"] = structure_dir / f"{spec.slug}_tower.mcfunction"
        write_function(outputs["tower"], build_tower(spec))
    else:
        outputs["houses"] = structure_dir / f"{spec.slug}_houses.mcfunction"
        write_function(outputs["houses"], build_houses(spec))

    outputs["guide"] = write_guide(spec, outputs, structure_dir)
    outputs["zip"] = export_zip(spec, structure_dir)

    if install_to_addon:
        copy_to_addon(outputs)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent de structures Minecraft Bedrock")
    parser.add_argument("brief", nargs="*", help="Description de la structure à générer")
    parser.add_argument("--name", help="Nom de la structure")
    parser.add_argument("--origin", help="Coordonnées x y z, exemple: '0 70 0'")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-install", action="store_true", help="Ne copie pas les fonctions dans generated/addon")
    args = parser.parse_args()

    brief = " ".join(args.brief).strip() or "village médiéval avec spawn, maisons, marché et donjon"
    outputs = generate_structure(
        brief=brief,
        name=args.name,
        output_dir=args.output_dir,
        origin=parse_origin(args.origin),
        install_to_addon=not args.no_install,
    )
    print("Structure Minecraft générée ✅")
    for key, path in outputs.items():
        print(f"- {key}: {path}")


if __name__ == "__main__":
    main()
