#!/usr/bin/env python3
"""Europa-Park OSM -> Minecraft Bedrock .mcfunction/.mcaddon source.

Reconstruction géographiquement fidèle et stylisée à partir d'OpenStreetMap:
- bâtiments extrudés + toits
- chemins/routes
- eau
- rails/roller coasters en lignes colorées
- zones de parc/attractions

Limite: ce n'est pas une copie texturée/photographique des attractions.
"""
from __future__ import annotations

import argparse
import json
import math
import zipfile
import uuid
import zlib
import struct
from pathlib import Path
from collections import defaultdict

GROUND_Y = 63
ORIGIN_X = 0
ORIGIN_Z = 0
MAX_CMDS = 8500

M_GROUND = "grass_block"
M_PATH = "sandstone"
M_ROAD = "stone"
M_WATER = "water"
M_PARK = "green_wool"
M_COASTER = "red_concrete"
M_RAIL = "iron_block"
M_BUILDING = "smooth_quartz"
M_ROOF = "red_sandstone"
M_SHOP = "bricks"
M_HOTEL = "white_concrete"
M_SERVICE = "smooth_stone"
M_AMENITY = "yellow_concrete"
M_WINDOW = "glass_pane"
M_TREE_TRUNK = "oak_log"
M_TREE_LEAVES = "oak_leaves"
M_LAMP = "glowstone"


def stable_hash(x, z, salt=0):
    return (x * 73856093 + z * 19349663 + salt * 83492791) & 0xffffffff


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def bbox_from_elements(elements):
    lats=[]; lons=[]
    for e in elements:
        for p in e.get("geometry") or []:
            lats.append(p["lat"]); lons.append(p["lon"])
    return min(lats), min(lons), max(lats), max(lons)


def projector(bbox):
    min_lat, min_lon, max_lat, max_lon = bbox
    lat0 = (min_lat + max_lat) / 2
    m_lat = 111_320
    m_lon = 111_320 * math.cos(math.radians(lat0))
    def project(lat, lon):
        x = int(round((lon - min_lon) * m_lon))
        z = int(round((max_lat - lat) * m_lat))
        return x, z
    width = int(round((max_lon - min_lon) * m_lon)) + 1
    depth = int(round((max_lat - min_lat) * m_lat)) + 1
    return project, width, depth


def bresenham(x0,z0,x1,z1):
    pts=[]; dx=abs(x1-x0); dz=-abs(z1-z0)
    sx=1 if x0<x1 else -1; sz=1 if z0<z1 else -1
    err=dx+dz; x=x0; z=z0
    while True:
        pts.append((x,z))
        if x==x1 and z==z1: break
        e2=2*err
        if e2>=dz:
            err+=dz; x+=sx
        if e2<=dx:
            err+=dx; z+=sz
    return pts


def thick_line(points, width):
    cells=set(); r=max(0,width//2)
    for (x0,z0),(x1,z1) in zip(points, points[1:]):
        for x,z in bresenham(x0,z0,x1,z1):
            for dx in range(-r,r+1):
                for dz in range(-r,r+1):
                    if dx*dx+dz*dz <= r*r+1:
                        cells.add((x+dx,z+dz))
    return cells


def polygon_edges(poly):
    cells=set()
    if len(poly)<2: return cells
    pts=poly+[poly[0]] if poly[0]!=poly[-1] else poly
    for a,b in zip(pts, pts[1:]):
        cells.update(bresenham(a[0],a[1],b[0],b[1]))
    return cells


def point_in_poly(x,z,poly):
    inside=False; n=len(poly); j=n-1
    for i in range(n):
        xi,zi=poly[i]; xj,zj=poly[j]
        if ((zi>z)!=(zj>z)) and (x < (xj-xi)*(z-zi)/(zj-zi+1e-9)+xi):
            inside=not inside
        j=i
    return inside


def fill_polygon(poly, limit_area=250_000):
    if len(poly)<3: return set()
    xs=[p[0] for p in poly]; zs=[p[1] for p in poly]
    minx,maxx=max(min(xs),0),max(xs); minz,maxz=max(min(zs),0),max(zs)
    area=(maxx-minx+1)*(maxz-minz+1)
    if area>limit_area:
        return set(polygon_edges(poly))
    cells=set()
    for z in range(minz,maxz+1):
        for x in range(minx,maxx+1):
            if point_in_poly(x+0.5,z+0.5,poly):
                cells.add((x,z))
    return cells


def height_from_tags(tags):
    if tags.get("height"):
        s=str(tags["height"]).replace("m","").replace(",",".").strip()
        try: return max(4, min(60, int(float(s))))
        except: pass
    if tags.get("building:levels"):
        try: return max(4, min(60, int(float(tags["building:levels"]))*3))
        except: pass
    b=str(tags.get("building","")).lower()
    tourism=str(tags.get("tourism","")).lower()
    if tourism in {"hotel","guest_house"} or b=="hotel": return 18
    if b in {"service","garage","shed","roof"}: return 4
    if b in {"commercial","retail"}: return 8
    return 9


def building_material(tags):
    txt=" ".join(str(v).lower() for v in tags.values())
    name=str(tags.get("name","")).lower()
    b=str(tags.get("building","")).lower()
    amenity=str(tags.get("amenity","")).lower()
    tourism=str(tags.get("tourism","")).lower()
    if "hotel" in txt or tourism in {"hotel", "guest_house"}:
        return M_HOTEL, "light_blue_concrete"
    if amenity in {"restaurant", "fast_food", "cafe", "bar"} or "restaurant" in txt or "food" in txt:
        return "terracotta", "orange_concrete"
    if "shop" in tags or "retail" in txt or b in {"retail", "commercial"}:
        return M_SHOP, "brick_slab"
    if "station" in name or "bahnhof" in name:
        return "polished_andesite", "stone_brick_slab"
    if "service" in txt or "garage" in txt or b in {"service", "garage", "shed"}:
        return M_SERVICE, "smooth_stone_slab"
    if "attraction" in tags or "theme_park" in txt:
        return "orange_concrete", "red_sandstone_slab"
    if amenity:
        return M_AMENITY, "yellow_concrete"
    return M_BUILDING, M_ROOF


def highway_width(tags):
    h=tags.get("highway","")
    return {"primary":7,"secondary":6,"tertiary":5,"residential":4,"service":3,"footway":2,"path":2,"pedestrian":4,"cycleway":2,"steps":1}.get(h,2)


def add(cmds, cmd):
    cmds.append(cmd)


def write_png(path: Path, width: int, height: int, rgb_rows):
    raw=b"".join(b"\x00"+bytes(row) for row in rgb_rows)
    def chunk(t,d):
        return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"
    data+=chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,2,0,0,0))
    data+=chunk(b"IDAT",zlib.compress(raw,9))
    data+=chunk(b"IEND",b"")
    path.write_bytes(data)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", default="europa_park_osm_raw.json")
    ap.add_argument("--out", default="generated")
    ap.add_argument("--name", default="europa_park")
    ap.add_argument("--bbox", default="48.2570,7.7080,48.2765,7.7355", help="S,W,N,E")
    args=ap.parse_args()
    here=Path(__file__).resolve().parent
    data=load_json(here/args.input)
    clip_bbox=tuple(float(x) for x in args.bbox.split(','))
    s,w,n,e=clip_bbox
    elements=[]
    for el in data.get("elements",[]):
        geom=el.get("geometry") or []
        clipped=[p for p in geom if s <= p.get("lat",0) <= n and w <= p.get("lon",0) <= e]
        if len(clipped) >= 2:
            ne=dict(el)
            ne["geometry"]=clipped
            elements.append(ne)
    bbox=clip_bbox
    project,width,depth=projector(bbox)

    paths=set(); roads=set(); water=set(); park=set(); rails=set()
    coaster_heights={}
    coaster_supports=set()
    building_wall={}; building_roof={}; window_cells=[]; attraction_points=[]
    tree_cells=set(); lamp_cells=set(); flower_cells=set()
    counts=defaultdict(int)

    for e in elements:
        tags=e.get("tags",{})
        geom=e.get("geometry") or []
        poly=[project(p["lat"],p["lon"]) for p in geom]
        if len(poly)<2: continue
        closed = len(poly)>=4 and poly[0]==poly[-1]
        if "building" in tags:
            counts["building"]+=1
            top=GROUND_Y+height_from_tags(tags)
            mat,roof=building_material(tags)
            edge_cells = polygon_edges(poly)
            for c in edge_cells:
                building_wall[c]=(mat,top)
                x,z=c
                if top >= GROUND_Y + 8 and stable_hash(x,z,3) % 13 == 0:
                    for wy in range(GROUND_Y+4, top, 4):
                        window_cells.append((x,z,wy))
            # roofs/floors limited to avoid exploding on huge roof polygons
            for c in fill_polygon(poly, limit_area=60_000): building_roof[c]=(roof,top+1)
        elif tags.get("natural")=="water" or "waterway" in tags:
            counts["water"]+=1
            water |= fill_polygon(poly, limit_area=180_000)
            water |= thick_line(poly, 4)
        elif "roller_coaster" in tags or tags.get("attraction") in {"roller_coaster","water_slide"}:
            counts["coaster"]+=1
            cells = thick_line(poly, 3)
            for x,z in cells:
                # hauteur stylisée mais déterministe: les rails montent/descendent au lieu d'être plats
                y = GROUND_Y + 8 + int(10 + 10 * math.sin((x * 0.018) + (z * 0.011)))
                coaster_heights[(x,z)] = max(coaster_heights.get((x,z), 0), y)
                if stable_hash(x,z,7) % 19 == 0:
                    coaster_supports.add((x,z,y))
        elif tags.get("railway"):
            counts["railway"]+=1
            rails |= thick_line(poly, 2)
        elif "highway" in tags:
            counts["highway"]+=1
            w=highway_width(tags)
            target=roads if w>=3 else paths
            line_cells = thick_line(poly, w)
            target |= line_cells
            for x,z in line_cells:
                if stable_hash(x,z,19) % 1800 == 0:
                    lamp_cells.add((x,z))
                if w <= 3 and stable_hash(x,z,29) % 2200 == 0:
                    tree_cells.add((x+3,z+3))
                if stable_hash(x,z,31) % 750 == 0:
                    flower_cells.add((x,z))
        elif tags.get("leisure") in {"theme_park","park","water_park","playground","garden"} or tags.get("tourism") in {"theme_park","attraction"}:
            counts["park_area"]+=1
            new_park = fill_polygon(poly, limit_area=200_000)
            park |= new_park
            for x,z in new_park:
                if stable_hash(x,z,11) % 9500 == 0:
                    tree_cells.add((x,z))
        elif "attraction" in tags or "tourism" in tags:
            counts["attraction"]+=1
            xs=[p[0] for p in poly]; zs=[p[1] for p in poly]
            attraction_points.append((sum(xs)//len(xs), sum(zs)//len(zs), tags.get("name") or tags.get("attraction") or "Attraction"))

    out=here/args.out
    func_dir=out/"addon"/"behavior_pack"/"functions"/args.name
    func_dir.mkdir(parents=True, exist_ok=True)
    cmds=[]
    # terrain rows
    for z in range(depth):
        add(cmds, f"fill {ORIGIN_X} {GROUND_Y} {ORIGIN_Z+z} {ORIGIN_X+width} {GROUND_Y} {ORIGIN_Z+z} {M_GROUND}")
    # park underlay
    for x,z in sorted(park - water):
        add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y} {ORIGIN_Z+z} {M_PARK}")
    for x,z in sorted(water):
        add(cmds, f"fill {ORIGIN_X+x} {GROUND_Y} {ORIGIN_Z+z} {ORIGIN_X+x} {GROUND_Y+1} {ORIGIN_Z+z} {M_WATER}")
    for x,z in sorted(paths - water):
        add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y+1} {ORIGIN_Z+z} {M_PATH}")
    for x,z in sorted(roads - water):
        add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y+1} {ORIGIN_Z+z} {M_ROAD}")
    for x,z in sorted(rails - water):
        add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y+2} {ORIGIN_Z+z} {M_RAIL}")
        if stable_hash(x,z,23) % 23 == 0:
            add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y+3} {ORIGIN_Z+z} rail")
    for x,z,y in sorted(coaster_supports):
        if (x,z) not in water and y > GROUND_Y+5:
            add(cmds, f"fill {ORIGIN_X+x} {GROUND_Y+2} {ORIGIN_Z+z} {ORIGIN_X+x} {y-1} {ORIGIN_Z+z} iron_bars")
    for (x,z),y in sorted(coaster_heights.items()):
        if (x,z) not in water:
            add(cmds, f"setblock {ORIGIN_X+x} {y} {ORIGIN_Z+z} {M_COASTER}")
            add(cmds, f"setblock {ORIGIN_X+x} {y+1} {ORIGIN_Z+z} rail")
    for x,z in sorted(tree_cells - water - roads - paths):
        add(cmds, f"fill {ORIGIN_X+x} {GROUND_Y+1} {ORIGIN_Z+z} {ORIGIN_X+x} {GROUND_Y+4} {ORIGIN_Z+z} {M_TREE_TRUNK}")
        add(cmds, f"fill {ORIGIN_X+x-2} {GROUND_Y+5} {ORIGIN_Z+z-2} {ORIGIN_X+x+2} {GROUND_Y+7} {ORIGIN_Z+z+2} {M_TREE_LEAVES}")
    for x,z in sorted(lamp_cells - water):
        add(cmds, f"fill {ORIGIN_X+x} {GROUND_Y+2} {ORIGIN_Z+z} {ORIGIN_X+x} {GROUND_Y+5} {ORIGIN_Z+z} fence")
        add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y+6} {ORIGIN_Z+z} {M_LAMP}")
    flower_palette = ["red_tulip", "orange_tulip", "azure_bluet", "oxeye_daisy", "poppy"]
    for x,z in sorted(flower_cells - water - roads):
        add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y+2} {ORIGIN_Z+z} {flower_palette[stable_hash(x,z,37)%len(flower_palette)]}")
    for (x,z),(mat,top) in sorted(building_wall.items()):
        add(cmds, f"fill {ORIGIN_X+x} {GROUND_Y+1} {ORIGIN_Z+z} {ORIGIN_X+x} {top} {ORIGIN_Z+z} {mat}")
    for (x,z),(mat,y) in sorted(building_roof.items()):
        add(cmds, f"setblock {ORIGIN_X+x} {y} {ORIGIN_Z+z} {mat}")
    for x,z,wy in window_cells:
        add(cmds, f"setblock {ORIGIN_X+x} {wy} {ORIGIN_Z+z} {M_WINDOW}")
    # Mark named attractions with beacon-like towers/titles in limited count
    for i,(x,z,name) in enumerate(attraction_points[:80]):
        safe=str(name).replace('"','')[:40]
        add(cmds, f"fill {ORIGIN_X+x} {GROUND_Y+1} {ORIGIN_Z+z} {ORIGIN_X+x} {GROUND_Y+8} {ORIGIN_Z+z} blue_stained_glass")
        add(cmds, f"setblock {ORIGIN_X+x} {GROUND_Y+9} {ORIGIN_Z+z} sea_lantern")
        add(cmds, f'tellraw @a {{"rawtext":[{{"text":"Attraction Europa-Park: {safe}"}}]}}')

    # Split
    parts=[]
    for i in range(0,len(cmds),MAX_CMDS):
        part=cmds[i:i+MAX_CMDS]
        path=func_dir/f"{args.name}_part{i//MAX_CMDS:03d}.mcfunction"
        path.write_text("\n".join(part)+"\n", encoding="utf-8")
        parts.append(path)
    master=out/"addon"/"behavior_pack"/"functions"/f"build_{args.name}.mcfunction"
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("\n".join([f"function {args.name}/{p.stem}" for p in parts]+[
        'title @a title Europa-Park',
        'title @a subtitle Reconstruction OSM stylisee - fonctions terminees'
    ])+"\n", encoding="utf-8")
    start=out/"addon"/"behavior_pack"/"functions"/"start_europa_park.mcfunction"
    start.write_text('tellraw @a {"rawtext":[{"text":"Europa-Park: lance /function build_europa_park pour construire le parc."}]}\n', encoding="utf-8")

    manifest={
        "format_version":2,
        "header":{"name":"Europa-Park Réaliste (OSM)","description":"Reconstruction stylisée d'Europa-Park depuis OpenStreetMap","uuid":str(uuid.uuid4()),"version":[1,0,0],"min_engine_version":[1,20,0]},
        "modules":[{"type":"data","uuid":str(uuid.uuid4()),"version":[1,0,0]}]
    }
    bp=out/"addon"/"behavior_pack"; bp.mkdir(parents=True, exist_ok=True)
    (bp/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2), encoding="utf-8")

    stats={
        "bbox":bbox,"width_blocks":width,"depth_blocks":depth,"commands":len(cmds),"parts":len(parts),"counts":dict(counts),
        "realism_upgrades":{
            "classified_building_materials": True,
            "window_facades": len(window_cells),
            "variable_height_coasters": len(coaster_heights),
            "coaster_supports": len(coaster_supports),
            "trees": len(tree_cells),
            "path_lamps": len(lamp_cells),
            "landscape_trees": len(tree_cells),
            "flower_beds": len(flower_cells),
            "attraction_markers": min(len(attraction_points),80),
        },
        "source":"OpenStreetMap ODbL","scale":"1 block = 1 metre"}
    (out/"build_stats.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2), encoding="utf-8")

    # Preview, scaled down
    scale=max(1, math.ceil(max(width,depth)/1200))
    pw=width//scale+1; ph=depth//scale+1
    img=[[(120,170,90) for _ in range(pw)] for __ in range(ph)]
    def paint(cells,color):
        for x,z in cells:
            px=x//scale; pz=z//scale
            if 0<=px<pw and 0<=pz<ph: img[pz][px]=color
    paint(park,(80,190,90)); paint(water,(45,120,210)); paint(paths,(210,190,135)); paint(roads,(55,55,55)); paint(rails,(200,200,210)); paint(set(coaster_heights.keys()),(220,40,40)); paint(set(building_roof.keys()),(220,140,65)); paint(set(building_wall.keys()),(245,220,180)); paint(tree_cells,(30,120,45)); paint(flower_cells,(255,80,180)); paint(lamp_cells,(255,240,100))
    rows=[]
    for row in img:
        flat=[]
        for r,g,b in row: flat.extend([r,g,b])
        rows.append(flat)
    write_png(out/"europa-park-preview.png", pw, ph, rows)

    print(json.dumps(stats, ensure_ascii=False))

if __name__ == "__main__":
    main()
