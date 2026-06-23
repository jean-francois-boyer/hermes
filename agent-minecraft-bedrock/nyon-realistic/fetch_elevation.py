#!/usr/bin/env python3
"""fetch_elevation.py — échantillonne une grille d'altitudes réelles (SRTM 30m)
sur la bbox de Nyon via OpenTopoData, et sauvegarde elevation_grid.json."""
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent

# bbox identique à build_stats (S,W,N,E)
MIN_LAT, MIN_LON = 46.3672638, 6.2276363
MAX_LAT, MAX_LON = 46.3922896, 6.2645758

GRID = 28  # 28x28 = 784 points (< quota 1000/jour)
API = "https://api.opentopodata.org/v1/srtm30m"


def main():
    lats = [MIN_LAT + (MAX_LAT - MIN_LAT) * i / (GRID - 1) for i in range(GRID)]
    lons = [MIN_LON + (MAX_LON - MIN_LON) * j / (GRID - 1) for j in range(GRID)]
    points = [(la, lo) for la in lats for lo in lons]

    elevations = []
    for k in range(0, len(points), 100):
        batch = points[k:k + 100]
        locs = "|".join(f"{la:.6f},{lo:.6f}" for la, lo in batch)
        url = API + "?" + urllib.parse.urlencode({"locations": locs})
        req = urllib.request.Request(url, headers={"User-Agent": "MinecraftNyonGen/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
        assert data["status"] == "OK", data
        for res in data["results"]:
            elevations.append(res["elevation"])
        print(f"  batch {k//100+1}: {len(batch)} points, "
              f"alt {min(e for e in elevations if e is not None):.0f}"
              f"-{max(e for e in elevations if e is not None):.0f} m")
        time.sleep(1.2)  # respecter 1 req/s

    grid = []
    idx = 0
    for i in range(GRID):
        row = []
        for j in range(GRID):
            row.append(elevations[idx])
            idx += 1
        grid.append(row)

    out = {
        "bbox": [MIN_LAT, MIN_LON, MAX_LAT, MAX_LON],
        "grid_size": GRID,
        "lats": lats,
        "lons": lons,
        "elevation": grid,
        "min_elev": min(e for e in elevations if e is not None),
        "max_elev": max(e for e in elevations if e is not None),
        "source": "OpenTopoData SRTM 30m",
    }
    (HERE / "elevation_grid.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({
        "points": len(elevations),
        "min_elev": out["min_elev"],
        "max_elev": out["max_elev"],
        "range_m": out["max_elev"] - out["min_elev"],
    }, indent=2))


if __name__ == "__main__":
    main()
