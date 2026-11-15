"""Validate sourced events, typed relations and independently dated waypoints."""
import json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def validate(data):
    ids=set()
    def common(r):
        assert r['id'] not in ids;ids.add(r['id'])
        assert type(r['year']) is int and r['year']!=0 and -3400<=r['year']<=2026
        assert r['summary'] and r['sources'] and all(s in data['sources'] for s in r['sources'])
    def coordinates(p):
        assert len(p)==2 and all(isinstance(v,(int,float)) for v in p)
        assert -180<=p[0]<=180 and -90<=p[1]<=90
    for e in data['events']:
        common(e);coordinates(e['coordinates'])
        assert e['category'] in ['battle','landing','political','founding','religious','technology','catastrophe']
        assert 1<=e['importance']<=3
        if 'date' in e:assert date.fromisoformat(e['date']).year==e['year']
    for c in data['campaigns']:
        common(c);assert c['attacker'] and c['defender'] and c['outcome']
        assert len(c['waypoints'])>=2
        dates=[]
        for w in c['waypoints']:
            coordinates(w['coordinates']);d=date.fromisoformat(w['date']);assert d.year==c['year'];dates.append(d)
        assert all(a<b for a,b in zip(dates,dates[1:]))
    for r in data['relations']:
        common(r);assert r['origin'] and r['destination'] and r['kind']
        assert len(r['coordinates'])==2
        for p in r['coordinates']:coordinates(p)
    for s in data['sources'].values():assert s['url'].startswith('https://') and s['author'] and s['locator']
    return data


def main():
    data=validate(json.loads((ROOT/'pipeline/curated/events.json').read_text(encoding='utf-8')))
    (ROOT/'atlas/data/events.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Packaged {len(data["events"])} events, {len(data["campaigns"])} campaigns and {len(data["relations"])} explicit relations.')


if __name__=='__main__':main()
