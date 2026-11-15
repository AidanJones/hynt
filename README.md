# Hynt — Human History Atlas

[Open the live atlas](https://aidanjones.github.io/hynt/).

Hynt (Welsh: the course, the way taken) maps changing claimed or controlled territory, with sources attached to every shape.

The viewer includes Cliopatria polities, regional technology evidence, Britain/Wales evidence, migration/site stories, dated events/campaigns, separately typed religion proxies, synchronized comparison, territorial rankings and geographic/entity filters. The original build spec remains the product brief; [SPEC_REVIEW.md](SPEC_REVIEW.md) records corrections and implementation decisions. Remaining source-review/device work is tracked in Beads.

## Run locally

No viewer build, package install, CDN, API key or backend is required. From the repository root:

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory atlas
```

Open http://127.0.0.1:8000 in a browser with WebGL 2 and the standard gzip `DecompressionStream` API (current major browsers). Serve over HTTP; opening `index.html` as a file does not support modules and data fetching.

The viewer supports 300,000 BP–2026 CE with a piecewise slider: 1,000-year prehistoric steps to 12,000 BP, then 50-year steps to 3400 BCE, then annual steps. There is no civil year zero. `BP` means before 1950 CE; `ya` means before the atlas's fixed 2026 endpoint. Precise BCE/CE and BP input, playback, sourced details, search, regions and shareable state are supported. Polity coverage remains 3400 BCE–2024 CE and is not extrapolated.

Enable **Technologies & knowledge**, choose farming/herding, ironworking, algebra, printing, writing or paper, and open **Explore dated milestones** to jump between evidence records. Each marker lists the package's locally evidenced components and citations. Hollow markers show a dating window; dashed connections are schematic and individually sourced. Past markers represent recorded evidence, not continuous use or universal adoption. Example: `http://127.0.0.1:8000/#y=1145&l=polity,technology&t=algebra&c=20,35,2`. See [technology-report.md](technology-report.md) for coverage and [PRE_ROMAN_BRITAIN.md](PRE_ROMAN_BRITAIN.md) for the Wales/Britain investigation.

Enable **Britain & Wales evidence**, expand its explorer, and choose **Explore Wales · 700 BCE**. Browse archaeological sites, metalwork, communities and named rulers, or search for Caratacus, Tasciovanus or Llyn Fawr. **Recorded by this year** keeps earlier evidence; **Dating overlaps this year** uses the actual cited interval. Points are approximate evidence anchors, not kingdoms or tribal boundaries. Example: `http://127.0.0.1:8000/#y=51&l=britain&bk=ruler&bm=window&c=-3,52,5`.

## Rebuild data

Enable **Migrations & early presence** and use **Begin at 100,000 BP** to explore two schematic dispersal models and three dated-presence stories. Source caveats distinguish routes, site evidence, calibrated dates and approximate age estimates. See [migrations-report.md](migrations-report.md). [audit-report.md](audit-report.md) documents regional coverage, identity/overlap flags and date decisions.

Python 3.12+:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r pipeline/requirements.txt
./.venv/Scripts/python.exe -m pipeline.build
```

The first build fetches a pinned archive to ignored `pipeline/raw/`. Use `--offline` for subsequent rebuilds from cache. Its SHA-256 is checked before use. Run from the repository root. With Make, `make -f pipeline/Makefile data` is equivalent. Viewer files and era data are included, so rebuilding is optional for browsing. `python -m pipeline.fetch_assets` refreshes the pinned MapLibre and Natural Earth assets separately.

Outputs include packed era files, a manifest, citations, an entity index, [build-report.md](build-report.md) and [pipeline/quarantine.json](pipeline/quarantine.json). Invalid source dates are quarantined without guessing; other validation failures stop the build. Geography is simplified for overview use, not precise boundary analysis. Packaging then deduplicates exact geometry, delta-encodes coordinates with exact exceptions and gzips the result. Every chunk must reproduce all validated coordinates and properties exactly. The viewer reconstructs standard GeoJSON before passing it to MapLibre. See [performance-report.md](performance-report.md).

Technology data is edited in `pipeline/curated/technologies.json`, `technology-expansion.json` and `technology-regional.json`. Rebuild with `python -m pipeline.technologies`; validation requires dates, citations, coordinates, BP epoch consistency and chronological connections. There are seven packages and 32 attestations, including writing, paper and mathematics. Then run `python -m pipeline.technology_regions` to refresh the 955 land chunks and optional dated-polity coverage assumptions. The full pipeline includes both steps. See [technology-regions-report.md](technology-regions-report.md) for the inference rules and research limits.

British evidence is edited in `pipeline/curated/britain.json`; rebuild with `python -m pipeline.britain`. The full pipeline includes both curated layers. `python -m pipeline.package` converts a legacy manifest/GeoJSON export to the packed format; it is also part of the full build. To inspect a packed chunk in Python, use `pipeline.package.read_collection(path)`.

## Checks

Enable **Events & campaigns** for the 1066 dated tour and the cited 476 transition. Enable **Religion evidence & proxies** for the synchronized 750 CE comparison or the distinct India 2011 census observation. **Territorial extent ranking** opens the global leaderboard; selecting an entity shows its recorded history. **Geographic & evidence filters** supports drawing or entering a box. See [milestones-report.md](milestones-report.md) for coverage and methods, and [source-review-report.md](source-review-report.md) for the searchable review queue and remaining source work.

Individual rebuilds: `python -m pipeline.events`, `python -m pipeline.religion`, `python -m pipeline.ranking`. The full build includes these. `python -m pipeline.culture_review` inspects candidate prehistoric snapshots separately; their polygons are not distributed.

Reviewed exact identity decisions live in `pipeline/curated/entity-crosswalk.json`. `python -m pipeline.reconcile` refreshes those decisions in existing packed geometry, then regenerates entity indices, audits, rankings and regional assumptions. Original QIDs remain attached to corrected records. Removing a decision restores the source grouping on refresh.

`python -m pipeline.migrations` validates and packages migration/site stories. `python -m pipeline.audit` regenerates the coverage/overlap report and viewer interpretation notes from current packed data. Both are part of the full rebuild. Six source records with inclusive zero endpoints are now represented without changing membership over valid civil years; original values and the explicit conversion rule are in `pipeline/date-decisions.json`.

```powershell
node --test tests/*.test.js
./.venv/Scripts/python.exe -m pytest tests -q
./.venv/Scripts/python.exe -m playwright install chromium
# Start the HTTP server above in another terminal, then:
./.venv/Scripts/python.exe tests/browser_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/deep_time_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/audit_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/cross_era_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/technology_regions_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/events_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/religion_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/focus_ranking_smoke.py http://127.0.0.1:8000
./.venv/Scripts/python.exe tests/review_polish_smoke.py http://127.0.0.1:8000
# Run separately from other browser tests:
./.venv/Scripts/python.exe tests/browser_performance.py http://127.0.0.1:8000
# Windows Direct3D test; inspect the reported renderer, not just this flag:
./.venv/Scripts/python.exe tests/browser_performance.py http://127.0.0.1:8000 desktop --hardware
```

The browser script exercises five dates, rendered polygons, citations, actual map clicks, BCE/CE stepping, layer/hash persistence, playback, mobile layout and a failed-download retry. Screenshots and measurements go to ignored `test-results/`. [verification.md](verification.md) records the latest run and its limits.

## Task tracking

```powershell
bd ready
bd list
bd show hynt-deep
```

Beads tracks the initial milestones and follow-up work, including technologies and pre-Roman Britain/Wales. `.beads/issues.jsonl` is an interchange snapshot; the local Dolt database holds live state. Refresh it with `bd export -o .beads/issues.jsonl`. In a fresh clone, initialize Beads and import the snapshot; JSONL is not a full database history backup.

## Evidence and licences

Application code is MIT. Cliopatria data is **CC BY 4.0**, attributed to its contributors and the Seshat Global History Databank. Natural Earth land is public domain; MapLibre is BSD-3-Clause. See [pipeline/LICENCES.md](pipeline/LICENCES.md) and the viewer's About dialog for attribution and transformations.

Blank land means missing data. Confidence is shown as not assessed, because the source does not provide individual ratings. A polity shape does not represent a homogeneous people or religion. Present-day coastlines provide context. GitHub Pages deployment remains a tracked later milestone.
