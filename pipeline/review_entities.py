"""Fetch exact article identity references and classify every temporal flag.

This creates review evidence, not automatic identity or boundary corrections.
"""
import hashlib,json,time,urllib.parse,urllib.request
from collections import Counter
from pathlib import Path
from shapely.geometry import shape
from pipeline.package import read_collection
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'atlas/data'
USER_AGENT='HyntAtlas-source-review/0.1 (https://github.com/AidanJones/hynt)'

def geometry_interval_digest(features):
    digest=hashlib.sha256()
    for f in sorted(features,key=lambda f:f['properties']['id']):
        p=f['properties']
        value={'id':p['id'],'geometry':f['geometry'],**{k:p[k] for k in ['from','to','source_from','source_to']}}
        digest.update(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8'))
        digest.update(b'\n')
    return digest.hexdigest()

def canonical_rows(query,titles):
    normalized={r['from']:r['to'] for r in query.get('normalized',[])}
    redirects={r['from']:r for r in query.get('redirects',[])}
    pages={p['title']:p for p in query.get('pages',[])}
    result={}
    for original in titles:
        current=normalized.get(original,original);seen=set();fragment=False
        while current in redirects and current not in seen:
            seen.add(current);r=redirects[current];fragment|=bool(r.get('tofragment'));current=r['to']
        page=pages.get(current,{})
        props=page.get('pageprops',{})
        result[original]={'title':current,'qid':props.get('wikibase_item'),
            'revision':(page.get('revisions')or[{}])[0].get('revid'),
            'ambiguous':fragment or 'disambiguation' in props,'missing':not page or 'missing' in page}
    return result

def fetch_articles(titles):
    raw=ROOT/'pipeline/raw/article-review';raw.mkdir(parents=True,exist_ok=True)
    result={};provenance=[]
    for offset in range(0,len(titles),40):
        batch=titles[offset:offset+40]
        params={'action':'query','prop':'pageprops|revisions','ppprop':'wikibase_item|disambiguation',
            'rvprop':'ids','redirects':'1','format':'json','formatversion':'2','titles':'|'.join(batch)}
        url='https://en.wikipedia.org/w/api.php?'+urllib.parse.urlencode(params)
        path=raw/(hashlib.sha256(url.encode()).hexdigest()+'.json')
        if not path.exists():
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':USER_AGENT}),timeout=45) as response:
                path.write_bytes(response.read())
            time.sleep(0.25)
        body=path.read_bytes();data=json.loads(body)
        if 'error' in data:raise ValueError(data['error'])
        result.update(canonical_rows(data['query'],batch))
        provenance.append({'url':url,'sha256':hashlib.sha256(body).hexdigest()})
        print(f'Reviewed article references {offset+len(batch)}/{len(titles)}',flush=True)
    return result,provenance

def temporal_review(pairs,features):
    geometries={id:shape(f['geometry']) for id,f in features.items()}
    rows=[]
    ordinal=lambda year:year if year<0 else year-1
    for p in pairs:
        a,b=geometries[p['a']],geometries[p['b']]
        kind='identical footprint' if a.equals(b) else 'separate footprints' if a.intersection(b).area==0 else 'overlapping footprints'
        rows.append({**p,'geometry_relation':kind,'civil_years':ordinal(p['to'])-ordinal(p['from']),
            'historical_status':'unadjudicated'})
    return rows

def main():
    audit=json.loads((DATA/'audit.json').read_text(encoding='utf-8'))
    manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'));features={}
    for chunk in manifest['chunks']:
        for f in read_collection(DATA/chunk['url'])['features']:features[f['properties']['id']]=f
    flagged={a['entity'] for a in audit['aliases']}
    selectors=sorted({(p['entity'],p['name'],p.get('wikipedia','')) for f in features.values() if (p:=f['properties'])['entity'] in flagged})
    titles=sorted({article for _,_,article in selectors if article})
    references,provenance=fetch_articles(titles)
    rows=[]
    for entity,name,article in selectors:
        ref=references.get(article,{})
        status='missing reference' if not ref.get('qid') or ref.get('missing') else 'ambiguous article' if ref.get('ambiguous') else 'consistent ID' if ref['qid']==entity else 'ID conflict'
        rows.append({'entity':entity,'name':name,'article':article,**ref,'status':status,
            'reference':f'https://en.wikipedia.org/w/index.php?oldid={ref["revision"]}' if ref.get('revision') else None})
    temporal=temporal_review(audit['same_entity_interval_overlaps'],features)
    result={'reviewed':'2026-11-16','polity_revision':manifest['revision'],
        'input_manifest_sha256':hashlib.sha256((DATA/'manifest.json').read_bytes()).hexdigest(),
        'method':'Exact source article references only; fragment/disambiguation redirects are not accepted as identities. Temporal geometry classes are mechanical, not historical verdicts. No fuzzy merges or boundary edits.',
        'article_batches':provenance,'identities':rows,'temporal':temporal,
        'summary':{'identity_status':dict(Counter(r['status'] for r in rows)),
                   'temporal_geometry':dict(Counter(r['geometry_relation'] for r in temporal))}}
    target=ROOT/'pipeline/reviews/entity-evidence.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary']),flush=True)
if __name__=='__main__':main()
