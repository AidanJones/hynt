# Events, religion, territorial extent and focus — 15 November 2026

## Events and independently dated campaigns

Five selected events, two dated campaigns and two cited political relations are available. In 1066, Fulford, Stamford Bridge, Pevensey and Hastings can be explored on an intra-year day slider with playback. The Yorkshire route uses the 18 September Riccall anchorage, 20 September Fulford battle and 25 September Stamford Bridge battle; William’s route uses 28 September Pevensey, 1 October Hastings camp and 14 October battle. English Heritage/Historic England sources date each anchor. Interpolation is illustrative, not a surveyed itinerary or measured speed.

The 476 relation concerns Romulus Augustulus’s deposition and Odoacer’s rule in Italy, not instant succession to all western provinces. Relations have independent citations, never inferred solely from adjacent polygons or Wikidata sequence properties. Records and caveats are in `pipeline/curated/events.json`. This implements the acceptance scenarios, not a 200-event global catalogue. Wider event/campaign coverage and verified Wikidata imports remain data gaps.

## Religion evidence and synchronized comparison

The fill has explicitly selectable meanings: **official affiliation of ruler/state**, or **population-majority observation**. No year-based switch changes its meaning. The 750 CE tour compares Umayyad Islam and Byzantine Christianity with polity context. The right half shows religion proxies and the left shows claims/control. Camera movements synchronize in both directions and both maps share one timeline. Mode, comparison and layers survive reload.

Three sourced observations are included: Umayyad and Byzantine state affiliation, and India’s 2011 census Hindu majority (79.8%). The latter appears only in its observation year, never as state religion. It is a national aggregate, not a local majority everywhere; enumeration coverage can differ from claimed-border geometry. Sources and caveats are in `pipeline/curated/religion.json`. No ARDA, DRH or Pew bulk data was redistributed without a version-specific reuse decision. Other population-religion coverage remains absent.

## Territorial extent and history

`python -m pipeline.ranking` produces 506 ranking intervals at geometry change points, a top ten and per-entity histories for 1,412 entities. Concurrent polygons are unioned **within each entity** before EPSG:6933 area measurement. Different overlapping entities rank independently; extents are not additive. Values are rounded to whole km² and derive from simplified claimed/controlled geometry. This measures neither population nor overall influence; no unsupported second metric is offered.

Clicking a ranked entity focuses its shapes and opens source details. Its chart shows recorded extent intervals, leaves gaps unjoined and marks the selected year. Identities follow the source except documented crosswalk corrections. Rankings remain global when geographic filters are active. Ranking/history data loads only when needed.

## Geographic filters and polish

The polity filter accepts four editable bounds or a mouse-drawn box; Escape cancels drawing. Intersection respects polygon holes; matching shapes remain whole rather than being clipped. A single window cannot cross the antimeridian. Window and confidence choices survive reload. The source supplies no feature confidence ratings, so the UI offers “all” and “not assessed” without inventing high/medium/low values.

Mobile controls can be hidden to expose the map. Text and touch targets were enlarged. Inferred technology chunks use diagonal hatching as well as colour. `review.html` makes audit flags searchable. The Pages workflow runs unit/browser checks before publishing; official Actions are pinned to immutable commits.

The offline rebuild validated 13,412 shapes and all 17 lossless era files and regenerated every derived layer. The Han identity correction leaves 140 alias sets and yields 1,412 entities; no geometry was redrawn. Latest test results are in `verification.md`.

Original summaries and illustrative anchors are CC0. Polity-derived fills, assignments and extent statistics attribute Cliopatria CC BY 4.0. Linked publications retain their rights. Culture import, comprehensive expert border adjudication and physical-phone certification remain separate tracked work; see `source-review-report.md` and `performance-report.md` for limits.
