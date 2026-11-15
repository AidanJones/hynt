import json
from pathlib import Path
from shapely.geometry import box, mapping, shape
from pipeline.technology_regions import make_cells, build_ledger, cell_id
from pipeline.technologies import load_curated

ROOT=Path(__file__).resolve().parents[1]


def test_grid_is_stable_land_clipped_and_has_no_area_overlap():
    land=box(1,1,9,9)
    cells=make_cells(land)
    assert len(cells)==4
    assert cell_id(180,90)=='71:29'
    assert cell_id(-180,-60)=='0:0'
    assert sum(shape(c['geometry']).area for c in cells)==land.area
    assert all(shape(c['geometry']).within(land) for c in cells)
    for a,b in zip(cells,cells[1:]):
        assert shape(a['geometry']).intersection(shape(b['geometry'])).area==0


def test_inference_uses_latest_date_dated_borders_and_never_recurses():
    cells=make_cells(box(1,1,19,4))
    fact={'id':'fact','coordinates':[2,2],'date_from':-10,'date_to':10}
    def polity(id,west,east,start,end):
        return {'properties':{'id':id,'entity':id,'name':id,'from':start,'to':end},'geometry':mapping(box(west,1,east,4))}
    ledger=build_ledger(cells,[fact],[polity('current',1,9,-1,11),polity('future',1,19,11,100),polity('neighbour',6,19,1,100)])
    assert len(ledger['inferred'])==1
    model=ledger['inferred'][0]
    assert model['year']==10 and model['polity']['id']=='current'
    assert cell_id(7,2) in model['cells']
    assert cell_id(17,2) not in model['cells']


def test_actual_ledger_references_real_facts_cells_and_preserves_sources():
    data=json.loads((ROOT/'atlas/data/technology-regions.json').read_text(encoding='utf-8'))
    tech=load_curated();records={a['id']:a for a in tech['attestations']}
    cells={c['id'] for c in data['cells']['features']}
    assert len(data['direct'])==len(records)
    for fact in data['direct']:
        assert fact['cell'] in cells and fact['attestation'] in records
    for model in data['inferred']:
        assert model['year']==records[model['attestation']]['date_to']
        assert set(model['cells'])<=cells
        assert model['polity']['from']<=model['year']<model['polity']['to']
        assert model['source']=='cliopatria'
