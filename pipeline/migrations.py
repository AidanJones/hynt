"""Validate and package schematic migration models and separately dated site evidence."""
import json
import math
from pathlib import Path
from pipeline.chronology import bp_to_civil
ROOT=Path(__file__).resolve().parents[1]

def validate(data):
    ids=set()
    for r in data['records']:
        assert r['id'] not in ids; ids.add(r['id'])
        assert r['kind'] in ['route','site']
        assert all(type(r[k]) is int and r[k]!=0 for k in ['date_from','date_to'])
        assert -298051<=r['date_from']<=r['date_to']<=2026
        assert len(r['coordinates']) >= (2 if r['kind']=='route' else 1)
        for x,y in r['coordinates']:
            assert math.isfinite(x) and math.isfinite(y) and -180<=x<=180 and -85<=y<=85
        assert all(r[k] for k in ['name','date_label','summary','caveat'])
        assert r['sources'] and all(s in data['sources'] for s in r['sources'])
        if 'source_age' in r:
            age=r['source_age']; assert age['epoch']==1950 and age['oldest']>=age['youngest']
            assert r['date_from']==bp_to_civil(age['oldest']) and r['date_to']==bp_to_civil(age['youngest'])
    return data

def main():
    data=validate(json.loads((ROOT/'pipeline/curated/migrations.json').read_text(encoding='utf-8')))
    (ROOT/'atlas/data/migrations.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f"Packaged {len(data['records'])} migration/site stories")

if __name__=='__main__': main()
