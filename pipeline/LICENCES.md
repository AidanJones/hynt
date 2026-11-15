# Dataset and dependency licences

Application code: repository MIT licence. Data licences are separate.

## Distributed

- **Britain/Wales evidence compilation:** original factual summaries, references, date explanations and illustrative anchors are CC0-1.0. Cadw, museum, university and Coflein publications retain their own rights. No source images, maps, bulk exports or quoted descriptions are included. The compilation does not inherit a bulk dataset licence from the sources it links.

- **Technology evidence compilation:** original factual summaries, package definitions, illustrative coordinate anchors and schematic connections are dedicated under CC0-1.0. Institutional publications linked in `technologies.json` retain their own rights. No article text, museum images or bulk catalogue exports are included; citations and original paraphrases accompany the markers. Curation is not a claim that linked sites have an open redistribution licence.

- **Cliopatria / Seshat Global History Databank contributors:** CC BY 4.0. Revision `5f433377139a6eeaeacbdc894b70f8805b72c8b5`. [Original licence](https://github.com/Seshat-Global-History-Databank/cliopatria/blob/5f433377139a6eeaeacbdc894b70f8805b72c8b5/LICENSE.md). Attribution and changes accompany every feature through `sources.json`, the map footer and About dialog. Transformed geometry remains CC BY 4.0.
- **Natural Earth:** public domain. Low-resolution present-day land only, no modern political borders. [Terms](https://www.naturalearthdata.com/about/terms-of-use/). Input revision and hash recorded in `atlas/data/basemap-source.json`.
- **MapLibre GL JS 5.6.2:** BSD-3-Clause. Vendored distribution and licence in `atlas/vendor/`.

## Not yet cleared or imported

historical-basemaps, CShapes, AADR, DRH, ARDA, Glottolog and OpenHistoricalMap need source-version-specific redistribution and attribution review before fetching for distribution. Wikidata is CC0 but date precision, statement ranks, qualifiers and reference provenance still need handling. No licence is inferred from this document for a future import.
