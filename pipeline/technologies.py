"""Validate and package original curated technology evidence, without fetching sources."""
import json
import math
from pathlib import Path
from pipeline.chronology import bp_to_civil

ROOT = Path(__file__).resolve().parents[1]

def load_curated():
    data = json.loads((ROOT / 'pipeline/curated/technologies.json').read_text(encoding='utf-8'))
    for filename in ['technology-expansion.json', 'technology-regional.json']:
        extension = json.loads((ROOT / 'pipeline/curated' / filename).read_text(encoding='utf-8'))
        for key in ['packages','attestations','transmissions']:
            data[key].extend(extension[key])
        assert not data['sources'].keys() & extension['sources'].keys(), 'Duplicate source IDs'
        data['sources'].update(extension['sources'])
    return data


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
        if 'source_date' in a:
            date = a['source_date']
            assert date['system'] == 'cal BP'
            assert a['date_from'] == bp_to_civil(date['oldest'])
            assert a['date_to'] == bp_to_civil(date['youngest'])
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
    data = validate(load_curated())
    (ROOT / 'atlas/data/technologies.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f"Packaged {len(data['packages'])} technology packages, {len(data['attestations'])} attestations, {len(data['transmissions'])} evidenced links")


if __name__ == '__main__':
    main()
