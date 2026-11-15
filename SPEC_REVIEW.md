# Build specification review

The architecture is a good fit: static ES modules, range-based geometry and a separately reproducible pipeline. Preserve the original specification as the product brief. These decisions amend its implementation contract.

## Corrections needed before importing data

1. **Inclusive source dates.** Cliopatria uses inclusive `FromYear` and `ToYear`. Convert its end to the next civil year before applying `[from, to)`. A one-year record must survive. There is no civil year zero: the successor of −1 is 1. Use a contiguous internal ordinal for slider steps and playback, while storing civil years in data and URLs.
2. **Coverage is not the current year.** The pinned backbone ends in 2024. Allow navigation to 2026, show a coverage warning, and do not carry 2024 borders forward without evidence.
3. **Confidence must have evidence.** Add `unknown` for sources without an explicit rating; display “not assessed”. Do not derive certainty from polygon precision. Uncertainty of dates, boundaries and attribution should eventually be separate fields.
4. **Identity is not a label.** Use QIDs where present and a stable source-name key otherwise. Preserve source record IDs and fields. Flag reconciliation needs; do not silently merge fuzzy matches.
5. **Campaign is missing from the common layer enum.** Add `campaign`, with timed waypoints and source references, in milestone 3. Keep event occurrence, uncertain dating and geometry validity as separate concepts.
6. **Deep time needs an epoch.** Scientific BP convention is 1950, unlike “years before 2026”. Label the chosen epoch explicitly and store original date ranges. Human origins around 300,000 years ago and dispersal out of Africa are different events. Define continuous piecewise intervals; the proposed 12,000-ya/10,000-BCE join currently leaves a gap.

## Evidence and product improvements

- Keep official/state religion and adherent-majority estimates as distinct selectable evidence types. A universal 1945 switch would imply precision and coverage the sources do not supply. Do not infer conversion, conquest or causal succession from Wikidata sequence edges alone.
- Name the first ranking **territorial extent**, not general influence. Compute at geometry change points instead of storing every annual repeat. Disclose overlap accounting and missing entities. Defer population until coverage supports meaningful comparisons; the spec's v1/v2 requirements currently conflict.
- Snapshot intervals are a model assumption, not observed constant borders. Preserve the observation date and say when a snapshot is carried forward. Avoid a silent “Cliopatria wins” rule for documented disagreements.
- Pin source revisions and hashes; retain download provenance, licences, attribution and transformation notes. Code's MIT licence does not relicense data. Unreviewed datasets stay out of distributed assets.
- Blank space means missing coverage. Place this statement on the map, distinguish unsupported years from failed downloads, and expose overlapping candidates on click.
- Add explicit unavailable-layer states, retryable loading errors, reduced-motion support, keyboard controls, mobile panels, safe link rendering, hash validation and out-of-order request protection from milestone 1.
- Use a manifest of era chunks, cache requests and prefetch adjacent chunks. Measure transfer size and frame time on a named device before claiming the performance budget. Geometry simplification must report units and distinguish per-feature validity from shared-border topology preservation.
- Add temporal boundary tests, deterministic rebuild checks and real-source checks for 117, 1280 and 1920. Browser smoke tests must assert visible polygons and citations, not merely that the document loads.

## First implementation boundary

Deliver milestone 1 as a working local static atlas: real Cliopatria polygons, annual 3400 BCE–2026 CE navigation, playback, sourced details, entity search, region presets and shareable state. Add the other datasets in the existing milestone order after their licences and evidence contracts are checked. GitHub Pages remains the requested eventual host; this first increment does not publish the repository.

## Verified primary references

- [Cliopatria README](https://github.com/Seshat-Global-History-Databank/cliopatria): inclusive year ranges and documented fields.
- [Pinned licence](https://github.com/Seshat-Global-History-Databank/cliopatria/blob/5f433377139a6eeaeacbdc894b70f8805b72c8b5/LICENSE.md): CC BY 4.0.
- [MapLibre API](https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/): filters, camera and rendered-feature queries.
