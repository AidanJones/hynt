"""Validate and package original curated technology evidence, without fetching sources."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    packages = {p['id']: p for p in data['packages']}
    assert len(packages) == len(data['packages']), 'Duplicate package IDs'
    records = {a['id']: a for a in data['attestations']}
    assert len(records) == len(data['attestations']), 'Duplicate evidence IDs'
    for p in packages.values():
        assert p['name'] and p['components'] and p['description']
    for a in records.values():
        assert a['package'] in packages
        assert all(type(a[k]) is int and a[k] != 0 for k in ['date_from', 'date_to'])
        assert -10000 <= a['date_from'] <= a['date_to'] <= 2026
        assert len(a['coordinates']) == 2 and all(math.isfinite(v) for v in a['coordinates'])
        assert -180 <= a['coordinates'][0] <= 180 and -90 <= a['coordinates'][1] <= 90
        assert a['location_note'] and a['summary'] and a['evidence'] and a['date_label']
        assert a['sources'] and all(s in data['sources'] for s in a['sources'])
    seen = set()
    for edge in data['transmissions']:
        assert edge['id'] not in seen
        seen.add(edge['id'])
        origin, target = records[edge['origin']], records[edge['destination']]
        assert origin['package'] == target['package'] == edge['package']
        assert origin['date_to'] <= target['date_from'], 'Transmission predates its origin'
        assert edge['sources'] and all(s in data['sources'] for s in edge['sources'])
        assert edge['summary'] and edge['kind']
    for source in data['sources'].values():
        assert source['url'].startswith('https://') and source['author'] and source['locator']
    return data


def main():
    data = validate(json.loads((ROOT / 'pipeline/curated/technologies.json').read_text(encoding='utf-8')))
    (ROOT / 'atlas/data/technologies.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f"Packaged {len(data['packages'])} technology packages, {len(data['attestations'])} attestations, {len(data['transmissions'])} evidenced links")


if __name__ == '__main__':
    main()
