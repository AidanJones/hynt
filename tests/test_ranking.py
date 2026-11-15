from shapely.geometry import box,mapping
from pipeline.ranking import derive
def test_ranking_unions_same_entity_without_summing_other_entities():
    def f(id,entity,west,east,start,end):
        return {'properties':{'id':id,'entity':entity,'name':entity,'from':start,'to':end},'geometry':mapping(box(west,0,east,1))}
    data=derive([f('a1','A',0,2,1,4),f('a2','A',1,3,1,3),f('b','B',0,2,1,4)])
    first=data['snapshots'][0][2]
    assert first[0][0]==0 # A is the union of width 3, not summed width 4.
    assert abs(first[0][1]/first[1][1]-1.5)<0.001
    assert len(data['snapshots'])==2
    assert data['snapshots'][1][0]==3
    assert len(data['history']['0'])==2
