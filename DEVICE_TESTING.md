# Physical device checks

Open [the device check](https://aidanjones.github.io/hynt/device-check.html) directly in Safari or Chrome on the phone/tablet. Enter the device model/browser and connection, confirm direct physical-device use, then run the check with the tab visible. Copy the JSON report back to the atlas chat or download it. No report is uploaded automatically.

The page loads the real atlas at the full viewport, measures 120 timeline updates in 117 and 1920, and checks loading at 1550, 1700 and 1920. It records renderer, viewport, pixel ratio, browser user agent, observed frame distributions, input work and first rendered geometry. Browser/HTTP caches can warm after the first case, so these are not cold-network measurements. A hidden tab invalidates the run. The model/browser and connection are self-reported, not independently established by the page.

Validate a saved report with `python -m pipeline.device_reports path/to/report.json`. Successful validation checks the report structure and actual-geometry assertions. It does not independently certify that hardware was a physical phone. A desktop browser with a small viewport remains desktop/unverified unless the person running the test states otherwise; even that declaration stays explicitly self-reported.

The automated harness check proves the test flow works on desktop Chromium. Actual Android/iOS results are still needed before closing the physical-device Beads task.
