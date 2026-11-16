# Source review follow-up — 15 November 2026

**16 November update:** [The next review pass](review-pass-2026-11-16.md) adds 34 exact identity corrections and a complete reference/temporal classification ledger. [Selected culture snapshots](culture-report.md) are now separately distributed with the published GPL terms and corresponding source. The earlier withholding decision and counts below describe the previous increment. Exhaustive historical border adjudication remains open.

## Entity and border review

The audit is now browsable at `atlas/review.html`: search aliases, concurrent source records and the largest spatial overlaps retained at the ten sampled years; each entry opens the relevant year/entity in the atlas. Original IDs remain visible. These are diagnostics, not automatic historical corrections. Full annual or expert border adjudication is not claimed.

A concrete identity collision was investigated: Cliopatria assigns `Q1068371` to both ancient Chinese **Han Dynasty** records (whose own further-reading field is “Han dynasty”) and **Chauhan Dynasty** records in medieval South Asia. [Wikidata’s Han dynasty item](https://www.wikidata.org/wiki/Q7209) identifies `Q7209`. The exact source QID/name/article combination is now corrected through `pipeline/curated/entity-crosswalk.json`. The original QID and cited reason are retained in each affected shape and displayed in its details. The correction changes entity grouping, search, colours, rankings and history; it does not alter any geometry or date. Other aliases have not been silently rewritten.

Three further exact source name/article collisions were corrected after checking their canonical identities: ancient Lu → [Q736936](https://www.wikidata.org/wiki/Q736936), South Korea → [Q884](https://www.wikidata.org/wiki/Q884), and South Vietnam → [Q180573](https://www.wikidata.org/wiki/Q180573). They had been grouped with Aq Qoyunlu, North Korea and North Vietnam respectively. No source dates or shapes change. Identity refresh is idempotent and can restore the original grouping if a curated decision is removed; `python -m pipeline.reconcile` refreshes packed identities and derived layers without rerunning geometry processing.

All 140 remaining label groups from the first pass were inspected for candidate name collisions; only the three independently verified exact matches above were changed. The final audit has 137 alias sets, 1,545 same-entity temporal-overlap pairs and 1,415 entity identities. A Han (state) article now redirects to a disambiguation page, demonstrating why article redirects and suggestive names are not automatically sufficient for a correction. Other cases remain unresolved.

The prior Mongol aggregate and British imperial component notes remain. Shared-label warnings now appear in source details, ranked rows and entity histories, with links into the review queue; search includes source aliases. Remaining identity/temporal/spatial flags require case-specific scholarly checks; high overlap counts do not imply that shapes should be deleted. The Beads border-review task remains open for that work.

## Prehistoric candidate import

`python -m pipeline.culture_review` inspected historical-basemaps revision `4b5039e50d8d2464b065bd76ad6086cd4597108d`. Five candidate snapshots at 123000, 10000, 8000, 5000 and 4000 BCE contain 157, 135, 134, 279 and 136 features respectively. Download URLs, SHA-256 hashes, field names and candidate labels are recorded in `pipeline/reviews/historical-basemaps.json`; downloaded geometry stays in the ignored raw cache and is not shipped.

The repository lists GPL-3.0, but [upstream issue 74](https://github.com/aourednik/historical-basemaps/issues/74) remains open asking whether that licence applies to the GeoJSON data. This is an unresolved provenance/reuse question, not a claim that GPL data cannot be used. The candidate snapshots also mix taxonomic, language, broad subsistence and archaeological labels. Labels such as “Bantu” in the 8000 BCE snapshot need specific historical support rather than automatic display as an archaeological culture. Feature-specific references and any interpretation of `BORDERPRECISION` need review; numerical precision alone does not measure historical confidence.

The import task remains blocked on a documented data-licence/provenance decision and sufficiently supported culture classifications. The working deep-time site/migration layer continues to use its separate cited evidence. No invented replacement cultural borders were drawn.
