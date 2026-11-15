"""Fetch pinned viewer assets (run once; files are checked in)."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'atlas'
NE_REV = 'v5.1.2'
assets = {
    'vendor/maplibre-gl.js': 'https://unpkg.com/maplibre-gl@5.6.2/dist/maplibre-gl.js',
    'vendor/maplibre-gl.css': 'https://unpkg.com/maplibre-gl@5.6.2/dist/maplibre-gl.css',
    'vendor/MAPLIBRE-LICENSE.txt': 'https://unpkg.com/maplibre-gl@5.6.2/LICENSE.txt',
    'data/land.geojson': f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{NE_REV}/geojson/ne_110m_land.geojson',
}
for relative, url in assets.items():
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        path.write_bytes(response.read())
    print(relative, path.stat().st_size)
metadata = dict(title='Natural Earth 1:110m land', revision=NE_REV, url=assets['data/land.geojson'],
                licence='Public domain', sha256=hashlib.sha256((ROOT / 'data/land.geojson').read_bytes()).hexdigest())
(ROOT / 'data/basemap-source.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
