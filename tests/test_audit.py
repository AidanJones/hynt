from shapely.geometry import box,mapping
from pipeline.audit import audit,overlap_pairs

def feature(id,entity,name,geometry,start=1,end=5):
    return {'type':'Feature','id':id,'properties':{'id':id,'entity':entity,'name':name,'from':start,'to':end},'geometry':mapping(geometry)}

def test_shared_edges_are_not_spatial_overlaps_and_real_overlap_is_flagged():
    a=feature('a','e1','A',box(0,0,2,2))
    b=feature('b','e2','B',box(2,0,3,2))
    c=feature('c','e1','A part',box(1,0,2,1))
    assert overlap_pairs([a,b])==[]
    pairs=overlap_pairs([a,c])
    assert len(pairs)==1 and pairs[0]['same_entity'] and pairs[0]['overlap_km2']>10000

def test_audit_distinguishes_aliases_temporal_flags_and_nonexclusive_windows():
    records=[feature('a','e','A',box(0,0,1,1),1,5),feature('b','e','A part',box(.5,.5,1.5,1.5),3,6)]
    result=audit(records,years=[2,3,6],windows={'sample':[0,0,2,2]})
    assert result['aliases'][0]['names']==['A','A part']
    assert len(result['same_entity_interval_overlaps'])==1
    assert [s['entities'] for s in result['samples']]==[1,1,0]
    assert result['samples'][1]['regional_entity_counts']['sample']==1
