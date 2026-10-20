# Hidden descendant geometry: source investigation

Status: **regression under investigation; provisional repair untested**.

The retained 32-row probe has 160 stages per browser. Independent recount finds zero bad stages in installed Firefox 158 and 32 in the shared project build. All project failures are flex cases after sibling insertion while hidden; repeated queries remain wrong. Block controls pass, and showing the content restores the target. This does not establish an upstream Firefox bug. The project contains accepted local changes and unaccepted prototypes, and the release is an older version.

## Specification trace

Scenario: an ordinary connected, nonfragmented div with fixed width 24px and height 32px, without borders, padding, transforms, top-layer status, or `display:none`, inside a hidden flex container.

1. [CSSOM View: getBoundingClientRect](https://drafts.csswg.org/cssom-view/#dom-element-getboundingclientrect) delegates to getting the element's bounding box.
2. [Getting the bounding box](https://drafts.csswg.org/cssom-view/#element-get-the-bounding-box) obtains `getClientRects()` and combines those rectangles.
3. [getClientRects step 3](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects) describes the border area of each box fragment. The first-step no-box exception does not apply to this scenario.
4. [CSS Containment: skipped contents](https://drafts.csswg.org/css-contain-2/#skips-its-contents) imposes containment and suppresses painting and hit testing. It does not turn ordinary descendants into `display:none`. Its [geometry-query example](https://drafts.csswg.org/css-contain-2/#cv-examples) corroborates the forced-layout interpretation; the example is informative, not the normative hook.

**Verdict: REACHED for the rectangle requirement**, by the explicit CSSOM algorithm and applicable box model. Returning a zero border size is not a permitted layout-skipping optimization here. Automated `trace` reported no indexed route; the manual chain above uses the captured algorithm sections rather than treating graph absence as a semantic result. The requested `#example-2` anchor failed validation; `#cv-examples` resolves.

Existing WPT `content-visibility-088.html` covers a block descendant query. `content-visibility-forced-layout-client-rects.html` covers nested skipped ancestors. Neither fetched test exercises hidden flex sibling insertion and repeated reads. No current pass/fail status is inferred from file existence.

## Native path and concrete hypothesis

The frozen exact HEAD sources are authoritative for this analysis. Searchfox discovery output is retained separately; some `--define` queries returned a nearby unrelated snippet, so those are not accepted as exact method bodies.

- `nsIContent::GetPrimaryFrame(Layout)` first flushes ordinary layout, then calls `PresShell::EnsureReflowIfFrameHasHiddenContent` and reacquires the primary frame.
- `UpdateHiddenContentInForcedLayout` returns immediately when the requested frame is clean. For a dirty frame, it records hidden in-flow ancestors and requests reflow of the topmost such ancestor. The subsequent flush temporarily makes `HidesContentForLayout()` false for recorded ancestors.
- `SizeItemInCrossAxis` measures the block-axis cross size even for a fixed-height block. `MeasureBSizeForFlexItem` reuses a measurement only when the item is clean and the entire key matches.
- On a miss, it invokes `ReflowChild`, then `FinishReflowChild`, and stores the result. An ordinary hidden block child's `Reflow` may return without producing its real geometry. `FinishReflowChild` still installs the returned size.
- `nsIFrame::DidReflow` preserves dirty state for a hidden child; it does not make an already-clean child dirty. Therefore a skipped measurement entered on a clean child can install zero size while leaving it ineligible for the later forced geometry flush.
- Local commit `6cf27eadddf9` adds the containing-block size to the measuring-cache key. A containing-block change can now reject a clean child's measurement even when the fixed item size stays unchanged. This is a concrete candidate explanation for the release/project difference, not a traced runtime key value. Preserve that key: it fixes genuine containing-block-dependent measurement reuse.

The uncommitted flex skip-predicate difference involving `GetNextContinuation()` cannot by itself distinguish the ordinary nonfragmented fixture. Shared `nsBlockFrame.cpp` differs from HEAD only in float recovery, which this empty fixed-size child does not exercise. Root is isolating HEAD flex sources and accepted changes; this artifact runs no browser or build.

## Provisional source repair

`candidate-provisional.patch` adds `NS_FRAME_IS_DIRTY` to a hidden flex item immediately before an actual measuring reflow after a cache miss. It leaves valid measurement reuse alone. During forced layout the hidden-for-layout predicate is false, so ordinary successful completion can clear dirty state normally. This preserves the containing-block key and makes a skipped measurement eligible for the descendant geometry flush.

This is a targeted proposal, not accepted native behavior. Required checks are:

- Confirm the regression boundary and actual cache miss/clean-item sequence; distinguish cached containing-block values from inferred ones.
- Verify forced layout remeasures rather than reuses the skipped zero result and leaves no persistent dirty/reflow loop.
- Review hidden nested flex/grid, anonymous in-flow parents, insertion/removal, continuation, and show/hide invalidation paths. This proposal does not repair arbitrary grid code or change shared completion APIs.
- Run the proposed WPT, retain block controls, and rerun containing-block/percentage-descendant and padding-cache regressions. Do not withdraw cache-key correctness to eliminate this fixture's failure.

## Proposed WPT

`content-visibility-hidden-geometry-after-insertion.html` has 24 subtests: block/flex/grid × initially visible/hidden × bounding/client rects/offset/scroll dimensions. Each collects initial, hide, first insertion, second insertion, and show phases with three repeated reads before asserting. It retains the original parent geometry flush sequence and uses only 24×32px items. The complete lifecycle is sampled even if an earlier stage is wrong. Grid is an additional diagnostic/control until its result and cause are isolated.

## Evidence limitations

No compiler, browser, main-source, index, or commit operation was performed. Source snapshots and the provisional patch are artifact-only. The runtime recount references root-owned receipts and authenticates their bytes, but does not recreate the browser runs or prove internal states. No new bug count, security finding, full lifecycle proof, or native acceptance is claimed.
