# Regional technology coverage — 15 November 2026

The technology explorer now offers stable five-degree reporting chunks, clipped to Natural Earth present-day land between 60°S and 90°N. There are 955 land chunks. These are geographic indices, not historical cultures, equal-area regions or boundaries of adoption. Small islands absent from this low-resolution basemap remain a coverage limitation.

Choose one of seven packages to see the earliest selected evidence in each chunk. Thirty-two attestations are packaged, including nine new records: Egyptian writing at Abydos, developed Indus script, Linear B, early Maya writing, pre-conquest Commius coin inscriptions, Roman London tablets, the Moscow Mathematical Papyrus, Old Babylonian YBC 7289 and the Zhangjiashan mathematical manuscript. Mathematics (calculation and geometry) is distinct from algebra. All new sources and limitations are stored in `pipeline/curated/technology-regional.json`.

“Earliest” means earliest in this selection, ordered by the start of the evidence interval. It is not a verified first invention or arrival date. Overlapping date intervals may not establish which object is older. Named navigation groups such as Europe and South Asia are approximate geographical aids; the numeric chunk bounds are authoritative. A regional anchor is not a proven findspot. The explorer separates direct evidence, evidence still inside its date window, optional polity inference and no entry by the selected year.

## Optional polity assumption

The model finds all Cliopatria polygons covering the evidence anchor at the **latest endpoint** of its dating window. It marks land chunks having a non-zero-area overlap with those polygons. Those chunk assignments persist into later years, including beyond the polity dataset’s end. They preserve a hypothesis about past coverage, not a claim of continuous use. This coarse indexing can mark land outside the attested polity within the same chunk. It is explicitly disclosed in the legend and details.

The build currently produces 22 dated polity assignments. Each retains the seed attestation, date, original polity record ID, entity, temporal interval and pinned source revision. Competing/overlapping polity candidates are retained. The model does not infer a polity before its recorded interval, follow later territorial expansion or propagate through an already inferred chunk. An approximate anchor and uncertain historical borders also make the inference uncertain. An unrepresented polity produces no inference.

Coverage is a cumulative history even when point markers are filtered to date windows. Inferred chunks remain eligible for direct research. The chunk browser can filter to direct evidence, inference only or remaining gaps, and provides Wikipedia/web research links. It never turns a search result into evidence automatically. The viewer remains a static site without a live-search service or embedded credentials.

## Rebuild, rights and verification

Run `python -m pipeline.technologies`, then `python -m pipeline.technology_regions`. Both are included in the full build; regenerate the regional ledger whenever evidence or polity data changes. The ledger is deterministic and uses distributed packed era data. The 449 KB regional file leaves the static atlas below 15 MB. Original research summaries remain CC0, underlying polity data/derived assignments are attributed CC BY 4.0, and Natural Earth land is public domain. No article text or published historical maps were imported.

48 Python and 23 Node tests passed after this feature, including land partitioning, dated-polity containment, no recursive spread, latest-endpoint inference, BCE uncertainty, cumulative retention and backward-compatible share links. The regional Playwright suite passed desktop/mobile layouts, source and research links, inference/evidence switching, mathematics, disabled coverage and reload. Screenshots were inspected. These checks verify implementation, not complete global historical coverage.
