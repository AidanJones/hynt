# Deep time and migrations

The timeline now reaches 300,000 BP, with BP explicitly referenced to 1950 CE. `ya` input instead means years before the atlas's fixed 2026 CE endpoint. BCE/CE has no year zero. Slider steps are 1,000 years down to 12,000 BP, 50 years until 3400 BCE, then annual. Precise entered dates and URLs remain supported between the coarse stops. Prehistoric playback advances through these coarse stops, rather than waiting thousands of seconds at annual speed.

Five curated stories are included: a later out-of-Africa model, the Madjedbebe occupation phase in Sahul, Bacho Kiro evidence in Europe, White Sands footprints in North America, and a broad early-farmer sequence linking the Mediterranean and Britain. Two stories are schematic route models; three are separately dated site attestations. Each has sources and an explicit interpretation caveat. Past evidence is retained when scrubbing forward; it is not a claim of continuous population identity or occupation.

Route drawing progresses across the stated broad interval. Intermediate positions and constant animation speed are illustrations, not measured migration speed or independently dated waypoints. Sites are never joined into an invented itinerary. The Sahul and White Sands records retain discussion of dating uncertainty. Calibrated radiocarbon BP is distinguished from OSL/rounded age estimates; for the latter the 1950 plotting conversion is explicitly approximate. Modern shorelines are labelled as orientation only.

## Data and licences

`pipeline/curated/migrations.json` is an original factual compilation with illustrative geometry, dedicated as CC0. Linked studies keep their own rights. No published route maps, images, ancient-DNA sample tables or bulk third-party records are redistributed. Run `python -m pipeline.migrations`; the full build also includes this step.

[historical-basemaps](https://github.com/aourednik/historical-basemaps) was checked: its repository identifies GPL-3.0 and warns that cultural regions and historical boundaries need verification. No prehistoric culture polygons have been imported in this increment. A version-specific source/citation and reuse review remains tracked separately, as do broader Holocene migrations and palaeocoastlines. This increment delivers the chronology and curated route/site part of milestone 2, not every dataset in the original milestone.

## Verification

Python validation checks unique IDs, source references, coordinate bounds, chronological intervals and age-to-civil conversions. Node tests cover piecewise joins, exact year round trips, no year zero, BP/ya input, URL state, progressive line interpolation and temporal clamping. A dedicated Playwright run passed: 100,000 BP tour, keyboard step to 99,000 BP, progressive route at 55,000 BP, Sahul/Europe/Americas evidence timing, sourced detail panels, reloadable story state, expanded paper/writing data, and a 390-pixel mobile layout. Desktop/mobile screenshots were inspected.
