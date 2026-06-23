#!/usr/bin/env python3
"""package_mcaddon.py — emballe le monde Nyon généré en .mcaddon importable."""
import json
import uuid
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADDON = HERE / "generated" / "addon"
BP = ADDON / "behavior_pack"
EXPORT = HERE / "exports"
EXPORT.mkdir(parents=True, exist_ok=True)


def u():
    return str(uuid.uuid4())


def write_manifest():
    BP.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format_version": 2,
        "header": {
            "name": "Nyon Réaliste (OSM)",
            "description": "Reconstitution réaliste du centre de Nyon (Suisse) à partir de données OpenStreetMap (ODbL). 1 bloc = 1 mètre.",
            "uuid": u(),
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {"type": "data", "uuid": u(), "version": [1, 0, 0]}
        ],
    }
    (BP / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


def main():
    manifest = write_manifest()
    out = EXPORT / "nyon-realiste.mcaddon"
    files = sorted(BP.rglob("*"))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if f.is_file():
                z.write(f, str(Path("behavior_pack") / f.relative_to(BP)))
    # stats
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    n_func = sum(1 for n in names if n.endswith(".mcfunction"))
    print(json.dumps({
        "mcaddon": str(out),
        "size_bytes": out.stat().st_size,
        "files_in_zip": len(names),
        "mcfunction_count": n_func,
        "manifest_name": manifest["header"]["name"],
        "bp_uuid": manifest["header"]["uuid"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
