"""Rebuild distributed data: python -m pipeline.build (Python 3.12+)."""
import argparse
import hashlib
import json
import math
import re
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

from shapely import make_valid
from shapely.geometry import mapping, shape
from pipeline.identity import apply_identity,entity_index

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'pipeline' / 'raw'
OUT = ROOT / 'atlas' / 'data'
REVISION = '5f433377139a6eeaeacbdc894b70f8805b72c8b5'
BASE = f'https://raw.githubusercontent.com/Seshat-Global-History-Databank/cliopatria/{REVISION}/'
ARCHIVE_SHA = 'e10a4e429fca708788ff9e7572a95fce801fae55852d217cffabc1c59cd4eed4'
TOLERANCE = 0.035  # degrees; world overview, not survey geometry


def next_year(year):
    return 1 if year == -1 else year + 1


def fetch(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        temporary = path.with_suffix(path.suffix + '.download')
        with urllib.request.urlopen(url, timeout=180) as response:
            temporary.write_bytes(response.read())
        temporary.replace(path)
    return path


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')


def rounded(value):
    if isinstance(value, (list, tuple)):
        return [rounded(v) for v in value]
    return round(value, 4) if isinstance(value, float) else value


def polygonal(geometry):
    if geometry.geom_type in ('Polygon', 'MultiPolygon'):
        return geometry
    from shapely.ops import unary_union
    pieces = [g for g in getattr(geometry, 'geoms', []) if g.geom_type in ('Polygon', 'MultiPolygon')]
    return unary_union(pieces)


def normalize(feature, index):
    p = feature['properties']
    start, end = int(p['FromYear']), int(p['ToYear'])
    if start == 0 or start > end:
        raise ValueError(f'Invalid source years in record {index}')
    qid = str(p.get('Wikidata', '')).strip()
    qid = qid if re.fullmatch(r'Q\d+', qid) else ''
    entity = qid or 'cliopatria:' + hashlib.sha256(p['Name'].encode()).hexdigest()[:16]
    geom = polygonal(make_valid(shape(feature['geometry'])))
    if geom.is_empty:
        raise ValueError(f'Empty polygon in record {index}')
    geom = polygonal(make_valid(geom.simplify(TOLERANCE, preserve_topology=True)))
    geometry = mapping(geom)
    geometry['coordinates'] = rounded(geometry['coordinates'])
    # Coordinate rounding can introduce invalid rings: repair after quantization too.
    final = polygonal(make_valid(shape(geometry)))
    if final.is_empty or not final.is_valid:
        raise ValueError(f'Invalid packaged geometry {index}')
    props = dict(id=f'polity:cliopatria:{index:05d}', entity=entity, name=p['Name'],
                 layer='polity', kind='polity', confidence='unknown',
                 **{'from': start, 'to': next_year(-1 if end == 0 else end)}, sources=['cliopatria'],
                 wikidata=qid, wikipedia=p.get('Wikipedia', ''),
                 area_km2=round(float(p['Area']), 2), source_record=index,
                 source_from=start, source_to=end)
    if end == 0:
        props['display_to'] = -1
        props['date_note'] = 'The upstream inclusive endpoint is 0. Over the viewer’s valid civil years (no year zero), this covers years through 1 BCE and excludes 1 CE. The original endpoint is retained; no historical date is inferred.'
    return {'type': 'Feature', 'id': props['id'], 'properties': apply_identity(props), 'geometry': mapping(final)}


def validate_feature(feature, sources):
    p = feature['properties']
    assert p['from'] != 0 and p['to'] != 0 and p['from'] < p['to']
    assert p['entity'] and p['sources'] and all(s in sources for s in p['sources'])
    assert p['confidence'] in ('unknown', 'high', 'medium', 'low', 'speculative')
    g = shape(feature['geometry'])
    assert not g.is_empty and g.is_valid and g.geom_type in ('Polygon', 'MultiPolygon')
    assert all(math.isfinite(v) for v in g.bounds)
    assert -180.001 <= g.bounds[0] <= g.bounds[2] <= 180.001
    assert -90.001 <= g.bounds[1] <= g.bounds[3] <= 90.001


def main():
    from pipeline.technologies import main as build_technologies
    from pipeline.britain import main as build_britain
    from pipeline.migrations import main as build_migrations
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Require cached input, do not fetch')
    args = parser.parse_args()
    build_technologies()
    build_britain()
    build_migrations()
    archive = RAW / 'cliopatria.geojson.zip'
    if not args.offline:
        fetch(BASE + archive.name, archive)
        fetch(BASE + 'LICENSE.md', RAW / 'LICENSE.md')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA:
        raise ValueError('Cached Cliopatria archive does not match the pinned SHA-256')
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.endswith('.geojson')]
        assert len(names) == 1, 'Expected one GeoJSON archive member'
        original = json.loads(z.read(names[0]))
    sources = {'cliopatria': {
        'title': 'Cliopatria · Seshat Global History Databank',
        'author': 'Cliopatria contributors / Seshat Global History Databank',
        'url': f'https://github.com/Seshat-Global-History-Databank/cliopatria/tree/{REVISION}',
        'licence': 'CC BY 4.0', 'licence_url': 'https://creativecommons.org/licenses/by/4.0/',
        'revision': REVISION, 'download_url': BASE + archive.name,
        'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'type': 'dataset', 'citation': 'Cliopatria, Seshat Global History Databank, pinned Git revision ' + REVISION,
        'changes': 'Inclusive dates converted to half-open civil-year intervals; geometries repaired, simplified at 0.035 degrees and rounded to 4 decimals. Original area retained. Confidence not supplied.'}}
    features, excluded, quarantined, date_decisions = [], Counter(), [], []
    for index, feature in enumerate(original['features']):
        if feature['properties']['Type'] != 'POLITY':
            excluded[feature['properties']['Type']] += 1
            continue
        p = feature['properties']
        if p['FromYear'] == 0 or p['FromYear'] > p['ToYear']:
            quarantined.append({'source_record': index, 'reason': 'Invalid or ambiguous civil-year range', 'properties': p})
            continue
        features.append(normalize(feature, index))
        if p['ToYear'] == 0:
            date_decisions.append({'source_record':index,'original_properties':p,
                'normalised_exclusive_end':1,'display_end':-1,
                'reason':'For every valid civil year y != 0, from <= y <= 0 is equivalent to from <= y < 1. This preserves source query membership without inferring a date or changing the raw endpoint.'})
        if index % 1000 == 0:
            print(f'Normalized {index} source records', flush=True)
    for feature in features:
        validate_feature(feature, sources)
    entities = {}
    for f in features:
        p = f['properties']
        entry = entities.setdefault(p['entity'], dict(id=p['entity'], name=p['name'], **{'from': p['from'], 'to': p['to']}))
        entry['from'] = min(entry['from'], p['from'])
        entry['to'] = max(entry['to'], p['to'])
    boundaries = [-3400, -3000, -2500, -2000, -1500, -1000, -500, 1, 500, 1000, 1500, 1600, 1700, 1800, 1900, 1950, 2000, 2027]
    chunks = []
    for start, end in zip(boundaries, boundaries[1:]):
        selected = [f for f in features if f['properties']['from'] < end and f['properties']['to'] > start]
        relative = f'polities/era_{start}_{end}.geojson'
        write(OUT / relative, {'type': 'FeatureCollection', 'features': selected})
        chunks.append({'from': start, 'to': end, 'url': relative, 'features': len(selected), 'bytes': (OUT / relative).stat().st_size})
    write(OUT / 'sources.json', sources)
    write(ROOT / 'pipeline' / 'quarantine.json', quarantined)
    write(ROOT / 'pipeline' / 'date-decisions.json', date_decisions)
    write(OUT / 'entities.json', entity_index(features))
    write(OUT / 'manifest.json', {'schema_version': 1, 'minimum_year': -3400, 'maximum_year': 2026,
                                'coverage_to': max(f['properties']['source_to'] for f in features),
                                'revision': REVISION, 'chunks': chunks})
    from pipeline.package import main as package_data
    package_data()
    chunks = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))['chunks']
    era_rows = '\n'.join(f"| {c['from']} to <{c['to']} | {c['features']} | {c['bytes'] / 1_000_000:.2f} MB |" for c in chunks)
    checks = []
    for year, fragment in [(117, 'Roman Empire'), (1280, 'Mongol'), (1920, 'British')]:
        matched = [f for f in features if f['properties']['from'] <= year < f['properties']['to'] and fragment.lower() in f['properties']['name'].lower()]
        checks.append(f'- {year}: {len(matched)} active records matching {fragment}. Source-presence check; expert visual review is still needed.')
    report = f'''# Build report — milestone 1

Generated by `python -m pipeline.build`. Source revision `{REVISION}`.

Separate curated evidence is documented in [technology-report.md](technology-report.md) and [PRE_ROMAN_BRITAIN.md](PRE_ROMAN_BRITAIN.md); the counts below describe polity data.

- {len(original['features'])} input records; {len(features)} polity shapes; {len(entities)} entity keys.
- Excluded non-polity record types: {dict(excluded)}.
- Quarantined {len(quarantined)} records with ambiguous year-zero or reversed ranges; original fields retained in pipeline/quarantine.json. Dates were not guessed.
- Restored {len(date_decisions)} zero-endpoint records by preserving membership over valid civil years; raw fields and the equivalence rule are in pipeline/date-decisions.json. No year zero is exposed.
- All distributed shapes passed date, provenance, finite-coordinate and valid polygon checks.
- {sum(c['bytes'] for c in chunks)/1_000_000:.2f} MB shipped across gzip era files; exact geometries deduplicated within chunks. Boundary-spanning shapes are duplicated between chunks.
- Simplification: 0.035 angular degrees, per-feature topology preserved; this is not a globally constant distance or shared-border topology guarantee. Coordinates rounded to four decimals and repaired. Source area is retained, not recomputed from simplified shapes.
- Coverage ends in {max(f['properties']['source_to'] for f in features)}; no extrapolation to 2026.

## Era files

| Civil interval | Features | Shipped size |
| --- | ---: | ---: |
{era_rows}

## Acceptance source checks

{chr(10).join(checks)}

## Gaps and limits

- No prehistoric polity, migration, event, religion or campaign data in this backbone. Separate curated evidence layers have their own reports.
- Confidence is unknown: the source has no per-record uncertainty rating. Bounds are claims/control approximations, not evidence of homogeneous identity.
- No data means no coverage, not uninhabited land. Current source thresholds and regional completeness need separate audit.
- Entity reconciliation uses QID then exact source-name hash; QID aliases and inconsistent identities need review.
- Contested overlaps and same-entity interval overlaps are preserved; click lists candidates. The sampled spatial/region-by-era audit and searchable review queue are available; exhaustive historical border adjudication remains outstanding. See audit-report.md and source-review-report.md.
- Performance budgets and expert historical acceptance are not certified by data validation. See verification.md for measured checks.
'''
    (ROOT / 'build-report.md').write_text(report, encoding='utf-8')
    from pipeline.audit import main as audit_data
    audit_data()
    from pipeline.technology_regions import main as regional_technologies
    regional_technologies()
    from pipeline.events import main as build_events
    build_events()
    from pipeline.religion import main as build_religion
    build_religion()
    from pipeline.ranking import main as build_ranking
    build_ranking()
    print(f'Built {len(features)} features in {len(chunks)} era chunks.', flush=True)


if __name__ == '__main__':
    main()
