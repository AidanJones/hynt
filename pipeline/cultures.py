"""Package selected GPL-licensed culture reconstructions with corresponding source."""
import hashlib,json
from pathlib import Path
from shapely import make_valid
from shapely.geometry import shape,mapping
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'atlas/data'

def build(curated,bundle):
    assert curated['revision']==bundle['revision'] and curated['licence']=='GPL-3.0-only'
    source={(r['snapshot'],r['source_index']):r for r in bundle['records']}
    features=[];ids=set()
    for r in curated['selection']:
        assert r['id'] not in ids;ids.add(r['id'])
        assert curated['coverage_from']<=r['snapshot']<r['to']<=curated['coverage_to']
        assert r['snapshot']!=0 and r['to']!=0
        original=source[(r['snapshot'],r['source_index'])]['feature']
        assert original['properties']['NAME']==r['source_name']
        assert r['references'] and all(s in curated['references'] for s in r['references'])
        geometry=make_valid(shape(original['geometry'])).simplify(0.01,preserve_topology=True)
        assert geometry.is_valid and not geometry.is_empty and geometry.geom_type in ('Polygon','MultiPolygon')
        properties={'id':r['id'],'entity':r['entity'],'name':r['name'],'layer':'culture','kind':'archaeological-culture',
            'from':r['snapshot'],'to':r['to'],'snapshot_year':r['snapshot'],'confidence':'unknown',
            'colour':r['colour'],'summary':r['summary'],'references':r['references'],
            'source_index':r['source_index'],'source_properties':original['properties'],
            'geometry_status':'partial interpretive reconstruction','licence':'GPL-3.0-only'}
        features.append({'type':'Feature','id':r['id'],'properties':properties,'geometry':mapping(geometry)})
    return {'type':'FeatureCollection','features':features,'references':curated['references'],'revision':curated['revision'],
        'coverage_from':curated['coverage_from'],'coverage_to':curated['coverage_to'],'licence':'GPL-3.0-only',
        'method':'Snapshot outlines carried until the next selected source snapshot or import coverage boundary; not culture start/end dates. Partial reconstructions, not ethnic, genetic or political borders.'}

def main():
    curated=json.loads((ROOT/'pipeline/curated/cultures.json').read_text(encoding='utf-8'))
    bundle=json.loads((ROOT/'pipeline/curated/culture-sources.json').read_text(encoding='utf-8'))
    result=build(curated,bundle)
    licence=(OUT/'cultures/LICENSE.txt').read_bytes()
    assert hashlib.sha256(licence).hexdigest()==bundle['licence_sha256']
    (OUT/'cultures.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (OUT/'cultures/source.json').write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Packaged {len(result["features"])} selected culture snapshots, corresponding source and GPL licence.')
if __name__=='__main__':main()
