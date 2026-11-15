import copy
import gzip
import hashlib
import json
from pathlib import Path

import pytest
from pipeline.package import pack_collection, unpack_collection, pack_ring, unpack_ring, read_collection

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('ring',[
    [[179.9999,-80],[-179.9999,-80],[-179.9999,-79],[179.9999,-80]],
    [[0,0],[0.123456789012345,1.23456789123456],[1,-1],[0,0]],
])
def test_delta_coordinates_are_lossless_including_repaired_vertices(ring):
    assert unpack_ring(pack_ring(ring)) == ring

def test_deduplication_preserves_independent_properties_and_multipolygons():
    geometry={'type':'MultiPolygon','coordinates':[[[[0,0],[1,0],[1,1],[0,0]]]]}
    original={'type':'FeatureCollection','features':[
        {'type':'Feature','id':f'f{i}','properties':{'id':f'f{i}','from':i+1},'geometry':copy.deepcopy(geometry)} for i in range(2)]}
    packed=pack_collection(original)
    assert len(packed['geometries']) == 1
    assert unpack_collection(packed) == original

def test_shipped_chunks_have_valid_hashes_and_meet_byte_budgets():
    manifest=json.loads((ROOT/'atlas/data/manifest.json').read_text())
    assert manifest['schema_version']==2
    total=0
    for chunk in manifest['chunks']:
        path=ROOT/'atlas/data'/chunk['url']; raw=path.read_bytes(); total+=len(raw)
        assert hashlib.sha256(raw).hexdigest()==chunk['sha256']
        assert len(raw)==chunk['bytes'] and len(raw)<3_000_000
    assert total<15_000_000
    assert sum(p.stat().st_size for p in (ROOT/'atlas/data').rglob('*') if p.is_file())<15_000_000
    assert sum(p.stat().st_size for p in (ROOT/'atlas').rglob('*') if p.is_file())<15_000_000

def test_gzip_build_is_deterministic():
    manifest=json.loads((ROOT/'atlas/data/manifest.json').read_text())
    chunk=next(c for c in manifest['chunks'] if c['from']<=117<c['to'])
    path=ROOT/'atlas/data'/chunk['url']
    rebuilt=pack_collection(read_collection(path))
    encoded=json.dumps(rebuilt,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    assert gzip.compress(encoded,compresslevel=9,mtime=0)==path.read_bytes()
