"""Losslessly pack validated GeoJSON into deduplicated, delta-coded gzip chunks."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'atlas/data'
FORMAT = 'hynt-polities-1'
SCALE = 10000


def pack_ring(points):
    deltas, exact, previous = [], [], [0, 0]
    for index, point in enumerate(points):
        encoded = [round(v * SCALE) for v in point]
        deltas.extend([encoded[0] - previous[0], encoded[1] - previous[1]])
        previous = encoded
        if any(v / SCALE != original for v, original in zip(encoded, point)):
            exact.append([index, *point])
    return {'d': deltas, 'e': exact} if exact else deltas


def unpack_ring(value):
    deltas = value['d'] if isinstance(value, dict) else value
    x = y = 0
    points = []
    for index in range(0, len(deltas), 2):
        x += deltas[index]
        y += deltas[index + 1]
        points.append([x / SCALE, y / SCALE])
    if isinstance(value, dict):
        for index, x, y in value['e']:
            points[index] = [x, y]
    return points


def pack_collection(collection):
    geometries, lookup, rows = [], {}, []
    for feature in collection['features']:
        geometry = feature['geometry']
        key = json.dumps(geometry, separators=(',', ':'), sort_keys=True)
        if key not in lookup:
            lookup[key] = len(geometries)
            polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
            geometries.append({'type': geometry['type'], 'coordinates': [[pack_ring(r) for r in polygon] for polygon in polygons]})
        rows.append([feature['properties'], lookup[key]])
    return {'format': FORMAT, 'scale': SCALE, 'geometries': geometries, 'rows': rows}


def unpack_collection(packed):
    assert packed['format'] == FORMAT and packed['scale'] == SCALE
    geometries = []
    for item in packed['geometries']:
        polygons = [[unpack_ring(r) for r in polygon] for polygon in item['coordinates']]
        geometries.append({'type': item['type'], 'coordinates': polygons if item['type'] == 'MultiPolygon' else polygons[0]})
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'id': properties['id'], 'properties': properties, 'geometry': geometries[index]}
        for properties, index in packed['rows']]}


def read_collection(path):
    if path.suffix == '.gz':
        return unpack_collection(json.loads(gzip.decompress(path.read_bytes())))
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    manifest_path = DATA / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest['schema_version'] == 2:
        print('Packed manifest already current; run the full build to regenerate inputs.')
        return
    old_paths, chunks = [], []
    expanded_total = 0
    for chunk in manifest['chunks']:
        original_path = DATA / chunk['url']
        original = read_collection(original_path)
        packed = pack_collection(original)
        assert unpack_collection(packed) == original, f"Lossless round-trip failed: {chunk['url']}"
        encoded = json.dumps(packed, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
        compressed = gzip.compress(encoded, compresslevel=9, mtime=0)
        relative = chunk['url'].replace('.geojson', '.json.gz')
        (DATA / relative).write_bytes(compressed)
        expanded = original_path.stat().st_size
        expanded_total += expanded
        chunks.append({**chunk, 'url': relative, 'bytes': len(compressed), 'expanded_bytes': expanded,
                       'geometries': len(packed['geometries']), 'sha256': hashlib.sha256(compressed).hexdigest()})
        old_paths.append(original_path)
        print(f"Packed {relative}: {len(compressed):,} bytes", flush=True)
    manifest.update(schema_version=2, encoding=FORMAT, chunks=chunks)
    temporary = manifest_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(manifest, separators=(',', ':')), encoding='utf-8')
    temporary.replace(manifest_path)
    # Remove only exact generated inputs from the old manifest, after validation.
    for path in old_paths:
        if path.resolve().parent != (DATA / 'polities').resolve() or path.suffix != '.geojson':
            raise ValueError(f'Refusing to remove an unexpected generated path: {path}')
        path.unlink()
    summary = {'encoding': FORMAT, 'original_bytes': expanded_total,
               'shipped_bytes': sum(c['bytes'] for c in chunks),
               'largest_chunk_bytes': max(c['bytes'] for c in chunks),
               'round_trip': 'Every property and coordinate equals the validated input; no further simplification.'}
    (DATA / 'packaging-report.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
