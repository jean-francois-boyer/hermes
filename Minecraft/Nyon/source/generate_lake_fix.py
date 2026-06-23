#!/usr/bin/env python3
"""Génère behavior_pack/functions/fix_lake_geneva.mcfunction depuis la relation OSM du Léman.
Patch léger: remplit le lac au sud/est de la rive de Nyon sans régénérer tout le monde."""
import json, math
from pathlib import Path
HERE=Path(__file__).resolve().parent
stats=json.load(open(HERE/'generated/build_stats.json'))
min_lat,min_lon,max_lat,max_lon=stats['bbox']
lat0=(min_lat+max_lat)/2
mlon=111320*math.cos(math.radians(lat0)); mlat=111320
W=int(math.ceil((max_lon-min_lon)*mlon)); D=int(math.ceil((max_lat-min_lat)*mlat))

def proj(lat,lon): return (lon-min_lon)*mlon, (max_lat-lat)*mlat

def bresenham(x0,z0,x1,z1):
    pts=[]; dx=abs(x1-x0); dz=abs(z1-z0); sx=1 if x0<x1 else -1; sz=1 if z0<z1 else -1; err=dx-dz
    while True:
        pts.append((x0,z0))
        if x0==x1 and z0==z1: break
        e2=2*err
        if e2>-dz: err-=dz; x0+=sx
        if e2<dx: err+=dx; z0+=sz
    return pts

lake=json.load(open(HERE/'lake_geneva_relation.json'))['elements'][0]
shore={}
for m in lake.get('members',[]):
    pts=[]
    for p in m.get('geometry') or []:
        if p and 'lat' in p and 'lon' in p:
            x,z=proj(p['lat'],p['lon']); pts.append((x,z))
    for i in range(len(pts)-1):
        x0,z0=pts[i]; x1,z1=pts[i+1]
        for x,z in bresenham(int(round(x0)),int(round(z0)),int(round(x1)),int(round(z1))):
            if 0 <= x <= W and -5 <= z <= D+5:
                shore[x]=max(shore.get(x,-10**9), z)

func_dir=HERE/'generated/addon/behavior_pack/functions'
func_dir.mkdir(parents=True, exist_ok=True)
out=func_dir/'fix_lake_geneva.mcfunction'
cmd=[]
cmd.append('title @a actionbar Correction du lac Leman: eau + rive')
# Niveau lac Minecraft: base Y 63, effacement au-dessus jusqu'au relief max 123
WATER_Y=63; CLEAR_TOP=124; CHUNK=350
for x in sorted(shore):
    z0=max(0,min(D,shore[x])); z1=D
    # eau en grands spans
    cmd.append(f'fill {x} {WATER_Y} {z0} {x} {WATER_Y} {z1} water')
    # air au-dessus par morceaux pour respecter les limites de /fill
    a=z0
    while a<=z1:
        b=min(z1,a+CHUNK-1)
        cmd.append(f'fill {x} {WATER_Y+1} {a} {x} {CLEAR_TOP} {b} air')
        a=b+1
out.write_text('\n'.join(cmd)+'\n')
# ajouter l'appel à la fonction maître si absent
master=func_dir/'build_nyon.mcfunction'
if master.exists():
    text=master.read_text()
    line='function fix_lake_geneva'
    if line not in text:
        master.write_text(text.rstrip()+'\n'+line+'\n')
print(json.dumps({'function':str(out),'shore_spans':len(shore),'commands':len(cmd),'world_size':[W,D]},indent=2))
