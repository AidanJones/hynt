import copy
import json
from pathlib import Path
import pytest
from pipeline.migrations import validate

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'pipeline/curated/migrations.json').read_text(encoding='utf-8'))
def test_migration_evidence_is_valid_and_packaged():
    assert validate(DATA)
    assert json.loads((ROOT/'atlas/data/migrations.json').read_text(encoding='utf-8'))==DATA

@pytest.mark.parametrize('fault',['source','age','geometry','range','duplicate'])
def test_inconsistent_migration_evidence_fails(fault):
    data=copy.deepcopy(DATA);record=data['records'][0]
    if fault=='source':record['sources']=[]
    if fault=='age':record['source_age']['oldest']=70000
    if fault=='geometry':record['coordinates']=[[200,5]]
    if fault=='range':record['date_to']=record['date_from']-1
    if fault=='duplicate':data['records'].append(copy.deepcopy(record))
    with pytest.raises(AssertionError):validate(data)
