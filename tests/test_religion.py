import copy,json
from pathlib import Path
import pytest
from pipeline.religion import validate
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'pipeline/curated/religion.json').read_text(encoding='utf-8'))
def test_religion_types_and_package():
    assert validate(DATA)
    assert json.loads((ROOT/'atlas/data/religion.json').read_text(encoding='utf-8'))==DATA
def test_plurality_is_not_a_majority():
    data=copy.deepcopy(DATA);data['records'][-1]['share_percent']=49
    with pytest.raises(AssertionError):validate(data)
