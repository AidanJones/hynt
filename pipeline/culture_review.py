"""Inspect pinned candidate snapshots without redistributing cultural polygons."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REVISION='4b5039e50d8d2464b065bd76ad6086cd4597108d'
BASE=f'https://raw.githubusercontent.com/aourednik/historical-basemaps/{REVISION}/'
YEARS=[-123000,-10000,-8000,-5000,-4000]
def main():
    raw=ROOT/'pipeline/raw/historical-basemaps'/REVISION;raw.mkdir(parents=True,exist_ok=True)
    rows=[]
    for year in YEARS:
        name=f'world_bc{abs(year)}.geojson';path=raw/name
        if not path.exists():
            with urllib.request.urlopen(BASE+'geojson/'+name,timeout=45) as response:path.write_bytes(response.read())
        content=path.read_bytes();data=json.loads(content)
        props=[f.get('properties',{}) for f in data['features']]
        names=sorted({str(p.get('NAME',p.get('name',''))) for p in props})
        rows.append({'year':year,'filename':name,'url':BASE+'geojson/'+name,'sha256':hashlib.sha256(content).hexdigest(),
                     'features':len(props),'fields':sorted({k for p in props for k in p}), 'names':names,
                     'has_feature_source_fields':sum(any('source' in k.lower() or 'citation' in k.lower() for k in p) for p in props),
                     'nonempty_weblinks':sum(bool(p.get('weblinks')) for p in props)})
        print(f'Reviewed {name}: {len(props)} features',flush=True)
    output={'revision':REVISION,'reviewed':'2026-11-15','status':'not imported',
            'upstream_licence_question':'https://github.com/aourednik/historical-basemaps/issues/74',
            'decision':'Do not ship this candidate import yet. Review unresolved data-licence scope, feature-specific sources and anachronistic/mixed culture-language-taxonomic labels. Repository GPL listing alone is not a completed provenance review.',
            'snapshots':rows}
    target=ROOT/'pipeline/reviews';target.mkdir(exist_ok=True)
    (target/'historical-basemaps.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
