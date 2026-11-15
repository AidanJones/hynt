"""Keep state affiliation and population-majority observations separate."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(data):
    ids=set()
    for r in data['records']:
        assert r['id'] not in ids;ids.add(r['id'])
        assert r['kind'] in ['official','majority'] and r['entity'].startswith('Q')
        assert all(type(r[k]) is int and r[k]!=0 for k in ['from','to']) and r['from']<r['to']
        assert r['summary'] and r['religion'] and r['sources'] and all(s in data['sources'] for s in r['sources'])
        if r['kind']=='majority':assert 50<r['share_percent']<=100
    for s in data['sources'].values():assert s['url'].startswith('https://') and s['author'] and s['locator']
    return data
def main():
    data=validate(json.loads((ROOT/'pipeline/curated/religion.json').read_text(encoding='utf-8')))
    entities={e['id'] for e in json.loads((ROOT/'atlas/data/entities.json').read_text(encoding='utf-8'))}
    assert all(r['entity'] in entities for r in data['records'])
    (ROOT/'atlas/data/religion.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Packaged {len(data["records"])} separately typed religion observations.')
if __name__=='__main__':main()
