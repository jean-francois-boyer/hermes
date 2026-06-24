#!/usr/bin/env python3
from pathlib import Path
import zipfile, json

HERE = Path(__file__).resolve().parent
GEN = HERE / 'generated' / 'addon'
OUT = HERE.parent / 'export'
OUT.mkdir(parents=True, exist_ok=True)
mcaddon = OUT / 'europa-park-realiste.mcaddon'
with zipfile.ZipFile(mcaddon, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in (GEN / 'behavior_pack').rglob('*'):
        if p.is_file():
            z.write(p, p.relative_to(GEN))
print(mcaddon)
