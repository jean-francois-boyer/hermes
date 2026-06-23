#!/usr/bin/env python3
"""Agent local de création de skins Minecraft 64x64.

Génère sans dépendance externe :
- un skin PNG Minecraft 64x64 compatible Bedrock/Java,
- une prévisualisation PNG agrandie,
- un skin pack Bedrock `.mcpack` optionnel pour importer plusieurs skins.

Le rendu est procédural : l'agent interprète un brief simple (chevalier, robot,
pirate, ninja, mage, aventurier, youtubeur, etc.) et crée un skin cohérent.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import struct
import uuid
import zlib
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "generated" / "skins"
PACK_DIR = ROOT / "exports" / "skin-packs"

Color = tuple[int, int, int, int]
RGB = tuple[int, int, int]

TRANSPARENT: Color = (0, 0, 0, 0)
BLACK: Color = (20, 20, 24, 255)
WHITE: Color = (245, 245, 235, 255)


@dataclass
class SkinSpec:
    name: str
    theme: str
    model: str
    skin: Color
    hair: Color
    eyes: Color
    shirt: Color
    pants: Color
    shoes: Color
    accent: Color
    metal: Color


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüçñ -]", "", text)
    text = text.translate(str.maketrans("àâäéèêëîïôöùûüçñ", "aaaeeeeiioouuucn"))
    text = re.sub(r"\s+", "-", text)
    return text[:70].strip("-") or "skin-minecraft"


def rgba(rgb: RGB | tuple[int, int, int, int], alpha: int = 255) -> Color:
    if len(rgb) == 4:  # type: ignore[arg-type]
        return rgb  # type: ignore[return-value]
    return (rgb[0], rgb[1], rgb[2], alpha)  # type: ignore[index]


def clamp(v: int) -> int:
    return max(0, min(255, v))


def shade(c: Color, delta: int) -> Color:
    return (clamp(c[0] + delta), clamp(c[1] + delta), clamp(c[2] + delta), c[3])


def seeded_random(text: str) -> random.Random:
    seed = sum((i + 1) * ord(ch) for i, ch in enumerate(text))
    return random.Random(seed)


def parse_spec(brief: str, name: str | None, model: str) -> SkinSpec:
    lower = brief.lower()
    rnd = seeded_random(brief + (name or ""))

    skin_tones = [
        (232, 190, 145, 255), (198, 134, 86, 255), (141, 85, 56, 255),
        (241, 194, 125, 255), (224, 172, 105, 255),
    ]
    hair_colors = [(60, 38, 25, 255), (35, 28, 22, 255), (125, 78, 35, 255), (218, 176, 92, 255), (55, 55, 65, 255)]

    palettes: dict[str, tuple[Color, Color, Color, Color]] = {
        "chevalier": ((55, 70, 88, 255), (35, 42, 52, 255), (170, 175, 180, 255), (180, 30, 35, 255)),
        "knight": ((55, 70, 88, 255), (35, 42, 52, 255), (170, 175, 180, 255), (180, 30, 35, 255)),
        "robot": ((80, 90, 105, 255), (45, 50, 62, 255), (155, 165, 175, 255), (0, 200, 255, 255)),
        "cyber": ((30, 35, 50, 255), (18, 20, 30, 255), (75, 85, 105, 255), (0, 220, 180, 255)),
        "pirate": ((105, 45, 38, 255), (45, 28, 22, 255), (190, 160, 95, 255), (220, 30, 30, 255)),
        "ninja": ((24, 24, 30, 255), (12, 12, 16, 255), (55, 55, 65, 255), (120, 20, 190, 255)),
        "mage": ((55, 40, 105, 255), (32, 24, 65, 255), (90, 70, 155, 255), (255, 210, 60, 255)),
        "sorcier": ((55, 40, 105, 255), (32, 24, 65, 255), (90, 70, 155, 255), (255, 210, 60, 255)),
        "youtubeur": ((35, 45, 65, 255), (25, 30, 42, 255), (240, 240, 240, 255), (255, 0, 0, 255)),
        "aventurier": ((55, 115, 65, 255), (70, 55, 40, 255), (135, 100, 60, 255), (245, 190, 70, 255)),
    }

    theme = "aventurier"
    for key in palettes:
        if key in lower:
            theme = key
            break

    shirt, pants, metal, accent = palettes[theme]
    if "rouge" in lower:
        accent = (220, 35, 45, 255)
    elif "bleu" in lower:
        accent = (35, 100, 220, 255)
    elif "vert" in lower:
        accent = (30, 190, 90, 255)
    elif "or" in lower or "doré" in lower or "dore" in lower:
        accent = (245, 190, 55, 255)

    return SkinSpec(
        name=name or title_from_theme(theme),
        theme=theme,
        model=model,
        skin=rnd.choice(skin_tones),
        hair=rnd.choice(hair_colors),
        eyes=(rnd.choice([40, 80, 180, 55, 95]), rnd.choice([70, 110, 160, 120]), rnd.choice([80, 140, 210, 60]), 255),
        shirt=shirt,
        pants=pants,
        shoes=(25, 22, 20, 255),
        accent=accent,
        metal=metal,
    )


def title_from_theme(theme: str) -> str:
    titles = {
        "chevalier": "Chevalier Agent",
        "knight": "Knight Agent",
        "robot": "Robot Agent",
        "cyber": "Cyber Agent",
        "pirate": "Pirate Agent",
        "ninja": "Ninja Agent",
        "mage": "Mage Agent",
        "sorcier": "Sorcier Agent",
        "youtubeur": "YouTubeur Agent",
        "aventurier": "Aventurier Agent",
    }
    return titles.get(theme, "Skin Agent Minecraft")


class Canvas:
    def __init__(self, width: int, height: int, bg: Color = TRANSPARENT):
        self.width = width
        self.height = height
        self.pixels: list[list[Color]] = [[bg for _ in range(width)] for _ in range(height)]

    def set(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def rect(self, x: int, y: int, w: int, h: int, color: Color) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def rect_noise(self, x: int, y: int, w: int, h: int, color: Color, rnd: random.Random, amount: int = 10) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, shade(color, rnd.randint(-amount, amount)))

    def copy_rect_from(self, other: "Canvas", src_x: int, src_y: int, w: int, h: int, dst_x: int, dst_y: int, scale: int = 1) -> None:
        for y in range(h):
            for x in range(w):
                color = other.pixels[src_y + y][src_x + x]
                for sy in range(scale):
                    for sx in range(scale):
                        self.set(dst_x + x * scale + sx, dst_y + y * scale + sy, color)


def draw_skin(spec: SkinSpec) -> Canvas:
    rnd = seeded_random(spec.name + spec.theme)
    c = Canvas(64, 64, TRANSPARENT)

    # Base body parts — Minecraft skin UV map 64x64.
    draw_head(c, spec, rnd)
    draw_body(c, spec, rnd)
    draw_right_arm(c, spec, rnd)
    draw_left_arm(c, spec, rnd)
    draw_right_leg(c, spec, rnd)
    draw_left_leg(c, spec, rnd)
    draw_overlays(c, spec, rnd)
    return c


def draw_head(c: Canvas, s: SkinSpec, rnd: random.Random) -> None:
    skin, hair = s.skin, s.hair
    # head faces
    c.rect_noise(8, 8, 8, 8, skin, rnd, 6)   # front
    c.rect_noise(0, 8, 8, 8, shade(skin, -18), rnd, 4)  # right
    c.rect_noise(16, 8, 8, 8, shade(skin, -8), rnd, 4)  # left
    c.rect_noise(24, 8, 8, 8, shade(skin, -25), rnd, 4) # back
    c.rect_noise(8, 0, 8, 8, shade(skin, 8), rnd, 3)    # top
    c.rect_noise(16, 0, 8, 8, shade(skin, -28), rnd, 3) # bottom
    # hair cap
    for x in range(8, 16):
        for y in range(8, 11):
            c.set(x, y, shade(hair, rnd.randint(-8, 8)))
    for x in [8, 15]:
        for y in range(10, 14):
            c.set(x, y, shade(hair, -5))
    # eyes
    c.set(10, 12, WHITE); c.set(13, 12, WHITE)
    c.set(11, 12, s.eyes); c.set(14, 12, s.eyes)
    # mouth / beard variants
    if s.theme in {"pirate", "ninja"}:
        c.rect(10, 14, 5, 1, shade(s.hair, -20))
    else:
        c.rect(11, 15, 3, 1, shade(s.skin, -35))
    # side/back hair
    c.rect_noise(0, 8, 8, 3, hair, rnd, 8)
    c.rect_noise(16, 8, 8, 3, hair, rnd, 8)
    c.rect_noise(24, 8, 8, 5, hair, rnd, 8)
    c.rect_noise(8, 0, 8, 4, hair, rnd, 8)


def draw_body(c: Canvas, s: SkinSpec, rnd: random.Random) -> None:
    shirt = s.metal if s.theme in {"chevalier", "knight", "robot"} else s.shirt
    c.rect_noise(20, 20, 8, 12, shirt, rnd, 8)      # front
    c.rect_noise(16, 20, 4, 12, shade(shirt, -20), rnd, 5)
    c.rect_noise(28, 20, 4, 12, shade(shirt, -12), rnd, 5)
    c.rect_noise(32, 20, 8, 12, shade(shirt, -25), rnd, 5)
    c.rect_noise(20, 16, 8, 4, shade(shirt, 15), rnd, 4)
    c.rect_noise(28, 16, 8, 4, shade(shirt, -30), rnd, 4)
    # belt + emblem
    c.rect(20, 28, 8, 2, s.pants)
    c.rect(23, 28, 2, 2, s.accent)
    if s.theme == "youtubeur":
        c.rect(22, 23, 4, 3, (245, 245, 245, 255)); c.set(24, 24, s.accent)
    elif s.theme in {"mage", "sorcier"}:
        c.set(24, 23, s.accent); c.set(23, 24, s.accent); c.set(25, 24, s.accent); c.set(24, 25, s.accent)
    else:
        c.rect(23, 23, 2, 3, s.accent)


def draw_right_arm(c: Canvas, s: SkinSpec, rnd: random.Random) -> None:
    sleeve = s.metal if s.theme in {"chevalier", "knight", "robot"} else s.shirt
    c.rect_noise(44, 20, 4, 12, sleeve, rnd, 8)
    c.rect_noise(40, 20, 4, 12, shade(sleeve, -18), rnd, 5)
    c.rect_noise(48, 20, 4, 12, shade(sleeve, -8), rnd, 5)
    c.rect_noise(52, 20, 4, 12, shade(sleeve, -25), rnd, 5)
    c.rect_noise(44, 16, 4, 4, shade(sleeve, 15), rnd, 4)
    c.rect_noise(48, 16, 4, 4, shade(sleeve, -25), rnd, 4)
    c.rect_noise(44, 29, 4, 3, s.skin, rnd, 4)


def draw_left_arm(c: Canvas, s: SkinSpec, rnd: random.Random) -> None:
    sleeve = s.metal if s.theme in {"chevalier", "knight", "robot"} else s.shirt
    c.rect_noise(36, 52, 4, 12, sleeve, rnd, 8)
    c.rect_noise(32, 52, 4, 12, shade(sleeve, -18), rnd, 5)
    c.rect_noise(40, 52, 4, 12, shade(sleeve, -8), rnd, 5)
    c.rect_noise(44, 52, 4, 12, shade(sleeve, -25), rnd, 5)
    c.rect_noise(36, 48, 4, 4, shade(sleeve, 15), rnd, 4)
    c.rect_noise(40, 48, 4, 4, shade(sleeve, -25), rnd, 4)
    c.rect_noise(36, 61, 4, 3, s.skin, rnd, 4)


def draw_right_leg(c: Canvas, s: SkinSpec, rnd: random.Random) -> None:
    c.rect_noise(4, 20, 4, 12, s.pants, rnd, 7)
    c.rect_noise(0, 20, 4, 12, shade(s.pants, -18), rnd, 5)
    c.rect_noise(8, 20, 4, 12, shade(s.pants, -8), rnd, 5)
    c.rect_noise(12, 20, 4, 12, shade(s.pants, -25), rnd, 5)
    c.rect(4, 29, 4, 3, s.shoes)


def draw_left_leg(c: Canvas, s: SkinSpec, rnd: random.Random) -> None:
    c.rect_noise(20, 52, 4, 12, s.pants, rnd, 7)
    c.rect_noise(16, 52, 4, 12, shade(s.pants, -18), rnd, 5)
    c.rect_noise(24, 52, 4, 12, shade(s.pants, -8), rnd, 5)
    c.rect_noise(28, 52, 4, 12, shade(s.pants, -25), rnd, 5)
    c.rect(20, 61, 4, 3, s.shoes)


def draw_overlays(c: Canvas, s: SkinSpec, rnd: random.Random) -> None:
    # Hat / helmet layer (head overlay x32..63 y0..15)
    overlay = Canvas(64, 64, TRANSPARENT)
    if s.theme in {"chevalier", "knight", "robot"}:
        helmet = shade(s.metal, 15)
        overlay.rect(40, 8, 8, 3, helmet)
        overlay.rect(40, 11, 1, 5, helmet)
        overlay.rect(47, 11, 1, 5, helmet)
        overlay.rect(42, 12, 4, 1, shade(s.accent, 20))
        overlay.rect(40, 0, 8, 4, shade(helmet, 20))
    elif s.theme == "pirate":
        overlay.rect(40, 8, 8, 2, BLACK)
        overlay.rect(43, 12, 3, 2, BLACK)
        overlay.set(44, 13, WHITE)
    elif s.theme == "ninja":
        overlay.rect(40, 8, 8, 8, (8, 8, 12, 210))
        overlay.rect(42, 12, 4, 1, TRANSPARENT)
    elif s.theme in {"mage", "sorcier"}:
        overlay.rect(40, 8, 8, 2, s.accent)
        overlay.rect(42, 5, 4, 4, s.shirt)
        overlay.rect(43, 2, 2, 3, shade(s.shirt, 20))
    else:
        overlay.rect(40, 8, 8, 2, shade(s.hair, 10))

    # Copy overlay canvas pixels into actual overlay zones.
    for y in range(64):
        for x in range(64):
            if overlay.pixels[y][x][3] != 0:
                c.set(x, y, overlay.pixels[y][x])

    # Body jacket overlay x20,36 front area.
    jacket = shade(s.shirt, 18)
    if s.theme not in {"chevalier", "knight", "robot"}:
        c.rect(20, 36, 8, 1, jacket)
        c.rect(20, 37, 1, 10, jacket)
        c.rect(27, 37, 1, 10, shade(jacket, -10))
        c.rect(23, 39, 2, 2, s.accent)


def save_png(canvas: Canvas, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    for row in canvas.pixels:
        raw.append(0)  # filter type 0
        for r, g, b, a in row:
            raw.extend([r, g, b, a])

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def make_preview(skin: Canvas, path: Path) -> None:
    scale = 8
    preview = Canvas(32 * scale, 48 * scale, (235, 240, 245, 255))
    # Front view from UV map.
    preview.copy_rect_from(skin, 8, 8, 8, 8, 12 * scale, 0, scale)      # head
    preview.copy_rect_from(skin, 20, 20, 8, 12, 12 * scale, 8 * scale, scale)  # body
    preview.copy_rect_from(skin, 44, 20, 4, 12, 8 * scale, 8 * scale, scale)   # right arm
    preview.copy_rect_from(skin, 36, 52, 4, 12, 20 * scale, 8 * scale, scale)  # left arm
    preview.copy_rect_from(skin, 4, 20, 4, 12, 12 * scale, 20 * scale, scale)  # right leg
    preview.copy_rect_from(skin, 20, 52, 4, 12, 16 * scale, 20 * scale, scale) # left leg
    save_png(preview, path)


def create_skin_pack(spec: SkinSpec, skin_path: Path) -> Path:
    pack_slug = slugify(spec.name)
    work = PACK_DIR / pack_slug
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    skins_dir = work / "skins"
    skins_dir.mkdir()

    skin_file_name = f"{pack_slug}.png"
    shutil.copy2(skin_path, skins_dir / skin_file_name)

    manifest = {
        "format_version": 1,
        "header": {
            "name": f"{spec.name} Skin Pack",
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0],
        },
        "modules": [
            {
                "type": "skin_pack",
                "uuid": str(uuid.uuid4()),
                "version": [1, 0, 0],
            }
        ],
    }
    skins = {
        "serialize_name": pack_slug,
        "localization_name": pack_slug,
        "skins": [
            {
                "localization_name": pack_slug,
                "geometry": "geometry.humanoid.customSlim" if spec.model == "slim" else "geometry.humanoid.custom",
                "texture": f"skins/{skin_file_name}",
                "type": "free",
            }
        ],
    }
    (work / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work / "skins.json").write_text(json.dumps(skins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work / "README_IMPORT.txt").write_text(
        "Import Bedrock : ouvre le .mcpack avec Minecraft Bedrock, puis cherche le skin dans le vestiaire.\n"
        "Si le skin pack n'apparaît pas, importe directement le PNG depuis le créateur de personnage classique.\n",
        encoding="utf-8",
    )

    mcpack = PACK_DIR / f"{pack_slug}.mcpack"
    if mcpack.exists():
        mcpack.unlink()
    with zipfile.ZipFile(mcpack, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(work.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(work))
    return mcpack


def write_report(spec: SkinSpec, skin: Path, preview: Path, pack: Path | None) -> Path:
    report = skin.with_suffix(".md")
    pack_line = f"- Skin pack Bedrock : `{pack}`" if pack else "- Skin pack Bedrock : non généré"
    report.write_text(
        f"""# Skin Minecraft — {spec.name}

Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Fichiers

- Skin PNG 64x64 : `{skin}`
- Prévisualisation : `{preview}`
{pack_line}

## Import dans Minecraft Bedrock

### Méthode PNG simple

1. Ouvre Minecraft Bedrock.
2. Va dans le vestiaire / dressing room.
3. Choisis un personnage classique.
4. Importe le fichier PNG 64x64.
5. Sélectionne le modèle `{spec.model}`.

### Méthode skin pack `.mcpack`

1. Ouvre le `.mcpack` avec Minecraft Bedrock.
2. Attends le message d'import.
3. Va dans le vestiaire et cherche le pack `{spec.name} Skin Pack`.

## Détails

- Thème détecté : `{spec.theme}`
- Modèle : `{spec.model}`
- Compatible : Minecraft Bedrock / Java, format skin 64x64
""",
        encoding="utf-8",
    )
    return report


def generate_skin(brief: str, name: str | None, model: str, with_pack: bool) -> dict[str, Path]:
    spec = parse_spec(brief, name, model)
    slug = slugify(spec.name)
    skin = draw_skin(spec)
    skin_path = OUT_DIR / f"{slug}.png"
    preview_path = OUT_DIR / f"{slug}-preview.png"
    save_png(skin, skin_path)
    make_preview(skin, preview_path)
    mcpack = create_skin_pack(spec, skin_path) if with_pack else None
    report = write_report(spec, skin_path, preview_path, mcpack)
    outputs = {"skin": skin_path, "preview": preview_path, "report": report}
    if mcpack:
        outputs["mcpack"] = mcpack
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent de création de skins Minecraft")
    parser.add_argument("brief", nargs="*", help="Description du skin à générer")
    parser.add_argument("--name", help="Nom du skin")
    parser.add_argument("--model", choices=["classic", "slim"], default="classic", help="Modèle du skin")
    parser.add_argument("--no-pack", action="store_true", help="Ne pas générer le skin pack .mcpack")
    args = parser.parse_args()

    brief = " ".join(args.brief).strip() or "aventurier médiéval fantasy bleu et or"
    outputs = generate_skin(brief, args.name, args.model, with_pack=not args.no_pack)
    print("Skin Minecraft généré ✅")
    for key, path in outputs.items():
        print(f"- {key}: {path}")


if __name__ == "__main__":
    main()
