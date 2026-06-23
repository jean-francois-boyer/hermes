#!/usr/bin/env python3
"""preview_map.py — génère une image PNG d'aperçu (vue de dessus) du monde Nyon
à partir des données OSM + relief, sans dépendance externe (PNG via zlib/struct)."""
import json
import math
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "nyon-preview.png"
SCALE = 4  # 1 px = 4 m (image ~709x697)

# Couleurs (R,G,B)
C_WATER = (54, 110, 180)
C_ROAD = (60, 60, 60)
C_BUILD = (190, 120, 90)
C_BUILD_OLD = (140, 100, 70)


def load(name):
    return json.load(open(HERE / name))


def make_projector(min_lat, min_lon, max_lat, max_lon):
    lat0 = (min_lat + max_lat) / 2.0
    mlat = 111320.0
    mlon = 111320.0 * math.cos(math.radians(lat0))

    def project(lat, lon):
        return (lon - min_lon) * mlon, (max_lat - lat) * mlat
    return project, (max_lon - min_lon) * mlon, (max_lat - min_lat) * mlat


def terrain_color(elev, lo, hi):
    """Vert (bas) -> brun -> gris/blanc (haut), façon carte topographique."""
    t = (elev - lo) / (hi - lo) if hi > lo else 0
    if t < 0.5:
        # vert -> jaune-vert
        u = t / 0.5
        return (int(90 + u * 90), int(150 + u * 40), int(70 + u * 20))
    else:
        u = (t - 0.5) / 0.5
        return (int(180 - u * 60), int(190 - u * 90), int(90 + u * 70))


def bresenham(x0, y0, x1, y1):
    pts = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x0 += sx
        if e2 < dx:
            err += dx; y0 += sy
    return pts


def fill_poly(poly, putpix, color, W, H):
    if len(poly) < 3:
        return
    ys = [p[1] for p in poly]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        yc = y + 0.5
        xs = []
        n = len(poly)
        for i in range(n):
            x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % n]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append(x0 + (yc - y0) / (y1 - y0) * (x1 - x0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                putpix(x, y, color)


def write_png(path, W, H, pixels):
    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        row = pixels[y * W * 3:(y + 1) * W * 3]
        raw.extend(row)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    comp = zlib.compress(bytes(raw), 9)
    path.write_bytes(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    osm = load("nyon_osm_raw.json")["elements"]
    ed = load("elevation_grid.json")
    stats = load("generated/build_stats.json")
    min_lat, min_lon, max_lat, max_lon = stats["bbox"]
    project, width, depth = make_projector(min_lat, min_lon, max_lat, max_lon)
    W = int(width / SCALE) + 1
    H = int(depth / SCALE) + 1

    pix = bytearray(W * H * 3)

    def putpix(px, py, color):
        if 0 <= px < W and 0 <= py < H:
            i = (py * W + px) * 3
            pix[i], pix[i + 1], pix[i + 2] = color

    # 1. fond = relief interpolé
    grid = ed["elevation"]; g = ed["grid_size"]
    lo, hi = ed["min_elev"], ed["max_elev"]

    def elev_at(px, py):
        mx, mz = px * SCALE, py * SCALE
        lon = min_lon + mx / (111320.0 * math.cos(math.radians((min_lat+max_lat)/2)))
        lat = max_lat - mz / 111320.0
        fi = min(max((lat - min_lat)/(max_lat-min_lat)*(g-1), 0), g-1)
        fj = min(max((lon - min_lon)/(max_lon-min_lon)*(g-1), 0), g-1)
        i0, j0 = int(fi), int(fj)
        return grid[i0][j0]

    for py in range(H):
        for px in range(W):
            putpix(px, py, terrain_color(elev_at(px, py), lo, hi))

    # 2. eau, routes, bâtiments
    def to_px(lat, lon):
        x, z = project(lat, lon)
        return int(x / SCALE), int(z / SCALE)

    # 2a. Lac Léman: remplir la surface au sud/est de la rive issue de la relation OSM.
    lake_file = HERE / "lake_geneva_relation.json"
    if lake_file.exists():
        lake = json.load(open(lake_file))["elements"][0]
        shore = {}
        for m in lake.get("members", []):
            pts = []
            for p in m.get("geometry") or []:
                if p and "lat" in p and "lon" in p:
                    pts.append(to_px(p["lat"], p["lon"]))
            for i in range(len(pts) - 1):
                for x, y in bresenham(*pts[i], *pts[i + 1]):
                    if 0 <= x < W and -2 <= y < H + 2:
                        shore[x] = max(shore.get(x, -10**9), y)
        for x, y0 in shore.items():
            y0 = max(0, min(H - 1, y0))
            for y in range(y0, H):
                putpix(x, y, C_WATER)

    for el in osm:
        if el.get("type") != "way":
            continue
        geom = el.get("geometry") or []
        if len(geom) < 2:
            continue
        tags = el.get("tags", {}) or {}
        poly = [to_px(p["lat"], p["lon"]) for p in geom]
        if tags.get("natural") == "water" or "waterway" in tags:
            fill_poly(poly, putpix, C_WATER, W, H)
        elif "highway" in tags:
            for i in range(len(poly) - 1):
                for (x, y) in bresenham(*poly[i], *poly[i + 1]):
                    putpix(x, y, C_ROAD)
        elif "building" in tags:
            old = "castle" in str(tags).lower() or tags.get("historic")
            fill_poly(poly, putpix, C_BUILD_OLD if old else C_BUILD, W, H)

    write_png(OUT, W, H, pix)
    print(json.dumps({"image": str(OUT), "size_px": [W, H],
                      "scale": f"1px={SCALE}m"}, indent=2))


if __name__ == "__main__":
    main()
