import json
from pathlib import Path

import pytest

from pipeline.build import next_year, normalize, validate_feature
from pipeline.package import read_collection

ROOT = Path(__file__).resolve().parents[1]


def source_feature(start, end):
    return {'type': 'Feature', 'properties': {'Name': 'Test polity', 'FromYear': start,
        'ToYear': end, 'Area': 12, 'Wikidata': 'Q123'},
        'geometry': {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}}


@pytest.mark.parametrize(('year', 'expected'), [(-2, -1), (-1, 1), (1, 2), (2024, 2025)])
def test_civil_successor(year, expected):
    assert next_year(year) == expected


@pytest.mark.parametrize(('start', 'end'), [(-1, -1), (117, 117), (-31, 117)])
def test_inclusive_source_endpoints_survive(start, end):
    f = normalize(source_feature(start, end), 0)
    validate_feature(f, {'cliopatria': {}})
    p = f['properties']
    assert p['from'] <= end < p['to']
    assert not p['from'] <= next_year(end) < p['to']


@pytest.mark.parametrize(('start', 'end'), [(0, 1), (0, 0), (5, 4)])
def test_ambiguous_dates_are_rejected(start, end):
    with pytest.raises(ValueError):
        normalize(source_feature(start, end), 0)


def test_missing_citation_fails_validation():
    f = normalize(source_feature(1, 2), 0)
    f['properties']['sources'] = []
    with pytest.raises(AssertionError):
        validate_feature(f, {})

def test_zero_end_boundary_preserves_every_valid_civil_year_without_guessing():
    f=normalize(source_feature(-14,0),0)
    p=f['properties'];validate_feature(f,{'cliopatria':{}})
    assert p['source_to']==0 and p['display_to']==-1 and p['to']==1
    for year in range(-100,20):
        if year==0:continue
        assert (-14<=year<=0)==(p['from']<=year<p['to'])


def test_manifest_has_continuous_half_open_coverage():
    manifest = json.loads((ROOT / 'atlas/data/manifest.json').read_text())
    chunks = manifest['chunks']
    assert chunks[0]['from'] == -3400 and chunks[-1]['to'] == 2027
    assert all(a['to'] == b['from'] for a, b in zip(chunks, chunks[1:]))
    for year in [-3400, -1, 1, 117, 1280, 1920, 2024, 2026]:
        assert sum(c['from'] <= year < c['to'] for c in chunks) == 1


@pytest.mark.parametrize(('year', 'name'), [(117, 'Roman Empire'), (1280, 'Mongol'), (1920, 'British')])
def test_real_backbone_examples(year, name):
    manifest = json.loads((ROOT / 'atlas/data/manifest.json').read_text())
    chunk = next(c for c in manifest['chunks'] if c['from'] <= year < c['to'])
    data = read_collection(ROOT / 'atlas/data' / chunk['url'])
    found = [f for f in data['features'] if name.lower() in f['properties']['name'].lower()
             and f['properties']['from'] <= year < f['properties']['to']]
    assert found
    for feature in found:
        validate_feature(feature, {'cliopatria': {}})


def test_no_extrapolation_past_coverage():
    manifest = json.loads((ROOT / 'atlas/data/manifest.json').read_text())
    chunk = manifest['chunks'][-1]
    data = read_collection(ROOT / 'atlas/data' / chunk['url'])
    assert not any(f['properties']['from'] <= 2026 < f['properties']['to'] for f in data['features'])
