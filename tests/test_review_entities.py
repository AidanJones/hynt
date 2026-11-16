from pipeline.review_entities import canonical_rows,temporal_review
from shapely.geometry import box,mapping

def test_article_redirect_fragments_and_disambiguation_are_not_identity_matches():
    query={'normalized':[{'from':'Han_state','to':'Han state'}],
      'redirects':[{'from':'Han state','to':'Han','tofragment':'Former states'}],
      'pages':[{'title':'Han','pageprops':{'wikibase_item':'Q1','disambiguation':''},'revisions':[{'revid':123}]},
               {'title':'State','pageprops':{'wikibase_item':'Q2'},'revisions':[{'revid':456}]}]}
    rows=canonical_rows(query,['Han_state','State','Missing'])
    assert rows['Han_state']['ambiguous']
    assert not rows['State']['ambiguous'] and rows['State']['qid']=='Q2'
    assert rows['Missing']['missing']

def test_temporal_triage_distinguishes_duplicates_components_and_overlap_across_bce_ce():
    def f(geometry):return {'geometry':mapping(geometry)}
    features={'a':f(box(0,0,2,2)),'b':f(box(0,0,2,2)),'c':f(box(3,3,4,4)),'d':f(box(1,1,3,3))}
    pairs=[{'a':'a','b':id,'from':-1,'to':1,'entity':'X'} for id in ['b','c','d']]
    rows=temporal_review(pairs,features)
    assert [r['geometry_relation'] for r in rows]==['identical footprint','separate footprints','overlapping footprints']
    assert all(r['civil_years']==1 and r['historical_status']=='unadjudicated' for r in rows)

def test_distributed_polity_geometry_and_chronology_match_pre_review_baseline():
    import json
    from pathlib import Path
    from pipeline.package import read_collection
    from pipeline.review_entities import geometry_interval_digest
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'atlas/data/manifest.json').read_text(encoding='utf-8'))
    baseline=json.loads((root/'pipeline/reviews/geometry-preservation.json').read_text(encoding='utf-8'))
    features={}
    for c in manifest['chunks']:
        for f in read_collection(root/'atlas/data'/c['url'])['features']:features[f['properties']['id']]=f
    assert len(features)==baseline['features_checked']
    assert geometry_interval_digest(features.values())==baseline['geometry_interval_sha256']
