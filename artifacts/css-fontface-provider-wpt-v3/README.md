# FontFace provider WPT v3

Minimal lint repair against the exact v2 tests; no test logic, test names, descriptors, resource paths, assertions or expected values change. Existing sealed packages and live tests are untouched. Root retains the exact v2 browser pair before installing this proposal.

- Canvas `.any.js` adds two `// META: spec=` lines using the same Font Loading 3 / FontFace and Fonts 5 / size-adjust URLs already in the DOM test. `META: help` would be invalid: current `check_script_metadata` accepts `spec`, and `SourceFile.spec_links` collects that key. Metadata stays contiguous before the first blank line.
- Both helpers split the identical source-selection ternary across three lines. Tokens, strings and branch order are unchanged. This removes the HTML linter's false `font.*:.*ahem` match spanning `fontData.slice(0) : 'url(...)'`. The Ahem heuristic only runs for HTML; formatting the canvas helper identically is harmless.

No extra Ahem stylesheet or font-family declaration is added, because these tests already fetch and construct an explicit FontFace from the controlled URL/buffer resource. No other formatting change is necessary for the two reported lint issues. Root should rerun full lint after installing the exact two files; this capsule checks the relevant pinned regex and metadata source, not every WPT/ESLint rule.

## Sources and replay

`original/` retains v2 and `proposal/` retains v3. `TEST-PINS.json` binds both versions and production target paths; `wpt-v2-to-v3.patch` is an exact two-file transformation. Pin FREEZE.json, then run:

```sh
python3 artifacts/css-fontface-provider-wpt-v3/check.py
```

The checker authenticates this capsule and integration-v1 before helper execution. It confirms the exact two string transformations, applies and reverses the patch with zero fuzz, runs Node syntax checks, and registers exactly the same 12 DOM, 28 window canvas and 28 dedicated-worker canvas names in both versions. Registration does not execute callbacks. It also extracts the actual regex constants from pinned WPT source, verifies accepted spec metadata, confirms the original false-positive match and its absence in v3. Python, Node and patch are required; the sibling integration-v1 source capsule supplies authenticated provenance. CHECK-RESULT.json is an excluded receipt.

The primary spec URLs were reopened on 2026-10-19: [FontFace interface](https://drafts.csswg.org/css-font-loading-3/#fontface-interface) and [size-adjust descriptor](https://drafts.csswg.org/css-fonts-5/#size-adjust-desc). These reproduce existing DOM help targets; no normative oracle is changed. The raw tool strips URL fragments, so anchor spelling is additionally inherited from the already reviewed DOM test rather than claimed as a fresh HTML-id audit.

## Browser evidence boundary

This is metadata and whitespace only, with an exact reverse transformation and unchanged registration. A new original-browser baseline is unnecessary for the semantic comparison when root retains the v2 pair. Root must still run the final candidate matrix on v3 bytes and record the v2→v3 input identity bridge. Do not silently run v3 against the sealed v2 harness pins: derive final TEST-PINS with these v3 hashes and retain the mapping. No native build/browser was run here, and syntax/registration checks do not prove rendering results.
