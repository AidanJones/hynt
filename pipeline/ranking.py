"""Rank equal-area union footprints at geometry change points, never by name count."""
import json
from collections import defaultdict
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import shape
from shapely import transform, make_valid
from shapely.ops import unary_union
from pipeline.package import read_collection
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'atlas/data'

def derive(features,top=10):
    entities=sorted({f['properties']['entity'] for f in features})
    index={entity:i for i,entity in enumerate(entities)}
    names={}
    for f in features:names.setdefault(f['properties']['entity'],f['properties']['name'])
    projector=Transformer.from_crs(4326,6933,always_xy=True).transform
    geometries={f['properties']['id']:make_valid(transform(shape(f['geometry']),projector,interleaved=False)) for f in features}
    additions=defaultdict(list);removals=defaultdict(list)
    for f in features:
        p=f['properties'];additions[p['from']].append(p);removals[p['to']].append(p)
    years=sorted(set(additions)|set(removals));active=defaultdict(dict);areas={};history=defaultdict(list);snapshots=[]
    for year,end in zip(years,years[1:]):
        changed=set()
        for p in removals[year]:active[p['entity']].pop(p['id'],None);changed.add(p['entity'])
        for p in additions[year]:active[p['entity']][p['id']]=geometries[p['id']];changed.add(p['entity'])
        for entity in changed:
            if not active[entity]:areas.pop(entity,None);continue
            area=round(unary_union(list(active[entity].values())).area/1_000_000)
            if area>0:areas[entity]=area
            else:areas.pop(entity,None)
        ranking=[[index[e],a] for e,a in sorted(areas.items(),key=lambda item:(-item[1],item[0]))[:top]]
        if snapshots and snapshots[-1][1]==year and snapshots[-1][2]==ranking:snapshots[-1][1]=end
        else:snapshots.append([year,end,ranking])
        for entity,area in areas.items():
            rows=history[index[entity]]
            if rows and rows[-1][1]==year and rows[-1][2]==area:rows[-1][1]=end
            else:rows.append([year,end,area])
    return {'metric':'territorial extent','units':'km²','projection':'EPSG:6933',
            'method':'Union of concurrent polygons per entity before equal-area measurement. Distinct overlapping entities rank separately; values must not be summed. Simplified claimed/controlled geometry, not power, population or exact land area.',
            'entities':[{'id':e,'name':names[e]} for e in entities], 'snapshots':snapshots,
            'history':{str(i):rows for i,rows in sorted(history.items())}}

def main():
    manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'));features={}
    for chunk in manifest['chunks']:
        for f in read_collection(DATA/chunk['url'])['features']:features[f['properties']['id']]=f
    result=derive(list(features.values()));result['revision']=manifest['revision']
    (DATA/'influence.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Built {len(result["snapshots"])} territorial ranking intervals; {len(result["entities"])} entities.')
if __name__=='__main__':main()
