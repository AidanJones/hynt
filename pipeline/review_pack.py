"""Publish the reviewed reference ledger and current mechanical overlap classes."""
import json
from collections import Counter
from pathlib import Path
from pipeline.package import read_collection
from pipeline.review_entities import temporal_review
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'atlas/data'
def main():
    baseline=json.loads((ROOT/'pipeline/reviews/entity-evidence.json').read_text(encoding='utf-8'))
    decisions=json.loads((ROOT/'pipeline/curated/identity-review.json').read_text(encoding='utf-8'))
    by_selector={(r['source_entity'],r['source_name'],r['source_article']):r for r in decisions['decisions']}
    manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'));features={}
    for c in manifest['chunks']:
        for f in read_collection(DATA/c['url'])['features']:features[f['properties']['id']]=f
    identities=[]
    for r in baseline['identities']:
        decision=by_selector.get((r['entity'],r['name'],r['article']))
        matching=[f['properties'] for f in features.values() if (p:=f['properties']).get('source_wikidata',p['entity'])==r['entity'] and p['name']==r['name'] and p.get('source_wikipedia',p.get('wikipedia',''))==r['article']]
        identities.append({**r,'current_entities':sorted({p['entity'] for p in matching}),
            'decision':decision['decision'] if decision else 'reference consistent' if r['status']=='consistent ID' else 'retained pending specific historical evidence',
            'reason':decision['reason'] if decision else 'An ID reference check is not a historical boundary or continuity judgement.',
            'review_reference':decision.get('review_reference') if decision else None})
    audit=json.loads((DATA/'audit.json').read_text(encoding='utf-8'))
    temporal=temporal_review(audit['same_entity_interval_overlaps'],features)
    result={'reviewed':baseline['reviewed'],'method':baseline['method'],'identities':identities,'temporal':temporal,
        'summary':{'decisions':dict(Counter(r['decision'] for r in identities)),
                   'temporal_geometry':dict(Counter(r['geometry_relation'] for r in temporal))}}
    (DATA/'review-evidence.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Published {len(identities)} identity reference checks and {len(temporal)} classified temporal pairs.')
if __name__=='__main__':main()
