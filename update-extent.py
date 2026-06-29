#!/usr/bin/env python3
"""
Run after updating tiles to regenerate tiles-extent.json.
Usage: python3 update-extent.py
"""
import math, glob, json

tiles = []
for path in glob.glob('./**/*.webp', recursive=True):
    parts = path.strip('./').split('/')
    if len(parts) == 3:
        z, x, y = int(parts[0]), int(parts[1]), int(parts[2].replace('.webp', ''))
        tiles.append((z, x, y))

if not tiles:
    print("No tiles found.")
    exit(1)

def tile_bounds_3857(x, y, z):
    """Return (west, south, east, north) in EPSG:3857 for a tile."""
    def to_meter(tx, ty, tz):
        n = 2 ** tz
        lon = tx / n * 360 - 180
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ty / n))))
        mx = lon * 20037508.34 / 180
        my = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180) * 20037508.34 / 180
        return mx, my
    w, n = to_meter(x, y, z)
    e, s = to_meter(x + 1, y + 1, z)
    return w, s, e, n

# Use the highest zoom level for the tightest extent
max_z = max(t[0] for t in tiles)
tiles_at_max_z = [(x, y) for z, x, y in tiles if z == max_z]

all_bounds = [tile_bounds_3857(x, y, max_z) for x, y in tiles_at_max_z]
extent = [
    min(b[0] for b in all_bounds),
    min(b[1] for b in all_bounds),
    max(b[2] for b in all_bounds),
    max(b[3] for b in all_bounds),
]

result = {
    "extent": extent,
    "minZoom": min(t[0] for t in tiles),
    "maxZoom": max(t[0] for t in tiles),
}

with open('tiles-extent.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Written tiles-extent.json")
print(f"  extent (EPSG:3857): {[round(v) for v in extent]}")
print(f"  zoom: {result['minZoom']}–{result['maxZoom']}")
