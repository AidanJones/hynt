# Hynt — Human History Atlas

Hynt (Welsh: the course, the way taken) maps changing claimed or controlled territory, with sources attached to every shape.

The viewer includes Cliopatria polities, technology/knowledge evidence, and a Britain/Wales evidence layer. The original build spec remains the product brief; [SPEC_REVIEW.md](SPEC_REVIEW.md) records corrections and implementation decisions. Later milestones are tracked in Beads.

## Run locally

No viewer build, package install, CDN, API key or backend is required. From the repository root:

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory atlas
```

Open http://127.0.0.1:8000 in a browser with WebGL 2 and the standard gzip `DecompressionStream` API (current major browsers). Serve over HTTP; opening `index.html` as a file does not support modules and data fetching.

The viewer supports 10,000 BCE–2026 CE, annual stepping with no year zero, playback, polity visibility/opacity, sourced details, entity search, region presets and URL state. Polity coverage remains 3400 BCE–2024 CE and is not extrapolated.

Enable **Technologies & knowledge**, choose farming/herding, ironworking, algebra or printing, and open **Explore dated milestones** to jump between evidence records. Each marker lists the package's locally evidenced components and citations. Hollow markers show a dating window; dashed connections are schematic and individually sourced. Past markers represent recorded evidence, not continuous use or universal adoption. Example: `http://127.0.0.1:8000/#y=1145&l=polity,technology&t=algebra&c=20,35,2`. See [technology-report.md](technology-report.md) for coverage and [PRE_ROMAN_BRITAIN.md](PRE_ROMAN_BRITAIN.md) for the Wales/Britain investigation.

Enable **Britain & Wales evidence**, expand its explorer, and choose **Explore Wales · 700 BCE**. Browse archaeological sites, metalwork, communities and named rulers, or search for Caratacus, Tasciovanus or Llyn Fawr. **Recorded by this year** keeps earlier evidence; **Dating overlaps this year** uses the actual cited interval. Points are approximate evidence anchors, not kingdoms or tribal boundaries. Example: `http://127.0.0.1:8000/#y=51&l=britain&bk=ruler&bm=window&c=-3,52,5`.

## Rebuild data

Python 3.12+:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r pipeline/requirements.txt
./.venv/Scripts/python.exe -m pipeline.build
```

The first build fetches a pinned archive to ignored `pipeline/raw/`. Use `--offline` for subsequent rebuilds from cache. Its SHA-256 is checked before use. Run from the repository root. With Make, `make -f pipeline/Makefile data` is equivalent. Viewer files and era data are included, so rebuilding is optional for browsing. `python -m pipeline.fetch_assets` refreshes the pinned MapLibre and Natural Earth assets separately.

Outputs include packed era files, a manifest, citations, an entity index, [build-report.md](build-report.md) and [pipeline/quarantine.json](pipeline/quarantine.json). Invalid source dates are quarantined without guessing; other validation failures stop the build. Geography is simplified for overview use, not precise boundary analysis. Packaging then deduplicates exact geometry, delta-encodes coordinates with exact exceptions and gzips the result. Every chunk must reproduce all validated coordinates and properties exactly. The viewer reconstructs standard GeoJSON before passing it to MapLibre. See [performance-report.md](performance-report.md).

Technology data is edited in `pipeline/curated/technologies.json`. Rebuild just that small layer with `python -m pipeline.technologies`; its schema checks require valid dates, source references, coordinates and chronological connection endpoints. The full pipeline includes this step.

British evidence is edited in `pipeline/curated/britain.json`; rebuild with `python -m pipeline.britain`. The full pipeline includes both curated layers. `python -m pipeline.package` converts a legacy manifest/GeoJSON export to the packed format; it is also part of the full build. To inspect a packed chunk in Python, use `pipeline.package.read_collection(path)`.

## Checks

```powershell
node --test tests/timeline.test.js tests/technology.test.js tests/britain.test.js tests/codec.test.js
./.venv/Scripts/python.exe -m pytest tests -q
./.venv/Scripts/python.exe -m playwright install chromium
# Start the HTTP server above in another terminal, then:
./.venv/Scripts/python.exe tests/browser_smoke.py http://127.0.0.1:8000
# Run separately from other browser tests:
./.venv/Scripts/python.exe tests/browser_performance.py http://127.0.0.1:8000
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
