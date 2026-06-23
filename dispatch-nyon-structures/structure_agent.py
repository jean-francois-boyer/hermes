#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
structure_agent.py — Generateur de structures Minecraft BEDROCK pour NYON (Suisse).

Emet des fichiers .mcfunction (commandes /fill, /setblock, /summon valides en
Bedrock) qui reconstruisent bloc par bloc les monuments emblematiques de Nyon :

  - chateau.mcfunction          : Chateau de Nyon (donjon rectangulaire blanc +
                                  5 tours rondes blanches + cour interieure)
  - colonnes_romaines.mcfunction: les 3 colonnes romaines reconstituees sur
                                  l'esplanade (gres/quartz, marronniers)
  - port_leman.mcfunction       : le bord du lac Leman (plan d'eau, quai/promenade,
                                  petit port avec jetees)
  - vieille_ville.mcfunction    : maisons de la vieille ville (pierre + sapin,
                                  toits pentus) le long d'une ruelle pavee
  - nyon.mcfunction             : fonction PRINCIPALE qui appelle les sous-fonctions
                                  via /function

Cible : Minecraft BEDROCK (Switch via Realms). Stdlib uniquement, aucun pip.

NB Bedrock : /fill est limite a ~32768 blocs par commande -> les gros volumes sont
decoupes en tranches (chunking) pour ne jamais depasser la limite.
"""

import os
import math

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "generated", "functions")

ORIGIN_X, ORIGIN_Y, ORIGIN_Z = 0, 64, 0      # origine commune du chantier
FILL_LIMIT = 30000                            # marge sous la limite Bedrock (~32768)

# Palette de blocs (identifiants valides Bedrock)
B_QUARTZ      = "quartz_block"
B_WHITE_CONC  = "concrete white"
B_SANDSTONE   = "sandstone"
B_STONE_BRICK = "stonebrick"
B_COBBLE      = "cobblestone"
B_STONE       = "stone"
B_SPRUCE_PLK  = "planks spruce"
B_SPRUCE_LOG  = "log spruce"
B_DARK_OAK    = "planks 5"
B_WATER       = "water"
B_GLASS       = "glass"
B_LEAVES      = "leaves oak"
B_OAK_LOG     = "log"
B_AIR         = "air"
B_GLOWSTONE   = "glowstone"
B_TORCH       = "torch"


# --------------------------------------------------------------------------- #
# Helpers de commandes
# --------------------------------------------------------------------------- #
def fill(cmds, x1, y1, z1, x2, y2, z2, block):
    """/fill chunke pour respecter la limite de volume Bedrock."""
    xa, xb = sorted((int(x1), int(x2)))
    ya, yb = sorted((int(y1), int(y2)))
    za, zb = sorted((int(z1), int(z2)))
    total = (xb - xa + 1) * (yb - ya + 1) * (zb - za + 1)
    if total <= FILL_LIMIT:
        cmds.append(f"fill {xa} {ya} {za} {xb} {yb} {zb} {block}")
        return
    layer = (xb - xa + 1) * (zb - za + 1)
    if layer <= FILL_LIMIT:
        max_layers = max(1, FILL_LIMIT // layer)
        y = ya
        while y <= yb:
            yt = min(yb, y + max_layers - 1)
            cmds.append(f"fill {xa} {y} {za} {xb} {yt} {zb} {block}")
            y = yt + 1
        return
    for y in range(ya, yb + 1):
        rl = (xb - xa + 1)
        max_rows = max(1, FILL_LIMIT // rl)
        z = za
        while z <= zb:
            zt = min(zb, z + max_rows - 1)
            cmds.append(f"fill {xa} {y} {z} {xb} {y} {zt} {block}")
            z = zt + 1


def setblock(cmds, x, y, z, block):
    cmds.append(f"setblock {int(x)} {int(y)} {int(z)} {block}")


def summon(cmds, entity, x, y, z):
    cmds.append(f"summon {entity} {int(x)} {int(y)} {int(z)}")


def comment(cmds, text):
    cmds.append(f"# {text}")


# --------------------------------------------------------------------------- #
# Geometrie des tours rondes
# --------------------------------------------------------------------------- #
def ring(cmds, cx, cz, y, radius, block):
    placed = set()
    steps = max(16, int(radius * 8))
    for i in range(steps):
        ang = (2 * math.pi * i) / steps
        bx = int(round(cx + radius * math.cos(ang)))
        bz = int(round(cz + radius * math.sin(ang)))
        if (bx, bz) not in placed:
            placed.add((bx, bz))
            setblock(cmds, bx, y, bz, block)


def disc(cmds, cx, cz, y, radius, block):
    r2 = radius * radius
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            if dx * dx + dz * dz <= r2:
                setblock(cmds, cx + dx, y, cz + dz, block)


def round_tower(cmds, cx, cz, base_y, height, radius, wall, roof):
    comment(cmds, f"Tour ronde ({cx},{cz}) r={radius} h={height}")
    for y in range(base_y, base_y + height):
        ring(cmds, cx, cz, y, radius, wall)
    top = base_y + height
    for i in range(0, 360, 45):
        a = math.radians(i)
        setblock(cmds, int(round(cx + radius * math.cos(a))), top,
                 int(round(cz + radius * math.sin(a))), wall)
    cone_h = max(3, radius + 1)
    for k in range(cone_h):
        disc(cmds, cx, cz, top + 1 + k, max(0, radius - k), roof)
    return top


# --------------------------------------------------------------------------- #
# 1) CHATEAU DE NYON
# --------------------------------------------------------------------------- #
def build_chateau():
    cmds = []
    comment(cmds, "=== CHATEAU DE NYON ===")
    comment(cmds, "Donjon rectangulaire blanc + 5 tours rondes + cour interieure")
    ox, oy, oz = ORIGIN_X, ORIGIN_Y, ORIGIN_Z

    fill(cmds, ox - 2, oy - 1, oz - 2, ox + 34, oy - 1, oz + 26, B_STONE_BRICK)

    x1, z1, x2, z2 = ox, oz, ox + 32, oz + 24
    wt = oy + 12
    fill(cmds, x1, oy, z1, x2, wt, z1 + 1, B_WHITE_CONC)
    fill(cmds, x1, oy, z2 - 1, x2, wt, z2, B_WHITE_CONC)
    fill(cmds, x1, oy, z1, x1 + 1, wt, z2, B_WHITE_CONC)
    fill(cmds, x2 - 1, oy, z1, x2, wt, z2, B_WHITE_CONC)

    fill(cmds, x1 + 2, oy - 1, z1 + 2, x2 - 2, oy - 1, z2 - 2, B_COBBLE)
    fill(cmds, x1 + 2, oy, z1 + 2, x2 - 2, wt, z2 - 2, B_AIR)

    for x in range(x1, x2 + 1, 2):
        setblock(cmds, x, wt + 1, z1, B_WHITE_CONC)
        setblock(cmds, x, wt + 1, z2, B_WHITE_CONC)
    for z in range(z1, z2 + 1, 2):
        setblock(cmds, x1, wt + 1, z, B_WHITE_CONC)
        setblock(cmds, x2, wt + 1, z, B_WHITE_CONC)

    fill(cmds, ox + 14, oy, z2 - 1, ox + 18, oy + 4, z2, B_AIR)

    th, tr = 16, 4
    for (cx, cz) in [(x1, z1), (x2, z1), (x1, z2), (x2, z2)]:
        round_tower(cmds, cx, cz, oy, th, tr, B_WHITE_CONC, B_QUARTZ)
    round_tower(cmds, ox + 16, oz + 12, oy, th + 6, tr + 1, B_WHITE_CONC, B_QUARTZ)

    setblock(cmds, ox + 16, oy + th + 6 + tr + 2, oz + 12, B_GLOWSTONE)

    for z in range(z1 + 4, z2 - 3, 4):
        setblock(cmds, x1, oy + 4, z, B_GLASS)
        setblock(cmds, x2, oy + 4, z, B_GLASS)
    setblock(cmds, x1 + 4, oy + 1, z1 + 4, B_TORCH)
    setblock(cmds, x2 - 4, oy + 1, z2 - 4, B_TORCH)
    return cmds


# --------------------------------------------------------------------------- #
# 2) COLONNES ROMAINES
# --------------------------------------------------------------------------- #
def build_colonnes():
    cmds = []
    comment(cmds, "=== COLONNES ROMAINES ===")
    comment(cmds, "3 colonnes sur esplanade en pierre + marronniers")
    ox, oy, oz = ORIGIN_X + 60, ORIGIN_Y, ORIGIN_Z

    fill(cmds, ox, oy - 1, oz, ox + 24, oy - 1, oz + 16, B_STONE_BRICK)
    fill(cmds, ox + 1, oy, oz + 1, ox + 23, oy, oz + 15, B_SANDSTONE)

    ch = 9
    for (cx, cz) in [(ox + 6, oz + 8), (ox + 12, oz + 8), (ox + 18, oz + 8)]:
        fill(cmds, cx - 1, oy, cz - 1, cx + 1, oy, cz + 1, B_STONE_BRICK)
        fill(cmds, cx, oy + 1, cz, cx, oy + ch, cz, B_QUARTZ)
        fill(cmds, cx - 1, oy + ch + 1, cz - 1, cx + 1, oy + ch + 1, cz + 1, B_QUARTZ)
    fill(cmds, ox + 5, oy + ch + 2, oz + 8, ox + 19, oy + ch + 2, oz + 8, B_SANDSTONE)

    for (tx, tz) in [(ox + 2, oz + 2), (ox + 22, oz + 2),
                     (ox + 2, oz + 14), (ox + 22, oz + 14)]:
        fill(cmds, tx, oy, tz, tx, oy + 4, tz, B_OAK_LOG)
        fill(cmds, tx - 2, oy + 5, tz - 2, tx + 2, oy + 6, tz + 2, B_LEAVES)
        setblock(cmds, tx, oy + 7, tz, B_LEAVES)
    return cmds


# --------------------------------------------------------------------------- #
# 3) PORT / LAC LEMAN
# --------------------------------------------------------------------------- #
def build_port():
    cmds = []
    comment(cmds, "=== PORT DU LAC LEMAN ===")
    comment(cmds, "Plan d'eau, quai/promenade, petit port avec jetees")
    ox, oy, oz = ORIGIN_X, ORIGIN_Y, ORIGIN_Z + 40

    fill(cmds, ox - 10, oy - 4, oz, ox + 80, oy - 1, oz + 60, B_WATER)
    fill(cmds, ox - 10, oy - 5, oz, ox + 80, oy - 5, oz + 60, B_STONE)

    fill(cmds, ox - 10, oy - 1, oz - 4, ox + 80, oy - 1, oz - 1, B_STONE_BRICK)
    fill(cmds, ox - 10, oy, oz - 4, ox + 80, oy, oz - 4, B_COBBLE)

    for x in range(ox, ox + 80, 10):
        fill(cmds, x, oy, oz - 2, x, oy + 3, oz - 2, B_COBBLE)
        setblock(cmds, x, oy + 4, oz - 2, B_GLOWSTONE)

    for jx in (ox + 20, ox + 50):
        fill(cmds, jx, oy - 1, oz, jx + 1, oy - 1, oz + 18, B_SPRUCE_PLK)
        for jz in range(oz, oz + 19, 3):
            fill(cmds, jx, oy - 3, jz, jx, oy - 1, jz, B_SPRUCE_LOG)

    fill(cmds, ox + 35, oy - 1, oz, ox + 35, oy, oz + 22, B_STONE_BRICK)

    for (bx, bz) in [(ox + 25, oz + 8), (ox + 40, oz + 6)]:
        fill(cmds, bx, oy - 1, bz, bx + 2, oy - 1, bz + 4, B_DARK_OAK)
    return cmds


# --------------------------------------------------------------------------- #
# 4) VIEILLE VILLE
# --------------------------------------------------------------------------- #
def build_vieille_ville():
    cmds = []
    comment(cmds, "=== VIEILLE VILLE ===")
    comment(cmds, "Maisons pierre+sapin a toits pentus le long d'une ruelle")
    ox, oy, oz = ORIGIN_X - 50, ORIGIN_Y, ORIGIN_Z

    fill(cmds, ox, oy - 1, oz, ox + 40, oy - 1, oz + 4, B_COBBLE)

    def maison(cx, cz, w, d, h):
        fill(cmds, cx, oy - 1, cz, cx + w, oy - 1, cz + d, B_STONE_BRICK)
        fill(cmds, cx, oy, cz, cx + w, oy + h, cz, B_STONE_BRICK)
        fill(cmds, cx, oy, cz + d, cx + w, oy + h, cz + d, B_STONE_BRICK)
        fill(cmds, cx, oy, cz, cx, oy + h, cz + d, B_STONE_BRICK)
        fill(cmds, cx + w, oy, cz, cx + w, oy + h, cz + d, B_STONE_BRICK)
        fill(cmds, cx + 1, oy, cz + 1, cx + w - 1, oy + h, cz + d - 1, B_AIR)
        fill(cmds, cx, oy + h, cz, cx + w, oy + h, cz + d, B_SPRUCE_LOG)
        for k in range((w // 2) + 1):
            y = oy + h + 1 + k
            fill(cmds, cx + k, y, cz - 1, cx + k, y, cz + d + 1, B_SPRUCE_PLK)
            fill(cmds, cx + w - k, y, cz - 1, cx + w - k, y, cz + d + 1, B_SPRUCE_PLK)
        fill(cmds, cx + w // 2, oy, cz, cx + w // 2, oy + 1, cz, B_AIR)
        setblock(cmds, cx + 1, oy + 1, cz, B_GLASS)
        setblock(cmds, cx + w - 1, oy + 1, cz, B_GLASS)
        setblock(cmds, cx + w // 2, oy + 2, cz - 1, B_TORCH)

    x = ox + 2
    for i in range(5):
        maison(x, oz - 8, 6, 5, 4 + (i % 2))
        maison(x, oz + 6, 6, 5, 5 - (i % 2))
        x += 8

    fx, fz = ox + 40, oz + 2
    fill(cmds, fx, oy, fz, fx + 2, oy, fz + 2, B_STONE_BRICK)
    setblock(cmds, fx + 1, oy + 1, fz + 1, B_WATER)
    return cmds


# --------------------------------------------------------------------------- #
# 5) FONCTION PRINCIPALE
# --------------------------------------------------------------------------- #
def build_main():
    cmds = []
    comment(cmds, "=== NYON — FONCTION PRINCIPALE ===")
    cmds.append("say Reconstruction de NYON en cours...")
    cmds.append("function chateau")
    cmds.append("function colonnes_romaines")
    cmds.append("function port_leman")
    cmds.append("function vieille_ville")
    cmds.append("say NYON reconstruite ! Bienvenue au bord du Leman.")
    return cmds


# --------------------------------------------------------------------------- #
# Ecriture
# --------------------------------------------------------------------------- #
def write_function(name, cmds):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + ".mcfunction")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(cmds) + "\n")
    return path, len(cmds)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    builds = {
        "chateau": build_chateau(),
        "colonnes_romaines": build_colonnes(),
        "port_leman": build_port(),
        "vieille_ville": build_vieille_ville(),
        "nyon": build_main(),
    }
    print(f"Generation des .mcfunction dans : {OUT_DIR}")
    for name, cmds in builds.items():
        path, n = write_function(name, cmds)
        print(f"  - {name}.mcfunction  ({n} lignes)  -> {path}")
    print("Termine. Importez 'functions' dans un behavior pack Bedrock.")


if __name__ == "__main__":
    main()
