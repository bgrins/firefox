# Hidden SVG matrix query audit

Status: source-conditioned lead and unexecuted eight-row diagnostic. No new accepted bug, native change, or browser result. The immediate next step is a guarded capture of `probe.html` on the root's restored working build, followed by `validate.py` on the captured JSON.

## Concrete readiness boundary

`SVGGraphicsElement::GetCTM` and `GetScreenCTM` flush the document's layout and immediately call `SVGContentUtils`. They do not call the hidden-content forcing path used by `GetBBox`. `GetCTMInternal` obtains primary frames without a flushing argument, composes `ChildToUserSpaceTransform`, and, for screen coordinates, frame offsets and ancestor transforms.

For an outer SVG, `SVGViewportElement::GetViewBoxTransform` reads `mViewportSize`. `SVGOuterSVGFrame::Reflow` updates that stored viewport from its computed CSS width/height. Therefore a layout flush which skips the hidden owner's descendants can leave the matrix provider's viewport stale even when the owner itself has its new width. This is a falsifiable source hypothesis; no native dirty state or skipped branch has been observed in this audit.

The required invariant is: before publishing a matrix whose scale depends on the outer SVG's CSS viewport, that viewport must reflect the current layout inputs, or the query must follow the specified unavailable-result case. Flushing pending document layout alone does not establish the first premise in a skipped subtree.

`getBBox()` and `getComputedTextLength()` instead use `GetPrimaryFrame(Layout)`. `nsIContent::GetPrimaryFrame` calls `EnsureReflowIfFrameHasHiddenContent` and reacquires the frame. The current forcing implementation only enters for a dirty queried subtree (apart from the accepted table-provider case), then finds hidden in-flow ancestors and forces their layout. Thus these two entrypoints have the expected forcing hook; this is a bounded negative finding, not a proof that all SVG dirty histories are safe. Fix107 marks skipped block children dirty, which can make the deliberate recovery query succeed in the working build. The CTM lead itself is a separate bypass of that hook.

## Spec and existing coverage

[SVG2 SVGGraphicsElement](https://svgwg.org/svg2-draft/types.html#InterfaceSVGGraphicsElement) defines matrices from the element's current coordinate system to its SVG viewport, or the document viewport for `getScreenCTM`. ViewBox and CSS box transforms participate. Its disconnected/non-rendered style-resolution cases remain relevant; this probe uses connected elements warmed while visible and does not test those cases.

[CSS Containment](https://drafts.csswg.org/css-contain-2/#content-visibility) permits skipped work. Its geometry-query example describes forcing layout for correct geometry, but is informative. The matrix expectation here comes from the SVG coordinate definition and a visible twin, not from treating that example as a universal normative forcing algorithm. The current draft was read on 2026-10-23 (Containment header: 15 October 2026).

The retained `content-visibility-svg-text.html` shares a hidden tspan across tests. Its earlier text-length query forces layout before the matrix checks, which only inspect an unchanged transform. `content-visibility-039.html` exercises forced text length, not matrix-first viewport mutation. The accepted ledger contains the earlier SVG empty-mask fix, but no accepted CTM readiness repair; the adjacent hidden-provider audit did not cover these matrix entrypoints.

## Diagnostic and oracle

Eight independent rows are method (`getCTM`, `getScreenCTM`) × viewBox/no-viewBox × visible/hidden. Each fresh subject has a separate visible twin at the same position. Both are warmed at 100×100. The subject's visibility is changed and only its host rectangle is read. Both host widths then become 200px. The first descendant observations are the subject's matrix and repeated matrix; the visible twin is queried afterwards. There is no descendant geometry query between hiding/mutation and those first two matrix reads.

For viewBox `0 0 100 100` with `preserveAspectRatio=none`, the changed matrix is `[2,0,0,1,0,0]` for CTM and `[2,0,0,1,20,30]` for screen CTM. Without a viewBox, the scale remains one. The validator derives these values independently of the payload and checks both visible-twin and host dimensions. It records finite matrices/null separately, strict case identities, initial/repeated results, viewport forcing, visibility policy, and restoration.

After the observations, `getBBox()` and then the outer SVG's bounding rectangle deliberately force layout. Their matrix effects are diagnostic evidence, not the source of the first-read oracle. Revealing and restoring the host give further controls. The hypothesis predicts only the two hidden viewBox first/repeated reads might retain scale one; no outcome is enforced. A different result or failed calibration must be retained and investigated. The validator preserves all calibration failures and null matrix observations, rejects malformed/nonfinite data, and does not equate capture completion with a confirmed bug.

This first probe excludes auto-skipping, text/font mutation, nested SVG viewports, transforms, scrolling, display:none, disconnected nodes, and extreme coordinates. A later repair must preserve those existing API availability semantics; replacing a document flush blindly is not a reviewed patch.

## Provenance and checks

`SOURCE-PINS.json` binds explicit HEAD90 objects and current file hashes. Six SVG bodies match both the current source and retained HEAD; the outer-frame Reflow function also matches Searchfox although its full file differs. `FUNCTION-JOINS.json` and `CURRENT-EXCERPTS.cpp.txt` retain the exact relevant current functions. The installed table-provider change in PresShell and integer-geometry change in Element are explicitly distinguished. Searchfox source discovery copies are retained, not silently presented as the current full tree.

`STATIC-CHECK.json` records JS syntax and synthetic validator checks only. No browser, native build, lint, index, or runtime controller was executed. Serve `probe.html` through the existing owned capture runner: it POSTs one JSON payload to `/result`, and also works in a normal browser tab via its visible JSON output. Capture must bind the actual restored source/resource/binary epoch and preserve cleanup as usual; this capsule does not itself supply that runtime authorization.
