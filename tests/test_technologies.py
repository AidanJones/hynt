import copy
import json
from pathlib import Path

import pytest

from pipeline.technologies import validate, load_curated
from pipeline.chronology import bp_to_civil

ROOT = Path(__file__).resolve().parents[1]
DATA = load_curated()


def test_curated_data_is_valid_and_packaged_without_changes():
    assert validate(DATA)
    assert json.loads((ROOT / 'atlas/data/technologies.json').read_text(encoding='utf-8')) == DATA

def test_bp_epoch_and_civil_year_boundary():
    assert bp_to_civil(0) == 1950
    assert bp_to_civil(1950) == -1
    assert bp_to_civil(6950) == -5001
    altered=copy.deepcopy(DATA)
    next(a for a in altered['attestations'] if a['id']=='farming-kuk')['date_from']=-5000
    with pytest.raises(AssertionError): validate(altered)


@pytest.mark.parametrize('change', ['no-source','zero-year','reversed','bad-coordinate','duplicate','future-origin'])
def test_evidence_contract_rejects_bad_records(change):
    data = copy.deepcopy(DATA)
    a = data['attestations'][0]
    if change == 'no-source': a['sources'] = []
    if change == 'zero-year': a['date_from'] = 0
    if change == 'reversed': a['date_to'] = -9500
    if change == 'bad-coordinate': a['coordinates'] = [200, 40]
    if change == 'duplicate': data['attestations'].append(copy.deepcopy(a))
    if change == 'future-origin': data['transmissions'][0]['origin'] = 'algebra-segovia'; data['transmissions'][0]['destination'] = 'algebra-baghdad'
    with pytest.raises(AssertionError):
        validate(data)
