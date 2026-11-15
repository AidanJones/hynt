"""Reproducible sampled spatial/temporal audit; flags are not historical verdicts."""
import json
from collections import defaultdict
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import shape,box
from shapely import transform
from shapely.strtree import STRtree
from pipeline.package import read_collection

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'atlas/data'
YEARS=[-3000,-1000,-1,1,117,750,1280,1700,1920,2024]
WINDOWS={
    'Europe':[-25,35,45,72], 'North Africa / Near East':[-20,0,60,35],
    'Africa south of 23N window':[-20,-36,55,23], 'South Asia':[60,0,100,35],
    'East Asia':[100,0,150,60], 'Americas':[-170,-55,-30,75],
    'Australia / New Guinea':[110,-50,180,0], 'Eurasian Steppe':[40,35,110,60]}

def overlap_pairs(features,minimum_km2=1):
    if not features:return []
    geometries=[shape(f['geometry']) for f in features]
    tree=STRtree(geometries)
    project=Transformer.from_crs(4326,6933,always_xy=True).transform
    projected={}
    def projected_shape(index):
        if index not in projected:projected[index]=transform(geometries[index],project,interleaved=False)
        return projected[index]
    pairs=[]
    for i,g in enumerate(geometries):
        for j in tree.query(g,predicate='intersects'):
            j=int(j)
            if j<=i:continue
            overlap=projected_shape(i).intersection(projected_shape(j)).area/1_000_000
            if overlap>minimum_km2:
                a,b=features[i]['properties'],features[j]['properties']
                pairs.append({'a':a['id'],'b':b['id'],'a_name':a['name'],'b_name':b['name'],
                    'same_entity':a['entity']==b['entity'],'overlap_km2':round(overlap,2)})
    return sorted(pairs,key=lambda x:(-x['overlap_km2'],x['a'],x['b']))

def audit(features,years=YEARS,windows=WINDOWS):
    grouped=defaultdict(list)
    for f in features:grouped[f['properties']['entity']].append(f['properties'])
    aliases=[];temporal=[]
    for entity,records in sorted(grouped.items()):
        names=sorted({p['name'] for p in records})
        if len(names)>1:aliases.append({'entity':entity,'names':names})
        ordered=sorted(records,key=lambda p:(p['from'],p['to'],p['id']))
        # Track all concurrent records, not just adjacent intervals.
        live=[]
        for record in ordered:
            live=[p for p in live if p['to']>record['from']]
            for p in live:temporal.append({'entity':entity,'a':p['id'],'b':record['id'],
                'from':max(p['from'],record['from']),'to':min(p['to'],record['to'])})
            live.append(record)
    samples=[]
    for year in years:
        active=[f for f in features if f['properties']['from']<=year<f['properties']['to']]
        counts={name:len({f['properties']['entity'] for f in active if shape(f['geometry']).intersects(box(*bounds))}) for name,bounds in windows.items()}
        pairs=overlap_pairs(active)
        samples.append({'year':year,'features':len(active),'entities':len({f['properties']['entity'] for f in active}),
            'regional_entity_counts':counts,'overlap_pairs_over_1_km2':len(pairs),'largest_overlaps':pairs[:30]})
    return {'method':'Ten sampled civil years; non-exclusive geographic windows; EPSG:6933 planar polygon intersection areas, threshold >1 km². Not an exhaustive annual audit, population count or adjudication of contested control. Antimeridian and projection effects require review.',
        'features':len(features),'entities':len(grouped),'windows':windows,'aliases':aliases,
        'same_entity_interval_overlaps':temporal,'samples':samples}

def main():
    manifest=json.loads((DATA/'manifest.json').read_text())
    unique={}
    for chunk in manifest['chunks']:
        for f in read_collection(DATA/chunk['url'])['features']:
            key=f['properties']['id']
            assert key not in unique or unique[key]==f,'Inconsistent boundary-spanning copy'
            unique[key]=f
    results=audit(list(unique.values()))
    notes=json.loads((ROOT/'pipeline/curated/review-notes.json').read_text(encoding='utf-8'))
    assert all(any(f['properties']['entity']==n['entity'] for f in unique.values()) for n in notes)
    (DATA/'review-notes.json').write_text(json.dumps(notes,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (DATA/'audit.json').write_text(json.dumps(results,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    rows='\n'.join('| '+str(s['year'])+' | '+str(s['entities'])+' | '+' | '.join(str(s['regional_entity_counts'][w]) for w in WINDOWS)+' | '+str(s['overlap_pairs_over_1_km2'])+' |' for s in results['samples'])
    decisions=json.loads((ROOT/'pipeline/date-decisions.json').read_text())
    report=f'''# Polity data audit

Generated with `python -m pipeline.audit`. {results['features']} distinct features, {results['entities']} entity keys. Every duplicated era-boundary record was checked for exact equality.

## Region / sampled-year counts

Counts are unique recorded entities whose geometry intersects a geographic window. Windows overlap and are explicitly defined in `atlas/data/audit.json`; these are not counts of peoples, regional population or exhaustive coverage. A zero means absent data in that window/year.

| Year | World | {' | '.join(WINDOWS)} | Overlap pairs >1 km² |
| --- | --- | {' | '.join('---' for _ in WINDOWS)} | --- |
{rows}

## Identity and temporal flags

- {len(results['aliases'])} entity keys have multiple source labels. Variants are preserved, not automatically split or merged.
- {len(results['same_entity_interval_overlaps'])} same-entity feature pairs overlap in validity. These can be components, aggregate claims or inconsistencies; they are not all errors.
- Largest spatial overlaps for each sample, feature IDs, alias sets and temporal pairs are in `atlas/data/audit.json`. Areas use EPSG:6933 and a >1 km² threshold; projection and antimeridian effects require review. Shared-edge touches do not count.
- Do not sum areas of overlapping empire aggregates and component records. A future territorial ranking needs explicit per-entity union and aggregation rules.

## Date-boundary decisions

{len(decisions)} records formerly excluded because their inclusive source endpoint is 0 are restored. For every valid civil year `y != 0`, `from <= y <= 0` is equivalent to `from <= y < 1`. Thus no valid source year is added or removed and no historical end date is inferred. The original zero endpoint is retained in `source_to`; the details panel labels the last included civil year as 1 BCE and explains the rule. All original fields and decisions are in `pipeline/date-decisions.json`. Starts at zero and reversed ranges still fail or remain quarantined.

## Historical interpretation checks

- Rome 117: a source record is present; its source-reported area is retained. This checks presence and provenance, not an expert vertex-by-vertex border reconstruction.
- Mongols 1280: the source uses an aggregate Mongol Empire shape after political fragmentation. The viewer now explains this when clicked, citing [Royal Armouries](https://royalarmouries.org/objects-and-stories/stories/the-mongols/fall-of-an-empire). It is not presented as proof of unified administration.
- Britain 1920: aggregate imperial and colonial records overlap, including multiple labels with Q8680. The viewer warns against additive areas and identical political-status assumptions. [The National Archives](https://www.nationalarchives.gov.uk/explore-the-collection/stories/the-imperial-conference-1926-and-the-origins-of-the-commonwealth-of-nations/) discusses the differing position of the dominions.

Expert review of detailed borders, source-label/QID reconciliation, unsampled years and disagreements between reconstructions remains open. Overlap alone does not justify a contested-history badge or deleting either source shape. No border has been redrawn in this audit.
'''
    (ROOT/'audit-report.md').write_text(report,encoding='utf-8')
    print(f"Audited {results['features']} features; {len(results['aliases'])} alias sets and {len(results['same_entity_interval_overlaps'])} temporal overlaps. Wrote audit-report.md.",flush=True)

if __name__=='__main__':main()
