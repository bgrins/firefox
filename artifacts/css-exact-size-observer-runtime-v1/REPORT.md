# Rectangle observer isolation

Outcome: a minimal non-flex rectangle discrepancy reproduces in installed Firefox and the restored project build. No repair is installed or accepted.

Both browsers completed56 identical records: eight minimal absolute-positioned ordinary boxes and48 supplemental family/size records. Every ResizeObserver record arrived; no scalar timeout/missing result occurred. Source, scripts and binaries were stable across each run, and temporary profiles were removed. getBoxQuads is unavailable under these browsers' default settings; no corner-API evidence is claimed.

A100px fixed host contains a box aligned at right:0 and bottom:0. At120.125px size, all four axis/padding controls report bounding end100 and marker end100. At139808.125px, all four report bounding end100.015625 but marker end100. ResizeObserver gives border dimension139808.140625, while the bounding dimension is larger. Padded and unpadded boxes agree; authored/computed transform is none. Thus the discrepancy needs neither flex overrides, table captions nor replaced elements.

The independent source-shaped calculation in css-exact-size-observer-boundary-review-v1 reproduces these values with a mathematically exact native edge: integer→float rectangle→rounded app-unit rectangle→DOMRect conversion can enlarge one dimension. This demonstrates a plausible actual source route, not an executed trace of all native operands. ResizeObserver itself uses floating values; it is a second public observer, not an assertion that every native integer was instrumented.

A separate source diagnosis corrects the earlier table observer: bounding collection includes the caption. Original supplemental assertions and32 remaining failures are unchanged. Neither those table diagnostics nor equality with an explicit image reference are treated as proof of native layout-size error.

Next: bind the full ancestor/transform/viewport/SVG/zoom path for the minimal case; prepare an independently reviewable correction and WPT only after that admission. Preserve fallback behavior for all excluded paths and the full exact safe-origin observer contract. No new accepted fix, native source/build change, index mutation or push occurred in this probe.
