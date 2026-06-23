#!/usr/bin/env python3
"""
osm_to_minecraft.py — Convertit des données OpenStreetMap réelles en monde
Minecraft Bedrock (.mcfunction) à l'échelle 1 bloc = 1 mètre.

Source de données: OpenStreetMap (licence ODbL).
Cible: Minecraft Bedrock Edition (compatible Switch via Realms).

Pipeline:
  1. Parse le JSON Overpass (way building/highway/water avec geometry).
  2. Projette lat/lon -> mètres locaux (équirectangulaire centrée sur la bbox).
  3. Rasterise:
       - terrain de base (herbe) + plage/quai
       - lac Léman (eau) au sud
       - routes (chemin de pierre)
       - empreintes de bâtiments (murs en pierre, extrudés selon hauteur OSM)
  4. Écrit des .mcfunction découpées en tuiles pour rester sous les limites
     de commandes par fonction.
"""
import json
import math
import argparse
from pathlib import Path
from collections import defaultdict

# --- Paramètres monde ---
GROUND_Y = 63          # niveau du sol (niveau de la mer Bedrock par défaut)
WATER_Y = 62           # surface de l'eau
DEFAULT_LEVELS = 3     # étages par défaut si pas de hauteur OSM
LEVEL_HEIGHT = 3       # blocs par étage
ORIGIN_X = 0           # offset monde
ORIGIN_Z = 0

# Matériaux Bedrock
M_GROUND = "grass_block"
M_ROAD = "stone"
M_PATH = "gravel"
M_WATER = "water"
M_WALL_DEFAULT = "stone_bricks"
M_WALL_OLD = "cobblestone"      # vieille ville / château
M_ROOF = "dark_oak_planks"
M_SAND = "sand"


def classify_building(tags):
    """Retourne (matériau_mur, matériau_toit) selon le type réel OSM."""
    t = tags or {}
    b = str(t.get("building", "")).lower()
    blob = " ".join(str(v).lower() for v in t.values())

    # Château / patrimoine / vieille ville
    if "castle" in blob or t.get("historic") or b in ("castle", "tower"):
        return ("cobblestone", "stone_brick_slab")
    # Église / lieu de culte
    if t.get("amenity") == "place_of_worship" or b in ("church", "chapel", "cathedral") or "place_of_worship" in blob:
        return ("quartz_block", "deepslate_tile_slab")
    # Commerce / commercial / retail
    if b in ("commercial", "retail") or t.get("shop"):
        return ("bricks", "brick_slab")
    # Industriel / entrepôt / hangar
    if b in ("industrial", "warehouse", "hangar", "shed", "garage", "garages"):
        return ("smooth_stone", "iron_block")
    # Public / école / hôpital / gare
    if b in ("public", "school", "hospital", "civic", "government", "train_station") or t.get("amenity") in ("school", "hospital", "townhall"):
        return ("stone_bricks", "polished_andesite_slab")
    # Résidentiel (maisons, immeubles)
    if b in ("house", "detached", "residential", "apartments", "terrace", "bungalow", "villa", "yes"):
        return ("bricks", "dark_oak_planks")
    return (M_WALL_DEFAULT, M_ROOF)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="nyon_osm_raw.json")
    p.add_argument("--out", default="generated")
    p.add_argument("--max-cmds", type=int, default=9000,
                   help="commandes max par .mcfunction")
    p.add_argument("--name", default="nyon")
    return p.parse_args()


def load_osm(path):
    data = json.load(open(path))
    return data["elements"]


def compute_bounds(elements):
    lats, lons = [], []
    for el in elements:
        for pt in el.get("geometry", []) or []:
            if pt and "lat" in pt:
                lats.append(pt["lat"])
                lons.append(pt["lon"])
    return min(lats), min(lons), max(lats), max(lons)


def make_projector(min_lat, min_lon, max_lat, max_lon):
    """Projection équirectangulaire -> mètres, origine au coin SW."""
    lat0 = (min_lat + max_lat) / 2.0
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(lat0))

    def project(lat, lon):
        x = (lon - min_lon) * m_per_deg_lon   # est = +X
        z = (max_lat - lat) * m_per_deg_lat   # sud = +Z (nord en haut)
        return x, z

    width = (max_lon - min_lon) * m_per_deg_lon
    depth = (max_lat - min_lat) * m_per_deg_lat
    return project, width, depth


def building_height(tags):
    if not tags:
        return DEFAULT_LEVELS * LEVEL_HEIGHT
    h = tags.get("height")
    if h:
        try:
            return max(3, int(round(float(str(h).replace("m", "").strip()))))
        except ValueError:
            pass
    lv = tags.get("building:levels")
    if lv:
        try:
            return max(3, int(round(float(lv))) * LEVEL_HEIGHT)
        except ValueError:
            pass
    return DEFAULT_LEVELS * LEVEL_HEIGHT


def polygon_edges_cells(poly):
    """Bresenham sur chaque arête -> ensemble de cellules (contour)."""
    cells = set()
    n = len(poly)
    for i in range(n):
        x0, z0 = poly[i]
        x1, z1 = poly[(i + 1) % n]
        cells |= bresenham(int(round(x0)), int(round(z0)),
                           int(round(x1)), int(round(z1)))
    return cells


def bresenham(x0, z0, x1, z1):
    cells = set()
    dx = abs(x1 - x0)
    dz = abs(z1 - z0)
    sx = 1 if x0 < x1 else -1
    sz = 1 if z0 < z1 else -1
    err = dx - dz
    while True:
        cells.add((x0, z0))
        if x0 == x1 and z0 == z1:
            break
        e2 = 2 * err
        if e2 > -dz:
            err -= dz
            x0 += sx
        if e2 < dx:
            err += dx
            z0 += sz
    return cells


def thick_line(poly, half):
    """Route épaisse: cellules du tracé + voisinage (rayon `half`)."""
    base = set()
    n = len(poly)
    for i in range(n - 1):
        x0, z0 = poly[i]
        x1, z1 = poly[i + 1]
        base |= bresenham(int(round(x0)), int(round(z0)),
                          int(round(x1)), int(round(z1)))
    if half <= 0:
        return base
    out = set()
    for (x, z) in base:
        for dx in range(-half, half + 1):
            for dz in range(-half, half + 1):
                if dx * dx + dz * dz <= half * half + 1:
                    out.add((x + dx, z + dz))
    return out


ROAD_WIDTH = {
    "motorway": 4, "trunk": 4, "primary": 3, "secondary": 3,
    "tertiary": 2, "residential": 2, "unclassified": 2, "service": 1,
    "living_street": 2, "pedestrian": 1, "footway": 0, "path": 0,
    "track": 1, "cycleway": 0, "steps": 0,
}


def main():
    args = parse_args()
    here = Path(__file__).resolve().parent
    elements = load_osm(here / args.input)
    min_lat, min_lon, max_lat, max_lon = compute_bounds(elements)
    project, width, depth = make_projector(min_lat, min_lon, max_lat, max_lon)
    W = int(math.ceil(width))
    D = int(math.ceil(depth))

    # Grilles
    height_map = {}      # (x,z) -> top block material override (eau, sable...)
    road_cells = set()
    water_cells = set()
    building_wall = {}   # (x,z) -> (material, top_y)
    building_floor = set()
    roof_cells = {}      # (x,z) -> (roof_material, top_y)

    n_build = n_road = n_water = 0

    def fill_clipped(poly):
        """fill_polygon mais en clippant les rangées au monde [0..W]x[0..D]."""
        cells = set()
        for (x, z) in fill_polygon_bounded(poly, 0, D):
            if 0 <= x <= W and 0 <= z <= D:
                cells.add((x, z))
        return cells

    for el in elements:
        et = el.get("type")
        tags = el.get("tags", {}) or {}

        # --- Relations multipolygon (ex: lac Léman) ---
        if et == "relation":
            is_water = (tags.get("natural") == "water"
                        or tags.get("water")
                        or tags.get("waterway"))
            if not is_water:
                continue
            # Récupère les segments du contour extérieur
            segs = []
            for m in el.get("members", []) or []:
                if m.get("role") != "outer":
                    continue
                g = m.get("geometry") or []
                if len(g) >= 2:
                    segs.append([project(p["lat"], p["lon"]) for p in g])
            # Stitch les segments en anneaux fermés
            for ring in stitch_rings(segs):
                if len(ring) >= 3:
                    n_water += 1
                    water_cells |= fill_clipped(ring)
            continue

        if et != "way":
            continue
        geom = el.get("geometry") or []
        if len(geom) < 2:
            continue
        poly = [project(p["lat"], p["lon"]) for p in geom]

        if "building" in tags:
            n_build += 1
            top = GROUND_Y + building_height(tags)
            wall_mat, roof_mat = classify_building(tags)
            for c in polygon_edges_cells(poly):
                building_wall[c] = (wall_mat, top)
            # plancher + toit = contour rempli (scanline simple)
            floor = fill_polygon(poly)
            building_floor |= floor
            for c in floor:
                roof_cells[c] = (roof_mat, top)
        elif "highway" in tags:
            n_road += 1
            hw = tags.get("highway", "residential")
            half = ROAD_WIDTH.get(hw, 1)
            road_cells |= thick_line(poly, half)
        elif tags.get("natural") == "water" or "waterway" in tags:
            n_water += 1
            water_cells |= fill_polygon(poly)

    # Lac Léman: la relation OSM du lac est énorme et n'est pas remplie comme
    # simple way dans Overpass. On charge la relation 332617 clippée à la bbox,
    # on reconstruit la ligne de rive visible, puis on remplit l'eau vers le sud
    # de cette rive (côté lac) avec des spans X -> Z.
    lake_z_by_x = {}
    lake_relation = here / "lake_geneva_relation.json"
    if lake_relation.exists():
        try:
            lake_data = json.loads(lake_relation.read_text())
            rel = lake_data.get("elements", [{}])[0]
            for member in rel.get("members", []):
                geom = member.get("geometry") or []
                pts = []
                for p in geom:
                    if p and "lat" in p and "lon" in p:
                        pts.append(project(p["lat"], p["lon"]))
                for i in range(len(pts) - 1):
                    x0, z0 = pts[i]
                    x1, z1 = pts[i + 1]
                    for x, z in bresenham(int(round(x0)), int(round(z0)), int(round(x1)), int(round(z1))):
                        if 0 <= x <= W and -5 <= z <= D + 5:
                            # garder la rive la plus au sud pour éviter de remplir
                            # les segments de clipping du polygone du lac.
                            lake_z_by_x[x] = max(lake_z_by_x.get(x, -10**9), z)
        except Exception as exc:
            print(f"WARN lake relation ignored: {exc}")

    def in_lake(x, z):
        shore = lake_z_by_x.get(x)
        return shore is not None and z >= shore

    lake_span_count = len(lake_z_by_x)

    # --- Construire les commandes ---
    out_dir = here / args.out
    func_dir = out_dir / "addon" / "behavior_pack" / "functions" / args.name
    func_dir.mkdir(parents=True, exist_ok=True)

    # --- Relief réel (SRTM) si disponible ---
    elev_path = here / "elevation_grid.json"
    terrain_y = None
    min_elev = None
    if elev_path.exists():
        ed = json.loads(elev_path.read_text())
        grid = ed["elevation"]
        gsize = ed["grid_size"]
        min_elev = ed["min_elev"]
        m_per_deg_lat = 111320.0
        lat0c = (min_lat + max_lat) / 2.0
        m_per_deg_lon = 111320.0 * math.cos(math.radians(lat0c))

        def terrain_y(x, z):
            # world x,z -> lat,lon
            lon = min_lon + x / m_per_deg_lon
            lat = max_lat - z / m_per_deg_lat
            fi = (lat - min_lat) / (max_lat - min_lat) * (gsize - 1)
            fj = (lon - min_lon) / (max_lon - min_lon) * (gsize - 1)
            fi = min(max(fi, 0), gsize - 1)
            fj = min(max(fj, 0), gsize - 1)
            i0, j0 = int(fi), int(fj)
            i1, j1 = min(i0 + 1, gsize - 1), min(j0 + 1, gsize - 1)
            di, dj = fi - i0, fj - j0
            e = (grid[i0][j0] * (1 - di) * (1 - dj)
                 + grid[i0][j1] * (1 - di) * dj
                 + grid[i1][j0] * di * (1 - dj)
                 + grid[i1][j1] * di * dj)
            return GROUND_Y + int(round(e - min_elev))

    def ground_top(x, z):
        return terrain_y(x, z) if terrain_y else GROUND_Y

    commands = []

    def add(cmd):
        commands.append(cmd)

    BASE_Y = GROUND_Y - 4  # fond de terre commun

    if terrain_y:
        # 1. Terrain en relief par tuiles 16x16 (plateformes interpolées)
        TILE = 16
        for tz in range(0, D + 1, TILE):
            for tx in range(0, W + 1, TILE):
                cx = min(tx + TILE // 2, W)
                cz = min(tz + TILE // 2, D)
                ty = ground_top(cx, cz)
                x0, x1 = ORIGIN_X + tx, ORIGIN_X + min(tx + TILE - 1, W)
                z0, z1 = ORIGIN_Z + tz, ORIGIN_Z + min(tz + TILE - 1, D)
                # corps de terre puis herbe au sommet
                add(f"fill {x0} {BASE_Y} {z0} {x1} {ty-1} {z1} dirt")
                add(f"fill {x0} {ty} {z0} {x1} {ty} {z1} {M_GROUND}")
    else:
        # Terrain plat (fallback sans relief)
        for z in range(0, D + 1):
            add(f"fill {ORIGIN_X} {GROUND_Y} {ORIGIN_Z+z} {ORIGIN_X+W} {GROUND_Y} {ORIGIN_Z+z} {M_GROUND}")

    # 2. Eau (petits cours d'eau) — surface au niveau du terrain local
    for (x, z) in sorted(water_cells):
        gy = ground_top(x, z)
        add(f"fill {ORIGIN_X+x} {gy} {ORIGIN_Z+z} {ORIGIN_X+x} {gy} {ORIGIN_Z+z} {M_WATER}")

    # 2b. Lac Léman — grands spans depuis la rive jusqu'au sud de la bbox
    for x, shore_z in sorted(lake_z_by_x.items()):
        z0 = max(0, min(D, shore_z))
        z1 = D
        gy = ground_top(x, z0)
        add(f"fill {ORIGIN_X+x} {gy} {ORIGIN_Z+z0} {ORIGIN_X+x} {gy} {ORIGIN_Z+z1} {M_WATER}")

    # 3. Routes (posées sur le relief, hors lac)
    for (x, z) in sorted(road_cells):
        if (x, z) in water_cells or in_lake(x, z):
            continue
        add(f"setblock {ORIGIN_X+x} {ground_top(x, z)} {ORIGIN_Z+z} {M_ROAD}")

    # 4. Planchers bâtiments (sur le relief, hors lac)
    for (x, z) in sorted(building_floor):
        if in_lake(x, z):
            continue
        add(f"setblock {ORIGIN_X+x} {ground_top(x, z)} {ORIGIN_Z+z} stone")

    # 5. Murs bâtiments (extrusion depuis le sol local, hors lac)
    for (x, z), (mat, top) in sorted(building_wall.items()):
        if in_lake(x, z):
            continue
        gy = ground_top(x, z)
        add(f"fill {ORIGIN_X+x} {gy+1} {ORIGIN_Z+z} {ORIGIN_X+x} {gy+(top-GROUND_Y)} {ORIGIN_Z+z} {mat}")

    # 6. Toits (couvercle au sommet, suit le relief, hors lac)
    for (x, z), (rmat, top) in sorted(roof_cells.items()):
        if in_lake(x, z):
            continue
        gy = ground_top(x, z)
        add(f"setblock {ORIGIN_X+x} {gy+(top-GROUND_Y)+1} {ORIGIN_Z+z} {rmat}")

    # --- Découper en tuiles sous max-cmds ---
    chunks = [commands[i:i + args.max_cmds]
              for i in range(0, len(commands), args.max_cmds)]
    part_names = []
    for i, ch in enumerate(chunks):
        pname = f"{args.name}_part{i:03d}"
        part_names.append(pname)
        (func_dir / f"{pname}.mcfunction").write_text("\n".join(ch) + "\n")

    # fonction maître qui appelle toutes les parties
    master = [f"function {args.name}/{p}" for p in part_names]
    master_dir = out_dir / "addon" / "behavior_pack" / "functions"
    (master_dir / f"build_{args.name}.mcfunction").write_text(
        "\n".join(master) + "\n")

    stats = {
        "bbox": [min_lat, min_lon, max_lat, max_lon],
        "world_size_blocks": [W, D],
        "buildings": n_build,
        "roads": n_road,
        "water_areas": n_water,
        "total_commands": len(commands),
        "parts": len(part_names),
        "scale": "1 block = 1 metre",
        "source": "OpenStreetMap ODbL",
        "relief": bool(terrain_y),
        "elevation_range_m": (ed["max_elev"] - ed["min_elev"]) if terrain_y else 0,
        "lake_geneva_spans": lake_span_count,
    }
    (out_dir / "build_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2, ensure_ascii=False))


def fill_polygon(poly):
    """Remplissage scanline d'un polygone -> cellules intérieures."""
    return fill_polygon_bounded(poly, None, None)


def stitch_rings(segments, tol=1.5):
    """Chaîne des segments (polylignes) en anneaux fermés.

    Les membres 'outer' d'une relation multipolygon arrivent en désordre et
    fragmentés; on les recolle bout à bout (extrémités proches a <= tol)."""
    segs = [list(s) for s in segments if len(s) >= 2]
    rings = []

    def dist(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    while segs:
        ring = segs.pop(0)
        extended = True
        while extended and segs:
            extended = False
            head, tail = ring[0], ring[-1]
            for i, s in enumerate(segs):
                if dist(tail, s[0]) <= tol:
                    ring.extend(s[1:]); segs.pop(i); extended = True; break
                if dist(tail, s[-1]) <= tol:
                    ring.extend(reversed(s[:-1])); segs.pop(i); extended = True; break
                if dist(head, s[-1]) <= tol:
                    ring[:0] = s[:-1]; segs.pop(i); extended = True; break
                if dist(head, s[0]) <= tol:
                    ring[:0] = list(reversed(s[1:])); segs.pop(i); extended = True; break
        rings.append(ring)
    return rings


def fill_polygon_bounded(poly, zlo, zhi):
    """Remplissage scanline; si zlo/zhi fournis, limite les rangées scannées
    (évite de balayer tout le lac Léman hors zone)."""
    cells = set()
    if len(poly) < 3:
        return cells
    zs = [p[1] for p in poly]
    zmin = int(math.floor(min(zs)))
    zmax = int(math.ceil(max(zs)))
    if zlo is not None:
        zmin = max(zmin, int(zlo))
    if zhi is not None:
        zmax = min(zmax, int(zhi))
    n = len(poly)
    for z in range(zmin, zmax + 1):
        zc = z + 0.5
        inters = []
        for i in range(n):
            x0, z0 = poly[i]
            x1, z1 = poly[(i + 1) % n]
            if (z0 <= zc < z1) or (z1 <= zc < z0):
                t = (zc - z0) / (z1 - z0)
                inters.append(x0 + t * (x1 - x0))
        inters.sort()
        for k in range(0, len(inters) - 1, 2):
            xa = int(math.floor(inters[k]))
            xb = int(math.ceil(inters[k + 1]))
            for x in range(xa, xb + 1):
                cells.add((x, z))
    return cells


if __name__ == "__main__":
    main()
