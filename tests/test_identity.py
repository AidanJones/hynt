import pipeline.identity as identity
def test_curated_identity_refresh_is_idempotent_and_can_be_reversed(monkeypatch):
    source={'name':'Republic of Korea','wikipedia':'South Korea','entity':'Q423','wikidata':'Q423','from':1948,'to':2025}
    corrected=identity.apply_identity(source)
    assert corrected['entity']=='Q884'
    assert identity.apply_identity(corrected)==corrected
    monkeypatch.setattr(identity,'CROSSWALK',[])
    assert identity.apply_identity(corrected)==source
    assert source['entity']=='Q423'
