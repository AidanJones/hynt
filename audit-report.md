# Polity data audit

Generated with `python -m pipeline.audit`. 13412 distinct features, 1444 entity keys. Every duplicated era-boundary record was checked for exact equality.

## Region / sampled-year counts

Counts are unique recorded entities whose geometry intersects a geographic window. Windows overlap and are explicitly defined in `atlas/data/audit.json`; these are not counts of peoples, regional population or exhaustive coverage. A zero means absent data in that window/year.

| Year | World | Europe | North Africa / Near East | Africa south of 23N window | South Asia | East Asia | Americas | Australia / New Guinea | Eurasian Steppe | Overlap pairs >1 km² |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -3000 | 4 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| -1000 | 11 | 4 | 9 | 1 | 0 | 1 | 0 | 0 | 2 | 3 |
| -1 | 44 | 18 | 9 | 4 | 9 | 8 | 3 | 0 | 16 | 18 |
| 1 | 45 | 17 | 9 | 4 | 10 | 8 | 3 | 0 | 16 | 17 |
| 117 | 36 | 7 | 6 | 4 | 10 | 9 | 3 | 0 | 12 | 10 |
| 750 | 75 | 37 | 8 | 4 | 18 | 13 | 3 | 2 | 17 | 41 |
| 1280 | 122 | 83 | 15 | 6 | 19 | 12 | 6 | 2 | 3 | 136 |
| 1700 | 106 | 42 | 24 | 20 | 24 | 25 | 9 | 11 | 19 | 157 |
| 1920 | 84 | 40 | 21 | 18 | 14 | 15 | 23 | 8 | 11 | 88 |
| 2024 | 192 | 58 | 54 | 54 | 13 | 18 | 40 | 9 | 21 | 75 |

## Identity and temporal flags

- 112 entity keys have multiple source labels. Variants are preserved, not automatically split or merged.
- 1525 same-entity feature pairs overlap in validity. These can be components, aggregate claims or inconsistencies; they are not all errors.
- Largest spatial overlaps for each sample, feature IDs, alias sets and temporal pairs are in `atlas/data/audit.json`. Areas use EPSG:6933 and a >1 km² threshold; projection and antimeridian effects require review. Shared-edge touches do not count.
- Do not sum areas of overlapping empire aggregates and component records. A future territorial ranking needs explicit per-entity union and aggregation rules.

## Date-boundary decisions

6 records formerly excluded because their inclusive source endpoint is 0 are restored. For every valid civil year `y != 0`, `from <= y <= 0` is equivalent to `from <= y < 1`. Thus no valid source year is added or removed and no historical end date is inferred. The original zero endpoint is retained in `source_to`; the details panel labels the last included civil year as 1 BCE and explains the rule. All original fields and decisions are in `pipeline/date-decisions.json`. Starts at zero and reversed ranges still fail or remain quarantined.

## Historical interpretation checks

- Rome 117: a source record is present; its source-reported area is retained. This checks presence and provenance, not an expert vertex-by-vertex border reconstruction.
- Mongols 1280: the source uses an aggregate Mongol Empire shape after political fragmentation. The viewer now explains this when clicked, citing [Royal Armouries](https://royalarmouries.org/objects-and-stories/stories/the-mongols/fall-of-an-empire). It is not presented as proof of unified administration.
- Britain 1920: aggregate imperial and colonial records overlap, including multiple labels with Q8680. The viewer warns against additive areas and identical political-status assumptions. [The National Archives](https://www.nationalarchives.gov.uk/explore-the-collection/stories/the-imperial-conference-1926-and-the-origins-of-the-commonwealth-of-nations/) discusses the differing position of the dominions.

Expert review of detailed borders, source-label/QID reconciliation, unsampled years and disagreements between reconstructions remains open. Overlap alone does not justify a contested-history badge or deleting either source shape. No border has been redrawn in this audit.
