# FontFace provider WPT proposal v2

Artifact-only proposal; no browser execution or live test changes. Copy the two `proposal/` files to the corresponding `testing/web-platform/tests/css/css-font-loading/` paths only during root integration. The DOM file is byte-identical to the valid retained baseline. The canvas file preserves the complete original prefix and appends twelve tests per realm. `extension.patch` changes only that existing canvas test; it is not an add-file patch for an empty repository.

## Cases and independent expectations

| Diagnostic group | Cases per realm | Expected behavior |
|---|---:|---|
| Retained canvas tests | 16 | Exact previous URL/buffer calibration, pre-add, existing/new context, deletion/fallback and URL peer expectations. |
| Invalid setters | 2 | Negative percentage and non-percentage throw SyntaxError; descriptor stays 100%, width stays 80px, status and promise remain loaded/identical. |
| Equivalent setters | 2 | 100% and 100.0% serialize to 100%, width stays 80px, loaded state/promise unchanged. |
| Repeated updates | 2 | 50%, 125%, 100% give 40px, 100px, 80px in existing and fresh contexts; scale does not accumulate. |
| Removed mutation/re-add | 2 | Deletion selects calibrated 60px fallback; mutation does not restore membership; re-add uses 40px; deleting again restores 60px. |
| Simultaneous distinct-family peers | 2 | Target updates to 40px then 60px while old/new peer contexts remain 80px; both promises stay identical. |
| Same-family buffer peers | 2 | After deleting one face, the remaining changed face supplies 40px or unchanged face supplies 80px. |

Canvas executes 28 tests in window and 28 in dedicated worker. The unchanged DOM file adds twelve window tests, for **68 subtests across three harness files**. `CASES.json` records every exact registered name. Node registration only records callbacks; it does not execute FontFace operations or validate browser behavior.

Four Ahem X advances at a fixed 20px font size total 80px at size-adjust 100%. Percentage scaling gives the other widths. Both fresh 50% and 100% controls already exist. The test does not derive expected widths from a buggy mutation result. Fresh unique families avoid other tests' fonts; peer tests deliberately use shared families only when deleting one peer makes selection unambiguous. Each buffer face receives a separate copy of the fixture data; later setters operate on that already loaded face without reconstructing it or supplying another buffer.

The loaded promise and `load()` return identity follow CSS Font Loading's existing FontStatusPromise slot. Invalid/no-op cases are independent from successful mutation cases, so a failed mutation does not prevent those controls from running. `size-adjust` rejects negative percentages, scales metrics and preserves the CSS font-size. [FontFace loading](https://drafts.csswg.org/css-font-loading/#font-face-load), [size-adjust](https://drafts.csswg.org/css-fonts-5/#size-adjust-desc).

Tests observe independence, not the internal identity of deduplicated wrappers or platform entries. Repeated calls to measureText exercise current matching/caches, but do not prove a specific sharing path occurred. `assertLoadedIdentity` calls load only after status is already loaded and requires the existing promise; it does not await an extra load to make the geometry test pass.

## Resources and root run

`DEPENDENCIES.json` records exact retained source provenance and the Ahem SHA-256. Runtime paths are `/fonts/Ahem.ttf`, `/resources/testharness.js` and `/resources/testharnessreport.js`; .any.js receives the standard WPT wrapper/global helpers. No custom server handler or generated font is needed. The WPT runner's standard resources remain external, and source-only replay does not claim to authenticate a future server. Root must pin the actual served files at execution.

`RUN.json` gives the exact existing Mach command shape, destination paths, expected generated wrapper IDs/counts and regression paths. Replace PHASE with original/candidate. Keep the worker-detachment prerequisite on both builds and use these exact WPT bytes for both. Capture raw logs plus source/executable/resource identities. The old worker canvas baseline contains a distinct family-detachment failure and is not a valid substitute for this fresh pair. Root owns installation, build and browser execution.

## Explicitly open coverage

- Portable WPT cannot require a specific installed local font. Loading Ahem via URL or buffer does not install it for local(). Generic family names are not guaranteed local full/PostScript face names. No `local("Ahem")` pass/skip is presented as coverage. Platform testing needs a controlled installed font, successful face-load admission, a calibrated nonzero width, a mutation ratio and an unaffected peer. Unavailability is unresolved coverage.
- All tests await face.load before mutation. They do **not** exercise native-loaded/DOM-loading. A delayed response, sleep or repeated race loop does not deterministically hold the worker between native completion and DOM callback publication. That requires a privileged scheduling hook or native test; no WPT coverage is claimed.
- No shutdown/reentry, external font replacement, CSS-connected setter, arbitrary font technology, variation-axis/feature or metric-override proof is added. Existing descriptor regressions remain separate.
- No assertion counts or passing results here are browser observations. Root must adjudicate fresh original/candidate output and keep each diagnostic group distinguishable.

## Source-only validation

`python3 check.py` authenticates all local files, verifies the DOM identity and canvas prefix/extension relation, applies/reverses the extension patch in a temporary copy, checks JavaScript syntax and registers the tests in both declared realms without invoking callbacks. Requires Python 3, Node and patch, with no live tree access. The freeze records fresh relocated replay and tamper rejection. This checker does not replace WPT or invoke a native/browser build.
