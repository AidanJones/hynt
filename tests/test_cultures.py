import copy,json
from pathlib import Path
import pytest
from pipeline.cultures import build
ROOT=Path(__file__).resolve().parents[1]
CURATED=json.loads((ROOT/'pipeline/curated/cultures.json').read_text(encoding='utf-8'))
BUNDLE=json.loads((ROOT/'pipeline/curated/culture-sources.json').read_text(encoding='utf-8'))
def test_culture_package_is_reproducible_and_keeps_source_separate():
    original=copy.deepcopy(BUNDLE)
    result=build(CURATED,BUNDLE)
    assert BUNDLE==original
    assert json.loads(json.dumps(result))==json.loads((ROOT/'atlas/data/cultures.json').read_text(encoding='utf-8'))
    assert len(result['features'])==6 and result['licence']=='GPL-3.0-only'
    assert all(f['properties']['confidence']=='unknown' and f['properties']['snapshot_year']==f['properties']['from'] for f in result['features'])
@pytest.mark.parametrize('failure',['wrong-source','bad-date','missing-reference'])
def test_culture_import_fails_on_unreviewed_inputs(failure):
    data=copy.deepcopy(CURATED)
    if failure=='wrong-source':data['selection'][0]['source_name']='Bantu'
    if failure=='bad-date':data['selection'][0]['to']=-12000
    if failure=='missing-reference':data['selection'][0]['references']=[]
    with pytest.raises(AssertionError):build(data,BUNDLE)
