"""Apply only explicit, cited exact-match identity decisions; never fuzzy merges."""
import json
from pathlib import Path
CROSSWALK=json.loads((Path(__file__).resolve().parent/'curated/entity-crosswalk.json').read_text(encoding='utf-8'))
def apply_identity(properties):
    p=dict(properties)
    original=p.get('source_wikidata',p.get('wikidata',''))
    if 'source_wikidata' in p:
        p.update(entity=original,wikidata=original)
        for key in ['source_wikidata','identity_note','identity_source']:p.pop(key,None)
    matches=[r for r in CROSSWALK if r['source_entity']==original and r['source_name']==p['name'] and r['source_wikipedia']==p.get('wikipedia','')]
    assert len(matches)<=1,'Ambiguous curated identity selector'
    if matches:
        r=matches[0]
        p.update(entity=r['entity'],wikidata=r['entity'],source_wikidata=original,identity_note=r['reason'],identity_source=r['source'])
    return p


def entity_index(features):
    entities={};labels={}
    for f in sorted(features,key=lambda f:f['properties'].get('source_record',0)):
        p=f['properties'];e=entities.setdefault(p['entity'],{'id':p['entity'],'name':p['name'],'from':p['from'],'to':p['to']})
        e['from']=min(e['from'],p['from']);e['to']=max(e['to'],p['to'])
        labels.setdefault(p['entity'],set()).add(p['name'])
    for id,names in labels.items():
        if len(names)>1:entities[id]['aliases']=sorted(names)
    return sorted(entities.values(),key=lambda e:e['name'])
