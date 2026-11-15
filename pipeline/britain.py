"""Validate and package the small Britain/Wales evidence compilation."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    records = {r['id']: r for r in data['records']}
    assert len(records) == len(data['records']), 'Duplicate evidence IDs'
    for record in records.values():
        assert record['kind'] in ('ruler', 'site', 'community', 'artefact')
        assert all(type(record[k]) is int and record[k] != 0 for k in ['date_from', 'date_to'])
        assert -10000 <= record['date_from'] <= record['date_to'] <= 2026
        x, y = record['coordinates']
        assert all(math.isfinite(v) for v in [x, y]) and -9 <= x <= 3 and 49 <= y <= 61
        assert all(record[k] for k in ['date_basis', 'date_label', 'evidence', 'summary', 'location_note', 'name', 'place'])
        assert record['sources'] and all(s in data['sources'] for s in record['sources'])
        assert all(other in records and other != record['id'] for other in record['related'])
    for source in data['sources'].values():
        assert source['url'].startswith('https://') and source['locator'] and source['author']
    return data


def main():
    data = validate(json.loads((ROOT / 'pipeline/curated/britain.json').read_text(encoding='utf-8')))
    (ROOT / 'atlas/data/britain.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f"Packaged {len(data['records'])} Britain/Wales evidence records")


if __name__ == '__main__':
    main()
