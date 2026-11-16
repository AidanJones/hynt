# First-increment verification

## Selected cultures and identity review — 16 November 2026

**75 Python and 31 Node tests passed.** The culture and review-page browser checks pass on desktop and phone-size layouts, with screenshots inspected. They exercise rendered culture polygons, references and licence links, half-open date windows, share state, corrected identity details, review filters, keyboard stepping and mobile controls. The physical-device harness also passed its desktop regression and deployed CI; that is not a physical-phone result.

The identity refresh preserves all 13,412 polity geometries and source/viewer intervals byte-for-byte after canonical serialization against commit `5440b55`; the checked digest is in `pipeline/reviews/geometry-preservation.json`. Thirty-four further exact identity corrections affect 315 source records. Reference checks and temporal geometry classes are reproducible diagnostics, not exhaustive scholarly border adjudication. See [the review report](review-pass-2026-11-16.md) and [culture provenance](culture-report.md). Physical-phone evidence remains pending.

Existing polity/Britain/technology, deep-time, audit, cross-era race/corrupt-download recovery, regional technology, campaign/event, religion-comparison and ranking/filter browser suites also passed sequentially after the changes. The static viewer is 14.01 MB, within its 15 MB budget; optional culture data remains lazy-loaded.

## Expanded atlas milestones and source review — 15 November 2026

**62 Python and 29 Node tests passed.** New browser suites passed regional technology coverage, independently dated 1066 campaigns/events, the 476 Italy relation, synchronized religion comparison, the observation-year-only 2011 majority record, territorial rankings, lifespan charts, geographic/confidence filters, source-review search, corrected identities, keyboard stepping and mobile control visibility. Desktop/mobile screenshots were inspected. Existing polity/Britain/technology, deep-time, audit and cross-era retry suites also passed after these additions.

The complete offline source rebuild passed for all 13,412 shapes, all 17 lossless era packages and every derived layer. The subsequent geometry-preserving identity refresh yields 1,415 entities, 137 alias sets and 1,545 same-entity interval-overlap pairs. Four exact source name/QID/article combinations have cited corrections with original IDs retained. Linux CI exposed and then passed the gzip-header portability fix; the verified build was deployed to GitHub Pages. The candidate prehistoric import remains withheld pending its documented source/licence review. Physical iOS/Android testing and broader historical border adjudication remain open; these are not certified by browser tests.

The expanded default map measured 59.96 FPS on verified Intel UHD/D3D11. On-demand optional data reduced the initial resource bodies to 1,571,192 bytes. First rendered polity geometry measured 2.868 s at configured 10 Mbps/40 ms latency; the slower 1.6 Mbps/150 ms phone-size viewport took 10.543 s. These are desktop laboratory results, not physical-phone or field-network certification. Details and reproducible results are in [performance-report.md](performance-report.md), [milestones-report.md](milestones-report.md) and [source-review-report.md](source-review-report.md).

## Regional technology coverage — 15 November 2026

48 Python and 23 Node tests passed; the regional Playwright desktop/mobile suite passed and screenshots were inspected. The feature adds 955 stable land chunks, nine cited records and an optional dated-polity inference model. Unknown regions remain explicit. See [technology-regions-report.md](technology-regions-report.md) for methods, sources and limits.

## Technology, deep time, audit and performance — 15 November 2026

**45 Python and 20 Node tests passed.** The sequential Playwright polity/Britain/technology, deep-time and audit suites passed, with desktop/mobile layouts inspected. A separate hardware-browser check passed delayed cross-era responses and recovery from a corrupt gzip download. These results supersede older counts and open-work statements below.

Technology coverage now contains six packages and 23 attestations, including writing, paper, ironworking and algebra. The timeline reaches 300,000 BP, explicitly using the 1950 epoch. Five migration stories distinguish two illustrative routes from three site attestations; they do not invent dated paths between sites. Prehistoric cultural-region polygons remain a separate Beads follow-up.

The source audit covers 13,412 shapes and 1,411 entities, with alias, temporal-overlap and sampled spatial-overlap reports. Six BCE records formerly quarantined for an end year of zero were restored through a conversion proven equivalent for every valid civil-year query; their original dates and explanations are retained. Historical interpretation notes are visible in the atlas. Flags require scholarly review and are not automatic border corrections. See [audit-report.md](audit-report.md).

Hardware profiling verified Intel UHD Graphics through Direct3D11 and approximately 60 FPS in the measured 117 CE, 1920 CE and phone-size viewport cases. Era decoding now runs in a worker; redundant map-property updates are skipped. The 117 CE benchmark reduced filter calls from 360 to 24 over 120 updates. Hardware already reached approximately 60 FPS before these changes, so this is not a claim of a code-only improvement from the older software-renderer result. The static atlas remains below 15 MB. Physical iOS/Android devices, other GPUs and constrained networks still need measurement. See [performance-report.md](performance-report.md) and the retained benchmark JSON.

The complete offline source rebuild and lossless packaging succeeded. Verification was performed locally; the atlas has not been published.

## Britain/Wales and lossless packaging — 15 November 2026

**35 Python and 11 Node tests passed.** The new checks cover British record dates, evidence filters, old/new URL state, provenance validation, valid related-record references, lossless coordinate exceptions, geometry deduplication, deterministic chunk repacking, browser gzip decoding and actual byte budgets.

A full offline rebuild from the pinned cached archive also completed: 13,406 validated polity shapes, both curated layers, all 17 exact-round-trip packed chunks and the generated build report. Packed sizes remained identical to the migration run.

The extended Playwright suite passed on its own with no uncaught page errors: Caratacus is searchable and opens the Coflein citation and disputed-location explanation; Wales in 700 BCE has archaeological evidence without a future Caratacus marker; type/date filters survive reload; the episode-only ruler marker disappears in 52 CE; Llyn Fawr details work at mobile size. Desktop/mobile screenshots were inspected. All earlier polity and technology checks, plus failed-download retry, still pass with the packed files. Local first view was observed at 2.67 seconds including network-idle waiting.

The whole static atlas is about 12.24 MB; packed era files are 10.91 MB. Details and limits are in [performance-report.md](performance-report.md). The isolated Windows Chromium software-renderer benchmark measured about 9.65 FPS, so the 60 FPS target remains outstanding in `hynt-frame-rate`. An initial simultaneous benchmark/smoke run timed out under contention and was replaced by separate successful verification runs.

Historical source and interpretation details are in [PRE_ROMAN_BRITAIN.md](PRE_ROMAN_BRITAIN.md). These records add point evidence, not reconstructed state borders. The older measurements below are retained as a record of earlier increments and are superseded by this section where they differ.

## Technology-layer follow-up — 15 November 2026

**23 Python and 6 Node tests passed** after adding the technology layer. Validation rejects missing sources, invalid chronology, year zero, out-of-bounds coordinates and duplicate evidence IDs. Temporal tests cover cumulative records, uncertainty windows, transmission dates, deep-time and legacy URL state.

The extended Playwright suite passed the original polity checks and technology checks: algebra has one hollow marker in 825 and two markers plus a cited connection in 1145; a dated trail button opens the translation citation; package/layer state survives reload; the window-only view shows no algebra markers in 2026; farming has one marker and zero polity polygons in 9000 BCE. Fit-to-evidence and desktop/mobile layouts were exercised. Updated screenshots were visually inspected. No uncaught page errors occurred. The latest local first-view observation was 2.14 seconds, not a network/device performance certification. Screenshots: `test-results/technology-desktop.png` and `test-results/technology-mobile.png`.

Coverage and interpretation limits are in [technology-report.md](technology-report.md). The following section preserves the original polity-increment measurements.

## Original polity increment

Verified locally on 15 November 2026, using Python 3.12.10, Node 24.22.1, Shapely 2.2.0 and Playwright Chromium 159 on Windows. Software WebGL rendering was enabled for the headless browser.

- **16 Python tests passed:** inclusive date conversion, BCE/CE successor, invalid dates, required citations, continuous era coverage, real source examples for Rome (117), Mongol (1280) and British (1920), and no extrapolation into 2026.
- **3 Node tests passed:** every annual slider value round-trips, no civil year zero, year parsing and URL state validation/round-trip.
- **Browser smoke passed:** visible map fragments at 3400 BCE (1), 117 (37), 1280 (142) and 1920 (117); zero polity fragments in unsupported 2026. These counts are rendered tile fragments, not polity totals.
- Browser checks also passed for search, source/Wikipedia links, an actual Roman polygon click, BCE/CE buttons, layer visibility persisted through reload, playback, About dialog, a 390×844 mobile viewport without horizontal overflow, and a simulated HTTP 503 followed by retry. No uncaught page errors occurred.
- Desktop (1440×1000) and mobile screenshots were visually inspected. Artifacts are in ignored `test-results/` and are regenerated by `tests/browser_smoke.py`.
- First view in the local browser test took **2.95 s**, including the test's network-idle wait. This is a loopback/software-renderer observation, not a broadband/device benchmark or a 3-second performance certification.
- All 13,406 exported shapes passed provenance, civil-year interval, finite-coordinate, coordinate-bound and polygon validity checks during the build. Six source records with year-zero endpoints were quarantined. 385 upstream RELATION records were excluded from the polity layer.

## Known limits and next work

The 17 era files total **68.30 MB uncompressed** (about 19.56 MB if gzip-compressed). This exceeds the spec's 15 MB total target. At the default 117 view, required local assets total **4,696,624 bytes** before HTTP compression; adjacent eras prefetch only near a boundary. Other eras can exceed the initial download budget. Shared geometry packaging, smaller chunks and compression need measurement before final release. The 60-fps scrub target, global shared-border topology, region-by-era coverage, detailed spatial-overlap reports, expert historical accuracy and cross-browser/device accessibility have not been certified.

This increment is served locally and has not been published. Deep time, migrations, events/campaigns, religion, rankings and advanced filters remain open in Beads. Exact source presence is not proof that every historical boundary is correct. The spec's milestone-1 expert “look right” acceptance is therefore still pending.
