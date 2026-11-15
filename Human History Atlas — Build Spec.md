# Human History Atlas — Build Spec

Nov 15, 2026 · @Aidan Jones

## Overview

Build a static, single-page web map with a time slider running from Homo sapiens leaving Africa to today. At any year it shows who held which land, the dominant religion, the most influential power and key events, and every shape on the map links to its sources.

**Goals**

- One `index.html` page in plain HTML, CSS and JavaScript, with no React, no framework and no build step for the viewer. It is served as static files.
- A time slider covering \~300,000 years ago to 2026 CE. It steps one year at a time from 3400 BCE onward and in coarser steps before that.
- Parallel layers: peoples and cultures, polities (states and empires), religion, influence ranking, migrations and key events.
- Filters and focus: zoom to a region, follow one people or polity through time, and toggle layers on and off.
- Every feature carries its sources and a further-reading link, and shows how confident the data is.

**Non-goals for v1**

- Editing data in the browser. The data is changed in the pipeline and rebuilt.
- A server or database. Everything is precomputed into static files.
- Population-level detail inside polities. A polygon means "this polity claimed or controlled this area", not that everyone there shared one identity.

## Data model

Don't store GeoJSON per year. Each feature is one shape of one entity, valid over a range of years `[from, to)`. The viewer shows a feature when `from <= year < to`. When an empire's borders change, it gets a new feature with a new range. This is how Cliopatria already stores polities, and it lets MapLibre filter by year on the GPU with no file swapping.

**Years** are integers, with negative numbers for BCE and no year 0 (−1 = 1 BCE). For deep prehistory the UI also shows "years ago" (2026 − year).

**Common feature properties** (all layers):

| Property | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable ID, e.g. `polity:roman-empire:0042` |
| `entity` | string | Entity ID shared by every shape of the same people, polity or religion |
| `name` | string | Display name |
| `layer` | enum | `people`, `polity`, `religion`, `migration`, `event` |
| `from`, `to` | int | Valid year range, `to` exclusive |
| `kind` | string | e.g. `empire`, `city-state`, `archaeological-culture`, `language-family`, `state-religion` |
| `confidence` | enum | `high`, `medium`, `low`, `speculative` |
| `sources` | string\[\] | IDs into `sources.json` |
| `wikidata` | string | QID, used for further-reading links and relations |
| `colour` | string | Optional; otherwise derived from `entity` hash |

**Layer-specific additions**

- **Polity:** `area_km2` (computed in the pipeline), `religion_official` (entity ID), `capital` \[lon, lat\].
- **People / culture:** `language_family`, `subsistence` (forager, farmer, pastoralist), `genetic_ancestry` notes.
- **Migration:** LineString features with `from`, `to`, a `progress` property so a route can draw itself over time, and `group` (entity ID).
- **Event:** Point features with `year` (or `from` and `to` for long events), `category` (battle, founding, migration milestone, religious, technology, catastrophe), `importance` 1–3 for label density.

* **Campaign:** LineString with per-waypoint years, `attacker`, `defender`, `outcome`, `strength`, `importance`. Drawn as invasion arrows (see Viewer).

**Supporting files**

- `sources.json` maps source ID to `{title, author, year, url, licence, citation, type}`. Popups render from here.
- `relations.json` holds typed edges between entities, each with year and sources: `succeeded_by`, `conquered_by`, `absorbed_into`, `split_into`, `migrated_from`, `converted_to`. This is what drives "who took over whom".
- `influence.json` lists, for each year step, the top N polities with scores and the metric used.

## Data sources

No single dataset covers all of this. Use Cliopatria as the backbone for states from 3400 BCE, historical-basemaps before that, Wikidata for events and relations, and a small hand-curated layer for prehistoric migrations and religion spread. Check every licence before redistributing data in the repo; anything unclear goes into `pipeline/LICENCES.md` as an open question.

| Layer | Source | Coverage | Used for | Licence |
| --- | --- | --- | --- | --- |
| Polities | [Cliopatria](https://github.com/Seshat-Global-History-Databank/cliopatria) (Seshat) | 3400 BCE – 2024 CE, 1,800+ polities, one GeoJSON | Primary borders. Includes only polities attested in written sources, ≥5,000 km² and lasting ≥50 years ([paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11822181/)) | Check repo LICENSE |
| Polities, prehistoric cultures | [historical-basemaps](https://github.com/aourednik/historical-basemaps) | `world_YYYY.geojson` snapshots, prehistory – 2010 | Pre-3400 BCE cultural regions; cross-check; `BORDERPRECISION` field → `confidence` | Listed as GPL-3.0; confirm |
| Polity attributes | [Seshat API](https://seshat-global-history-databank.readthedocs.io) | Sampled polities | Population estimates, religion variables, for influence scoring | Check |
| Modern borders | [CShapes 2.0](https://icr.ethz.ch/data/cshapes/) | 1886 – 2019 | Higher-precision modern state borders | Check |
| Events, relations, religion of state | [Wikidata SPARQL](https://query.wikidata.org) | All periods | Battles and events (`P585` date, `P625` coords); replaces/replaced by (`P1365`/`P1366`), follows/followed by (`P155`/`P156`); official religion (`P3075`); Wikipedia links for further reading | CC0 |
| Peoples (genetic evidence) | [AADR, Reich Lab](https://reich.hms.harvard.edu/allen-ancient-dna-resource-aadr-downloadable-genotypes-present-day-and-ancient-dna-data) | Thousands of ancient genomes with date + location | Dated sample points, evidence for migrations and population replacement | Check |
| Languages | [Glottolog](https://glottolog.org) | Present-day languages, families | Language-family layer, modern end only | CC BY 4.0 |
| Religion (history) | [Database of Religious History](https://religiondatabase.org) | Religious groups with GIS region + date range | Religion polygons where available | Check |
| Religion (modern) | [ARDA World Religion Dataset](https://www.thearda.com/data-archive?fid=WRPGLOBL) | Adherents by country, every 5 years 1945 – 2010 | Majority-religion fill on modern borders | Check |
| Base map | [Natural Earth](https://www.naturalearthdata.com) | Present-day land, rivers, relief | Background; no modern borders shown by default | Public domain |
| Crowd-sourced extras | [OpenHistoricalMap](https://www.openhistoricalmap.org) | Patchy, detailed in places | Optional local detail later | Check |

**Hand-curated data** (`pipeline/curated/*.yaml`, each entry with sources):

- Out-of-Africa and later dispersal routes, with dated waypoints (Arabia, Sahul \~60,000 years ago, Europe \~40,000, Beringia and the Americas). Source from peer-reviewed syntheses, not videos.
- Major Holocene migrations: early farmers spreading from Anatolia, steppe/Yamnaya expansion, Bantu expansion, Austronesian expansion, Norse expansion, Turkic and Mongol expansions, and so on.
- Religion spread polygons for periods with no polity proxy, e.g. the spread of Buddhism along trade routes.
- Key events list (\~200 to start), merged with the Wikidata query results.

## Data pipeline

Python scripts in `pipeline/` turn raw sources into the small, uniform files the viewer loads. One `make data` rebuilds everything, and raw downloads are cached in `pipeline/raw/` (gitignored).

1. **Fetch.** Download the Cliopatria release zip, the historical-basemaps GeoJSONs, Natural Earth, and the ARDA/AADR/Glottolog files. Run Wikidata SPARQL queries and save the results as JSON. Record the version, date and URL of every download in `sources.json`.
2. **Normalise.** Use geopandas to map each source's fields onto the common schema (Data model). Convert snapshot sources (historical-basemaps) into ranges: snapshot *i* is valid from its year until snapshot *i+1*. Fix invalid geometries (`make_valid`) and reproject to EPSG:4326.
3. **Reconcile entities.** Match the same entity across sources using its Wikidata QID first, then name plus overlap in time and space. Write a `crosswalk.csv` that a person can correct by hand. Cliopatria wins where sources disagree; others fill gaps.
4. **Merge curated YAML.** Validate the curated migrations, events and religion entries against a JSON Schema. Fail the build if any entry has no `sources`.
5. **Derive.**
   - `area_km2` per polity feature, using an equal-area projection.
   - Religion layer: attach `P3075` official religion to polity features and dissolve by religion for each period, labelled "official religion of the ruler". Use ARDA majority religion from 1945. Overlay curated and DRH polygons.
   - `influence.json`: for each year step, rank polities by area (v1). Add Seshat population where available (v2). Store the metric name with the scores so the UI can say what it is ranking.
   - `relations.json` from Wikidata `P1365`/`P1366`/`P155`/`P156` plus curated edges, typed as conquered, absorbed, split or succeeded.
6. **Simplify and package.** Run mapshaper with topology preserved and a \~2–5 km tolerance at world zoom, aiming for under 15 MB total. Split polities into era chunks (e.g. `-3400_-500`, `-500_500`, `500_1500`, `1500_1900`, `1900_2026`) so the viewer loads only what it needs. Later, optionally build PMTiles with tippecanoe for detail at high zoom.
7. **Validate.** Every feature has `from < to`, a known `entity`, at least one source, and a valid geometry. Same-layer polities may overlap (contested land) but get flagged in a report. Write `build-report.md` with counts per layer and era, plus gaps.

## Viewer

A full-screen map with a timeline along the bottom, layer controls on the left, and a details panel on the right that opens when you click something. It should work on a phone too, with the panels becoming bottom sheets.

**Time slider**

- The scale is piecewise rather than linear, so prehistory doesn't swallow the bar: 300,000–12,000 years ago in 1,000-year steps, 10,000–3400 BCE in 50-year steps, and 3400 BCE–2026 CE year by year. Era bands sit under the track (Palaeolithic, Neolithic, Bronze Age, Classical, Medieval, Early modern, Modern).
- Play/pause with speed options (e.g. 1, 10, 100 years/sec, auto-scaled in prehistory), step buttons, keyboard arrows, and a year box that accepts `55000 ya`, `300 BCE` or `1066`.
- Markers on the track for events in view, with density limited by `importance`.
- Changing year only updates a MapLibre filter (`["all", ["<=", ["get","from"], y], [">", ["get","to"], y]]`). Load the next era chunk ahead of time while playing.

**Layers** (each toggleable, with opacity)

- **Peoples and cultures:** archaeological cultures and ethnolinguistic groups as soft, hatched fills, plus optional ancient-DNA sample dots that fade in over a ±500-year window.
- **Polities:** solid fills with borders. Line style shows confidence: solid for high, dashed for low, dotted for speculative.
- **Religion:** fill by religion. Label it "official religion" before 1945 and "majority religion" after.
- **Influence:** dims everything except the top N polities and shows a leaderboard card (rank, name, score, metric) for the current year.
- **Migrations:** animated routes that draw themselves between `from` and `to`, with arrowheads.
- **Events:** point markers with icons by category, clustered at low zoom.

**Invasion arrows** (Dad's Army style)

Invasions and campaigns are drawn as thick, curved, tapering arrows in the attacker's colour. They sweep out from the origin and grow along their route as the year advances, like the arrows in a wartime newsreel map.

- **Data:** `campaigns.geojson`, a LineString per thrust, with waypoints each stamped with a year (and month or day where known), plus `attacker`, `defender`, `outcome` (`advance`, `repulsed`, `retreat`), `strength` (sets arrow width) and `sources`. Seed it from Wikidata invasions and military campaigns, then curate the big ones (Alexander, Mongols, Norse raids, 1066, Napoleon, WW1/WW2 fronts).
- **Rendering:** an SVG overlay on top of the map, re-projected with `map.project()` on every move or zoom. Each arrow is a smoothed curve through its waypoints, turned into a filled shape that is wide at the tail and narrows to a big arrowhead. A shadow or outline helps it read as a bold arrow.
- **Animation:** the arrow's length follows the slider. At any year it reaches the last waypoint passed, and the head slides between waypoints. When `outcome` is `repulsed` or `retreat`, a counter-arrow in the defender's colour pushes back along the route.
- **Clutter control:** show only campaigns active within ±N years of the slider, fade them afterwards, and use `importance` to thin them at world zoom. Arrows can be toggled independently of the events layer.
- **Click:** opens the campaign in the details panel with its dates, sides, outcome, sources and further reading.

**Side-by-side comparison:** a split view with two synced maps at the same year and camera, e.g. polities on the left and religion on the right. A swipe-divider mode can come later.

**Filters and focus**

- **Region focus:** presets (British Isles, Mediterranean, Near East, Eurasian Steppe, South Asia, East Asia, Sub-Saharan Africa, Americas, Oceania), or draw a box. The camera flies there, and the event list and leaderboard narrow to it.
- **Group focus:** search any people, polity or religion. The rest of the map fades, the slider highlights that entity's lifespan, and the panel shows its history: origins, shape over time (a small area chart), relations ("conquered by", "absorbed into", "succeeded by"), each linked so you can jump.
- **Filters:** event categories, polity kinds (empire, kingdom, city-state, tribal confederation), a minimum confidence level, and region.
- **Takeover moments:** when an entity ends and a relation exists, briefly draw an arrow from the old area to the successor, labelled with the relation type.

**Details panel** (on click)

- Name, years, kind, a short description (from Wikidata or curated), and a confidence badge with an explanation.
- **Sources:** every entry in `sources` rendered as a citation with a link.
- **Further reading:** the Wikipedia article via the Wikidata sitelink, plus curated links.
- Related entities and relations, plus events inside this entity during its lifespan.

**Shareable state:** year, layers, focus and camera live in the URL hash (`#y=-300&l=polity,religion&f=Q2277&c=12.5,41.9,4`). Changing it updates the view, so any view can be linked to.

**About panel:** lists all datasets with licences and versions, explains the caveats (last section), and links to the GitHub repo for corrections.

## Tech choices and layout

Use MapLibre GL JS for the map. It runs from a CDN `<script>` tag with no build step, renders large GeoJSON on the GPU, filters by year with expressions, and supports globe view. Leaflet would struggle with thousands of polygons being re-filtered on every slider tick.

| Concern | Choice |
| --- | --- |
| Viewer | `index.html` + ES modules (`app.js`, `timeline.js`, `layers.js`, `panel.js`, `state.js`) + `style.css`. No framework, no bundler |
| Map | MapLibre GL JS v5 (CDN), globe toggle, Natural Earth raster/vector background |
| Charts in panel | Hand-written SVG (area-over-time sparkline, leaderboard bars) |
| Pipeline | Python 3.12: geopandas, shapely, pyproj, requests, SPARQLWrapper, PyYAML, jsonschema. mapshaper (npm) for simplification. Optional tippecanoe + pmtiles |
| Hosting | Any static host (GitHub Pages works). `python -m http.server` locally |
| Performance budget | First view under 3 s on broadband, under 5 MB initial download, 60 fps while scrubbing at world zoom |
| Tests | pytest for pipeline validation, plus a Playwright smoke test that loads the page, scrubs to 5 years and checks features render |

```
atlas/
  index.html  style.css  app.js  timeline.js  layers.js  panel.js  state.js
  data/
    sources.json  relations.json  influence.json  events.geojson
    polities/era_-3400_-500.geojson …
    peoples/*.geojson  migrations.geojson  religion/*.geojson
  pipeline/
    Makefile  fetch.py  normalise.py  reconcile.py  derive.py  package.py  validate.py
    curated/migrations.yaml  events.yaml  religion.yaml
    schema/*.json  crosswalk.csv  LICENCES.md
  tests/
```

## Milestones

Build in this order, so there's a working map after milestone 1 and every later step adds a layer. Each milestone ends with a demo URL and an updated `build-report.md`.

1. **Skeleton and polities.** Pipeline for Cliopatria only, plus the viewer with a year-by-year slider from 3400 BCE to 2026, polity fills, click for details with sources and a Wikipedia link, and URL state.
   - *Done when:* scrubbing 3400 BCE → 2026 is smooth; Rome in 117 CE, the Mongol Empire in 1280 and the British Empire in 1920 look right; every click shows at least one source.
2. **Deep time and migrations.** Piecewise slider back to \~300,000 years ago, historical-basemaps prehistoric snapshots, curated out-of-Africa routes, and the Holocene migrations with animated routes.
   - *Done when:* playing from 100,000 years ago shows routes reaching Sahul, Europe and the Americas at the dates in their cited sources.
3. **Events, relations and invasion arrows.** Wikidata events and curated events, filter by category, "takeover" arrows from `relations.json`.
   - *Done when:* in 1066 Hastings and Stamford Bridge both appear; scrubbing past 476 shows the Western Roman Empire's end and what took its land; playing 1066 shows Harald's and William's arrows converging on England.
4. **Religion.** Official religion before 1945, ARDA majority religion after 1945, curated spread polygons, and side-by-side compare.
   - *Done when:* compare view at 750 CE shows Umayyad lands as Islamic next to Christian Byzantium, with labels saying "official religion".
5. **Influence.** Ranking by area per year, leaderboard card, dimming of the rest, with the metric shown on screen. Add Seshat population ranking as a switchable metric if the data allows.
6. **Focus and filters.** Region presets and box draw, entity search and lifespan view, confidence filter, and the about panel.
7. **Polish.** Mobile layout, performance budget met, Playwright tests, accessibility (keyboard slider, readable contrast, colour-blind-safe palette), and deployment to GitHub Pages.

For the coding agent: keep every data claim traceable. If a source can't be found for something, leave it out and list it in `build-report.md` under "gaps". Never invent borders, dates or citations.

## Caveats and how to show them

Solid borders and neat "peoples" are a simplification, and the app must show that rather than hide it. Every caveat below gets a visual treatment, not just a line in the about panel.

- **Borders before about 1800 are approximate.** Empires had frontier zones, tribute relationships and nominal claims. Use soft edges and confidence-based line styles, and say "claimed or controlled".
- **Peoples aren't polygons.** Cultures overlapped and mixed, and an archaeological culture (pottery style), a language family and a genetic ancestry are different things that don't map one-to-one. Label which one each feature is (`kind`) and never merge them into one "race" or "nation" layer.
- **Absence isn't emptiness.** Cliopatria leaves out polities without written sources, those under 5,000 km² and those lasting under 50 years. Blank areas on the map should read as "no data in this layer", e.g. with a light hatch, not as uninhabited land.
- **Prehistory dates change.** Out-of-Africa and arrival dates keep moving with new finds. Curated entries store a date range and the citation, and the UI shows the range.
- **Contested history.** Where sources disagree (borders, founding dates, who counts as a successor), keep both versions as separate features with their own sources and show a "contested" badge. Don't pick a winner silently.
- **Religion is a proxy.** Before 1945 the layer shows the ruler's or state's religion, not what people believed. Say so in the legend.
- **Influence is a metric choice.** Area flatters steppe and polar empires; population favours China and India. Always show which metric is in use, and offer at least two.
- **Eurocentrism in the data.** Wikidata and many datasets are denser for Europe. The build report should count features per region and era so gaps are visible and can be filled deliberately.
