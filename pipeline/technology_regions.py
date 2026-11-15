"""Stable land reporting chunks and explicitly hypothetical polity coverage.

No network research is performed at runtime or by this reproducible builder.
"""
import json
import math
from pathlib import Path

from shapely.geometry import Point, box, shape, mapping
from shapely.ops import unary_union

from pipeline.package import read_collection
from pipeline.technologies import load_curated, validate

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'atlas/data'
STEP = 5


def cell_id(lon, lat):
    # Canonical half-open bins, with the north/east outer endpoints clamped.
    x = min(71, max(0, math.floor((lon + 180) / STEP)))
    y = min(29, max(0, math.floor((lat + 60) / STEP)))
    return f'{x}:{y}'


def region_name(lon, lat):
    """Navigation groups only: these names do not claim historical boundaries."""
    if lon < -30:
        return 'South America' if lat < 10 else 'Mesoamerica & Caribbean' if lat < 25 else 'North America'
    if lon < 55 and lat < 37:
        return 'North Africa' if lat >= 20 and lon < 35 else 'Africa' if lat < 20 else 'West Asia'
    if lon < 40 and lat >= 37: return 'Europe'
    if lon < 65 and lat < 45: return 'West Asia'
    if 65 <= lon < 95 and 0 <= lat < 40: return 'South Asia'
    if 95 <= lon < 145 and lat >= 20: return 'East Asia' if lat < 55 else 'Central & North Asia'
    if 40 <= lon < 145 and lat >= 40: return 'Central & North Asia'
    if 95 <= lon < 135 and -10 <= lat < 20: return 'Southeast Asia'
    return 'Oceania & Pacific'


def polygons_only(geometry):
    if geometry.geom_type in ('Polygon', 'MultiPolygon'): return geometry
    return unary_union([polygons_only(g) for g in getattr(geometry,'geoms',[])])


def make_cells(land, step=STEP):
    assert step == STEP, 'Cell IDs and labels require the fixed five-degree grid'
    cells = []
    for south in range(-60, 90, step):
        for west in range(-180, 180, step):
            clipped = polygons_only(land.intersection(box(west, south, west + step, south + step)))
            if clipped.is_empty or clipped.area < 0.00001: continue
            anchor = clipped.representative_point()
            region = region_name(anchor.x, anchor.y)
            def degree(n, positive, negative): return f'{abs(n)}°{positive if n >= 0 else negative}'
            label = f'{region} · {degree(west,"E","W")}–{degree(west+step,"E","W")}, {degree(south,"N","S")}–{degree(south+step,"N","S")}'
            cells.append({'type':'Feature', 'id':cell_id(west, south),
                          'properties':{'id':cell_id(west, south), 'name':label, 'region':region,
                                        'bounds':[west,south,west+step,south+step], 'anchor':[anchor.x,anchor.y]},
                          'geometry':mapping(clipped)})
    return cells


def build_ledger(cells, attestations, polities):
    """Each fact seeds only polities containing its anchor at its latest date.

    Inference never propagates through inferred cells or later territorial growth.
    Each inferred cell needs a non-zero-area intersection with that dated polity.
    The grid is a coarse reporting index, not a homogeneous adoption polygon.
    """
    geometries = {c['id']: shape(c['geometry']) for c in cells}
    facts = []; inferred = []
    for a in sorted(attestations, key=lambda a:(a['date_to'],a['id'])):
        origin = cell_id(*a['coordinates'])
        assert origin in geometries, f"No land chunk for {a['id']}"
        facts.append({'cell':origin, 'attestation':a['id']})
        point = Point(a['coordinates'])
        year = a['date_to']
        candidates = [f for f in polities if f['properties']['from'] <= year < f['properties']['to']
                      and shape(f['geometry']).covers(point)]
        for f in sorted(candidates,key=lambda f:f['properties']['id']):
            p = f['properties']; geometry = shape(f['geometry'])
            affected = [cid for cid,g in geometries.items()
                        if g.intersects(geometry) and g.intersection(geometry).area > 0.000001]
            inferred.append({'attestation':a['id'], 'year':year, 'cells':affected,
                             'polity':{k:p[k] for k in ['id','entity','name','from','to','source_id'] if k in p},
                             'source':'cliopatria', 'wikipedia':p.get('wikipedia','')})
    return {'direct':facts,'inferred':inferred}


def main():
    technology = validate(load_curated())
    land_data = json.loads((DATA/'land.geojson').read_text(encoding='utf-8'))
    land = unary_union([shape(f['geometry']) for f in land_data['features']])
    cells = make_cells(land)
    # Read only era packages needed for the dated evidence and deduplicate copies.
    manifest = json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
    years = [a['date_to'] for a in technology['attestations']]
    polities = {}
    for chunk in manifest['chunks']:
        if not any(chunk['from'] <= y < chunk['to'] for y in years): continue
        for f in read_collection(DATA/chunk['url'])['features']:
            polities[f['properties']['id']] = f
    ledger = build_ledger(cells, technology['attestations'], list(polities.values()))
    result = {'schema_version':1, 'step_degrees':STEP, 'polity_revision':manifest['revision'],
              'method':'A chunk contains selected evidence, or overlaps an attested polity at the latest endpoint of an evidence date window. Inferred coverage persists; it does not prove adoption or continuous use. No recursive spread or later-conquest inference.',
              'cells':{'type':'FeatureCollection','features':cells}, **ledger}
    (DATA/'technology-regions.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Built {len(cells)} land chunks, {len(ledger["direct"])} direct records and {len(ledger["inferred"])} dated polity assumptions.')


if __name__ == '__main__': main()
