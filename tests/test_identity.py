import pipeline.identity as identity
def test_curated_identity_refresh_is_idempotent_and_can_be_reversed(monkeypatch):
    source={'name':'Republic of Korea','wikipedia':'South Korea','entity':'Q423','wikidata':'Q423','from':1948,'to':2025}
    corrected=identity.apply_identity(source)
    assert corrected['entity']=='Q884'
    assert identity.apply_identity(corrected)==corrected
    monkeypatch.setattr(identity,'CROSSWALK',[])
    assert identity.apply_identity(corrected)==source
    assert source['entity']=='Q423'

def test_corrected_reading_link_preserves_original_and_is_reversible(monkeypatch):
    source={'name':'Southern Liang','wikipedia':'Liang dynasty','entity':'Q1069868','wikidata':'Q1069868','from':397,'to':414}
    corrected=identity.apply_identity(source)
    assert corrected['entity']=='Q1330290' and corrected['source_wikipedia']=='Liang dynasty'
    assert corrected['wikipedia']=='Southern Liang (Sixteen Kingdoms)'
    assert identity.apply_identity(corrected)==corrected
    monkeypatch.setattr(identity,'CROSSWALK',[])
    assert identity.apply_identity(corrected)==source
