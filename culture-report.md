# Selected archaeological culture snapshots — 16 November 2026

The optional culture layer now contains six snapshots for Jōmon, Ubaid and Narva. Use **Selected archaeological cultures**, then the 5000 BCE tour. These are partial archaeological reconstructions, separate from polities, languages, ancestry and migration routes. Unknown regions remain blank.

Inputs are selected unchanged features from historical-basemaps revision `4b5039e50d8d2464b065bd76ad6086cd4597108d`. The repository's published GPL-3.0 terms were re-read, including their application to other works. This selected distribution follows those terms: it includes the full licence, attribution, corresponding selected source and transformation recipe. The viewer remains MIT; the imported dataset is separately GPL-3.0-only. [Upstream licence clarification issue 74](https://github.com/aourednik/historical-basemaps/issues/74) remains open; this review does not claim that the author has answered it. This supersedes the earlier decision to withhold all candidate geometry.

`pipeline/curated/culture-sources.json` preserves the original selected features, source URLs, hashes and indices. `pipeline/curated/cultures.json` records individual interpretation decisions and independent archaeological references. `python -m pipeline.cultures` repairs invalid geometry and simplifies by 0.01 degrees. Public source and licence are in `atlas/data/cultures/`.

Jōmon outlines omit documented northern sites, so their names explicitly say **partial source footprint**. Ubaid's southern Mesopotamian footprint omits its wider material distribution. Narva's date is supported by the cited Estonian chronology; the wider Baltic outline remains the source author's interpretation. Independent references support context and period, not each polygon vertex.

Snapshots persist until the next selected source window or the 3400 BCE import cutoff. This is an explicit display assumption; the cutoff does not indicate the end of a tradition. Overlap is allowed. The import excludes the unsupported 8000 BCE Bantu label, hominin taxonomic regions and the questionable 5000 BCE Funnel Beaker candidate. No bulk culture import or complete prehistoric coverage is claimed.

Unit and browser checks cover source reproducibility, required references, interval boundaries, separate polygons, selection, URL persistence, licence links and mobile controls.
