# Technology and knowledge layer

## Coverage expansion

The selection now has **six packages, 23 attestations and 19 source references**. Writing and paper join farming, ironworking, algebra and printing. Added records cover New Guinea cultivation, Mexican maize/squash, Uruk records, Shang inscriptions, Welsh iron objects, Meroe production, Brahmagupta's work at Bhinmal, Cai Lun's traditional report and an Egyptian paper object. These add regional evidence, not new unsupported transmission arrows.

Additional editable records live in `pipeline/curated/technology-expansion.json`; the pipeline merges that file with the initial compilation and rejects duplicate IDs. BP-dated records retain their original calibrated ranges and use a fixed 1950 CE epoch. The civil-year conversion explicitly skips year zero; the original BP labels remain visible.

The earlier starting-selection notes below are retained for context; the expansion supersedes their counts and the gaps it fills. The layer is still a small selection, with particularly sparse coverage of South America, much of Africa and many independent mathematical traditions.

Added 15 November 2026. The original curated compilation is in `pipeline/curated/technologies.json`; run `python -m pipeline.technologies` to validate and package it independently of the polity rebuild. The full build runs this step too.

- Four selectable packages: farming/herding, ironworking, algebra and movable-type printing.
- Thirteen dated attestations with nine cited institutional or scholarly references.
- Two evidenced connections: Arabic algebra to Robert of Chester's Latin translation, and Caxton's move from Bruges to Westminster. Lines are schematic connections, not reconstructed travel paths or simulated transit durations.
- Timeline extended to 10,000 BCE to make early farming evidence accessible. Polity coverage still begins in 3400 BCE; earlier years show the technology layer and an explicit coverage notice.
- “Recorded by this year” accumulates past evidence. It does not assert that a technology stayed in use or that everybody in a surrounding area adopted it. “Dated to this year” restricts markers to the cited date interval.
- Hollow markers mean the selected year is inside a dating window. Approximate singleton dates remain labelled approximate in details; they are not silently given invented error bars.
- Regional, city and site-vicinity anchors are distinguished. Coordinates are illustrative geography, not territorial extents or surveyed locations. Package components and components actually evidenced at each marker are listed separately.
- No Korea-to-Mainz printing arrow, Tell Hammeh-to-Beth-Shemesh iron transfer, or global adoption polygons are inferred merely from chronological order.

## Limits

This is a small curated starting selection, not a global inventory or technology ranking. Africa, the Americas, South Asia and many independent traditions require expansion. Ironworking currently has two Levantine production-site examples and no claimed origin point. Agriculture outside the selected Middle East/European sequence, paper, writing, steel and advanced mathematical traditions remain unpopulated. Guns, Germs, and Steel is inspiration for the feature, not the sole authority for its evidence.

The Britain/Wales evidence layer is now implemented separately, with archaeological sites, metalwork, named rulers and community attestations. Its interpretation rules and starting selection are recorded in `PRE_ROMAN_BRITAIN.md` and Bead `hynt-britain`.
