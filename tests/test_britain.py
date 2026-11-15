import copy
import json
from pathlib import Path
import pytest
from pipeline.britain import validate

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'pipeline/curated/britain.json').read_text(encoding='utf-8'))

def test_original_records_are_valid_and_packaged():
    assert validate(DATA)
    assert json.loads((ROOT/'atlas/data/britain.json').read_text(encoding='utf-8')) == DATA

@pytest.mark.parametrize('fault',['source','chronology','zero','coordinate','related','duplicate'])
def test_invalid_records_fail(fault):
    data = copy.deepcopy(DATA); record = data['records'][0]
    if fault=='source': record['sources']=[]
    if fault=='chronology': record['date_to']=-5000
    if fault=='zero': record['date_from']=0
    if fault=='coordinate': record['coordinates']=[100,10]
    if fault=='related': record['related']=['invented-ruler']
    if fault=='duplicate': data['records'].append(copy.deepcopy(record))
    with pytest.raises(AssertionError): validate(data)
