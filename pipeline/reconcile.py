"""Refresh cited identities in packed data without repeating geometry processing."""
import json,hashlib,re
from pathlib import Path
from pipeline.identity import apply_identity,entity_index
from pipeline.package import read_collection,pack_collection,unpack_collection,deterministic_gzip
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'atlas/data'
def main():
    manifest_path=DATA/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));features={}
    for chunk in manifest['chunks']:
        path=DATA/chunk['url'];collection=read_collection(path)
        for f in collection['features']:
            original_geometry=f['geometry']
            f['properties']=apply_identity(f['properties'])
            assert f['geometry'] is original_geometry
            features[f['properties']['id']]=f
        packed=pack_collection(collection);assert unpack_collection(packed)==collection
        encoded=json.dumps(packed,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
        compressed=deterministic_gzip(encoded);path.write_bytes(compressed)
        chunk.update(bytes=len(compressed),sha256=hashlib.sha256(compressed).hexdigest(),expanded_bytes=len(json.dumps(collection,ensure_ascii=False,separators=(',',':')).encode('utf-8')))
    manifest_path.write_text(json.dumps(manifest,separators=(',',':')),encoding='utf-8')
    entities={}
    for f in sorted(features.values(),key=lambda f:f['properties']['source_record']):
        p=f['properties'];e=entities.setdefault(p['entity'],{'id':p['entity'],'name':p['name'],'from':p['from'],'to':p['to']})
        e['from']=min(e['from'],p['from']);e['to']=max(e['to'],p['to'])
    (DATA/'entities.json').write_text(json.dumps(entity_index(list(features.values())),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    report=json.loads((DATA/'packaging-report.json').read_text(encoding='utf-8'))
    report.update(original_bytes=sum(c['expanded_bytes'] for c in manifest['chunks']),shipped_bytes=sum(c['bytes'] for c in manifest['chunks']),largest_chunk_bytes=max(c['bytes'] for c in manifest['chunks']))
    (DATA/'packaging-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    from pipeline.audit import main as audit
    from pipeline.ranking import main as ranking
    from pipeline.technology_regions import main as regions
    audit();ranking();regions()
    from pipeline.review_pack import main as review_pack
    review_pack()
    build_report=ROOT/'build-report.md'
    if build_report.exists():
        text=build_report.read_text(encoding='utf-8')
        text=re.sub(r'(input records; \d+ polity shapes; )\d+( entity keys\.)',lambda m:m[1]+str(len(entities))+m[2],text)
        marker='\nIdentity refresh: '
        text=text.split(marker)[0].rstrip()
        corrected=sum('source_wikidata' in f['properties'] for f in features.values())
        text+=f'\n\nIdentity refresh: {corrected} records have cited exact-match identity decisions; {len(entities)} entity keys. Geometry and source date ranges are unchanged. See source-review-report.md.\n'
        build_report.write_text(text,encoding='utf-8')
    print(f'Reconciled {len(features)} shapes into {len(entities)} identities; geometry untouched.')
if __name__=='__main__':main()
