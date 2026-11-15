# Payload and scrub performance — 15 November 2026

## Hardware profiling and update reduction

The software-only result below was not representative of the available GPU. Chromium was explicitly run with its Direct3D11 backend and the renderer was verified as **Intel UHD Graphics (0x00009B41)** on Windows 11 build 26200, driver 31.0.101.2137, Chromium 159.0.8154.6. All benchmark cases assert that actual polity polygons render.

| Case | Viewport | Mean FPS | 95th percentile frame | Input work / update |
| --- | --- | ---: | ---: | ---: |
| 117 CE, before | 1440×1000 | 60.31 | 18.30 ms | 1.58 ms |
| 117 CE, after | 1440×1000 | 59.99 | 18.90 ms | 1.56 ms |
| 1920 CE, after | 1440×1000 | 59.99 | 18.40 ms | 1.90 ms |
| 117 CE, phone-size viewport | 390×844 | 59.96 | 19.00 ms | 1.35 ms |

These are short 120-update, within-era observations. The hardware renderer already sustained approximately 60 FPS before optimization; the change reduces redundant work rather than claiming that code alone turned 9 FPS into 60. The original 117 CE test made 360 filter, 360 visibility and 120 paint-property calls; the optimized equivalent makes 24 filter calls and no redundant visibility/opacity calls. Its active features are unchanged, proven across date boundaries in tests.

Compressed era buffers now decode in a dedicated module worker, keeping decompression/JSON parsing off the main UI thread. HTTP download sizes remain observable in the main page. Worker errors reject the correct request, retry is supported, and a failed worker falls back to the compatible main-thread decoder. Rapid-scrub tests confirm that delayed old-era responses cannot replace a newer selection. A corrupt gzip body delivered with HTTP 200 was also recovered through Retry. A stale failed request cannot delete a newer cache entry for the same era.

Initial resource bodies in the measured default view were **1,508,817 bytes**; the 1920 view was **3,451,659 bytes** (plus document/headers). Packed source geometry was not simplified further. Six restored BCE boundary records bring the polity total to 13,412 and packed era files to 10,912,031 bytes. The whole atlas remains below 15 MB.

**Limits:** this verifies approximately 60 FPS on the named desktop GPU for the measured cases. The small viewport uses the same desktop GPU and is not a physical-phone certification. Network-limited and more extensive cross-era performance, iOS/Android devices and other GPUs still need measurement. Raw results are retained in `benchmarks/performance-2026-11-15.json`. The following sections retain the earlier packaging and software-renderer baseline; their counts and limitations are superseded here where they differ.

## Shipped bytes

- The 17 era files went from **68,297,906 bytes to 10,911,192 bytes** (84% smaller).
- Largest era file: **2,454,178 bytes**, previously over 13 MB uncompressed.
- Initial 117 CE resource bodies observed by the browser: **1,475,921 bytes**, plus the small HTML document and HTTP headers. The initial payload and every era plus the same fixed assets fit under the 5 MB byte budget.
- All distributed `atlas/data` files total **11,167,339 bytes**; the entire static `atlas` directory totals **12,242,350 bytes** at measurement. Both fit under 15 MB, and the test suite checks the actual current directory sizes.

These are actual shipped `.json.gz` files, not an estimate that assumes the static host enables HTTP compression. The browser handles both a raw gzip file and a response already decompressed by the host. It uses the standard browser `DecompressionStream` API; no compression dependency or viewer build was added.

## What packing changes

`pipeline/package.py` deduplicates identical geometry inside each era, records coordinate deltas as integers on the existing four-decimal grid, and retains sparse exact-coordinate exceptions for all vertices that need more precision. Those exceptions include vertices introduced by geometry repair. The files are gzipped with a fixed timestamp, and the manifest records their byte sizes and SHA-256 hashes. Requests use hash-based cache keys.

Every chunk is unpacked and compared with the validated input before being accepted: all properties, IDs, geometry types, rings and coordinates must match exactly. This stage does **not** simplify borders further or claim shared-border topology preservation. Python and browser decoding tests cover precision exceptions, polygon/multipolygon geometry, gzip responses, already decoded responses, malformed downloads and unsupported formats. A deterministic rebuild test repacks the actual Roman-era chunk and checks identical bytes.

MapLibre continues to receive ordinary GeoJSON and to filter it by year. The era request cache remains bounded to four entries. Marker DOM for British and technology evidence is now reused when the visible record set and uncertainty status do not change, rather than rebuilt on every annual tick.

## Frame timing

An isolated run of `tests/browser_performance.py` observed approximately **9.65 FPS**, with a mean frame interval of **103.67 ms** and a 95th percentile of **112.20 ms**, over 119 measured intervals. Environment: Windows 11 build 26200, Chromium 159.0.8154.6, 1440×1000, headless SwiftShader software WebGL. It scrubbed within a loaded era and confirmed stable technology marker DOM.

**The 60 FPS requirement is not met by this software-renderer measurement and is not certified on physical devices.** Bead `hynt-frame-rate` tracks desktop/mobile profiling, physical-GPU measurements and cross-era loading. An earlier concurrent browser run was discarded because running the smoke suite and this software-rendering benchmark together caused contention. Run these scripts separately.

The full smoke suite subsequently passed on its own, including all five polity dates, British evidence, technologies, citations, mobile layout and failed-download recovery. Its local first-view observation was 2.67 seconds including the test's network-idle wait; that is not a broadband benchmark.
