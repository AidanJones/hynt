import copy
import json
from pathlib import Path
import pytest
from pipeline.events import validate
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'pipeline/curated/events.json').read_text(encoding='utf-8'))

def test_events_are_valid_and_packaged():
    assert validate(DATA)
    assert json.loads((ROOT/'atlas/data/events.json').read_text(encoding='utf-8'))==DATA

@pytest.mark.parametrize('error',['source','duplicate','waypoint','coordinate'])
def test_event_contract(error):
    data=copy.deepcopy(DATA)
    if error=='source':data['events'][0]['sources']=[]
    if error=='duplicate':data['events'].append(data['events'][0])
    if error=='waypoint':data['campaigns'][0]['waypoints'].reverse()
    if error=='coordinate':data['events'][0]['coordinates']=[190,95]
    with pytest.raises(AssertionError):validate(data)
