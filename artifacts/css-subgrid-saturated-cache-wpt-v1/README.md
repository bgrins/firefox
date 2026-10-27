# Proposed saturated-cache landing tests

Artifact-only, unexecuted proposal: six testharness cases, one file, combined with the exact pending three-source saturated-cache patch. No native acceptance, assigned fix, baseline browser observation or candidate browser result is claimed. The existing82-case diagnostic and all sealed source proposals remain unchanged.

Landing path: `testing/web-platform/tests/css/css-grid/subgrid/subgrid-repeat-count-capacity.html`.

Each of columns and rows tests these three positive-literal shapes, with auto-fill first:

| Witness | Exact fixed count | Signed32 narrowing | Old64-bit remaining at C=3 | Expected fixed prefix |
|---|---:|---:|---:|---|
| INT32_MAX ×2 |4294967294|−2|5|[a][b][a]|
|1431655766 ×3 |4294967298|2|1|[a][b][c]|
|INT32_MAX ×2 +1+1|4294967296|0|3|[a][b][a]|

All three native64-bit subtractions are representable; none narrows to INT32_MIN. The second and third cases additionally cover32-bit product and accumulation overflow respectively. On an unchecked32-bit baseline those operations can wrap; on a checked32-bit baseline they may panic. No32-bit baseline execution or resulting behavior is asserted. The candidate saturation policy is intended to cover both widths. Testing that candidate requires actual compilation/runtime, beyond this proposal.

Each case creates only three200×200 parents with two fixed tracks per axis and one spanning child each. The reference uses literal repeat(2); the small auto-fill control uses the same reference with auto-fill first. Admission, retained large count, both parent track lists, parent/child dimensions, both axis spans, literal resolved prefix and repeated resolved values all precede the final large-count assertion. The full literal repeat counts are retained in source syntax; the native append limit caps the admitted span to three line-name entries. No large expanded array is built by the test. All nodes are removed by per-test cleanup. This is a line-name/capacity test, not a stale-first-read readiness oracle, so the calibration reads deliberately flush layout.

The small literal reference is independent of the defective cache arithmetic and confirms the expected prefix. `Witnesses.lean` kernel-checks the three exact integer products/sums/narrowings and the small reference prefixes; four anonymous examples add no named theorem or canonical credit. Python independently rederives exact counts and signed projection in results/ARITHMETIC.json. These are source-conditioned calculations, not recorded browser outputs.

## Focused existing controls

Searchfox discovery was restricted to `testing/web-platform/tests/css/css-grid/subgrid` and the strings auto-fill/getComputedStyle. Exact HEAD90 snapshots/pins, references and metadata are retained in CONTROL-PINS.json. Recommended later comparison roster is new6 +existing60 testharness subtests +four reftests, across seven test files:

- `grid-template-valid.html`:38 exact parser registrations covering both axes, fixed repeats and auto-fill.
- `grid-template-invalid.html`:22 exact rejection registrations, including invalid repeat/group syntax.
- `repeat-auto-fill-001.html` →`repeat-auto-fill-001-ref.html`: zero/full/partial remaining capacity, position before/after fixed names, ordinary repeated groups.
- `repeat-auto-fill-006.html` →`repeat-auto-fill-005-ref.html`: row serialization in vertical writing mode and fixed/auto repeat combinations.
- `repeat-auto-fill-008.html` →`repeat-auto-fill-008-ref.html`: multi-group auto-fill and remainder/truncation behavior.
- `line-names-005.html` →`line-names-005-ref.html`: inherited/resolved line-name placement and truncation with existing track repeats.

The four latter files are reftests, not testharness case arrays: their scripts append visible mismatch text, which participates in the reference comparison. Their nominal end status is PASS; the two parser files and new file require OK harness ends. Existing line-names-005 metadata allows [PASS,FAIL] on nondebug mac/Android; retain that metadata and the actual paired outcome/diagnostics, rather than treating its optional improvement as this repair or waiving regression. Other selected per-file metadata is absent in HEAD90; inherited grid/subgrid prefs are retained. These are proposed controls with no new run or expectation rewrite. CONTROL-ROSTER.json is obtained by evaluating the pinned parsing registration helper with inert test callbacks; DOM test bodies are never executed.

## Checks and scope

`wpt.patch` adds only the new file; `standalone.patch` is byte-for-byte pending source proposal.patch followed by that addition. Source originals/candidates are pinned separately, and scratch Git apply/check/reverse checks all four final paths against explicit HEAD90 preimages. This is textual applicability, not pristine-upstream browser validation. The new WPT cannot establish source-cache correctness for negative calculated counts, malformed native caps or all possible line-name constructors; those remain separate domains from these positive witnesses.

Reproduce into an absent output directory:

```
python3 artifacts/css-subgrid-saturated-cache-wpt-v1/check.py --output /tmp/absent-subgrid-landing-review
```

The check authenticates immutable references, runs Node syntax/inert registrations, applies/reverses the exact patch in an owned scratch Git repository, invokes existing Lean with two threads, and checks exact arithmetic. Temporary repository/compiler products are removed. No browser, Gecko build, native source/index or canonical library was changed. The Firefox frontend skill was applied; direct style assignments and synchronous geometry reads are intentional test inputs/oracles, not product hot-path code.
