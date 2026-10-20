# CSSOM rectangle precision repair proposal

Status: **READY_FOR_REVIEW_AND_REVERSIBLE_BUILD_EXPERIMENT**, not accepted or built as Gecko. This is a separate observer repair, not an exact-size transport patch. Full safe-origin obligations remain open.

## Browser evidence

Root's sealed `css-exact-size-observer-runtime-v1` has FILES SHA-256 `981df5c49843bbe325371489298ed73a0c0b58d26bf6e981faded2b99f7c2d30`. Both release and restored project completed 56 identical records. Four large ordinary absolute non-flex boxes have bounding edges 100.015625px, while their small border-edge markers report 100px and direct ResizeObserver border sizes report 139808.140625px. Four small controls agree at 100px. This separates the observable discrepancy from flex, table aggregation and replaced sizing. There was no integer native trace and getBoxQuads was unavailable under default preferences.

The previous sealed observer review documents the actual source path and conditional numeric reconstruction. Its original 32 supplemental failures are unchanged. The current source proposal does not reinterpret their assertions as passes.

## Proposed change

`native-proposal.patch` changes two implementations:

1. `BoxToRect::AddBox` tries an integer translation only for its root-relative, AccountForTransforms branch and only when it is not using a substituted SVG outer frame. `GetUntransformedRectToAncestor` walks the actual parent chain, rejects transformed/SVG-text/SVG-layout frames and different prescontexts, and accumulates positions with actual Mozilla CheckedInt. A null/missing ancestor, invalid intermediate, extent outside 0..nscoord_MAX, overflowing endpoint or out-of-coordinate-domain edge rejects the path. Rejected cases execute the original matrix path unchanged.
2. `DOMRect::SetLayoutRect` passes its existing double calculations through double setters. Its legacy `SetRect(float,...)` method and all other callers remain unchanged. Keeping the integer path without this second change would not preserve all aligned edges: the independent producer supplied exact x=-7,858,324au and width=7,864,324au, whose direct old DOMRect conversion yields 99.9921875px despite the native edge being 100px. This is a native numeric witness; its proposed browser width has not yet been run.

`proposal.patch` additionally includes the standalone WPT proposal. Candidate full files and original full files are retained. No production source, WPT tree, index or browser build was changed here.

## Actual source admission argument

| Obligation | Source argument and boundary |
| --- | --- |
| Correct coordinate space | The changed call site passes only a frame pointer to TransformFrameRectToAncestor. RelativeTo defaults to Layout in retained RelativeTo.h. The new branch is restricted to `mRelativeToIsRoot`; it does not alter arbitrary visual-coordinate callers of the transform utility. |
| No omitted CSS/SVG transform | Every traversed frame must fail IsTransformed, which includes CSS transforms and GetParentSVGTransforms. SVG layout and SVG text subtree frames are additionally rejected. `usingSVGOuterFrame` is rejected at the call site. Perspective/3D branches reached through a transformed frame therefore retain the old path. |
| Same scale and document | Every visited frame must have the destination prescontext. The chain uses only GetParent; crossing a document boundary or failing to reach the target returns Nothing. App-units/device-pixel conversion across prescontexts is not approximated. |
| Zoom and APZ | In retained GetTransformMatrix, the visual-to-layout inversion branch is conditional on a Visual destination and a zoomed-content-root test. This call is Layout-relative. Ordinary CSS zoom is already reflected in layout sizes/positions; the same-prescontext walk does not discard a separate visual transform. Visual viewport/APZ consumers outside this call site are unchanged. No general claim about arbitrary APZ callers follows. |
| Scrolling, relative and sticky offsets | The old default-flag transform route uses GetPosition, not GetPositionIgnoringScrollingAndSticky. The helper uses the same getter at every ordinary parent edge. Thus it retains actual stored positions rather than reconstructing them from CSS style. |
| Translation equivalence | With those admitted predicates, GetTransformMatrix's remaining branch aggregates positions until the target and returns a translation matrix. The proposal computes that same integer displacement plus the input rectangle origin before its float conversion. It preserves intended translation geometry, not the previous float rounding errors. |
| Coordinate clipping | Width and height lie in 0..nscoord_MAX, and both endpoint additions are checked; admitted start/end coordinates lie within nscoord_MIN..nscoord_MAX. Thus the admitted exact rectangle lies within the transform routine's coordinate clipping region and already satisfies ConstrainToCoordValues' separate extent cap. Rectangles outside that domain take the old path. This is not an equivalence assertion for prior float clipping at a representational boundary. |
| Intermediate cancellation | With all visited transforms rejected, default flags and one prescontext, GetTransformMatrix aggregates the whole segment to the root in one translation. GetTransformToAncestor's ProjectTo2D does not clip a translation. TransformGfxRectToAncestor applies TransformAndClipBounds once after composition, and ScaleThenRoundGfxRectToAppRect constrains once afterward. There is no intermediate nscoord-range clip to preserve on this admitted route. A tested signed32-valid prefix above Q followed by cancellation is therefore admitted. |
| Target ancestor | The target's own transform is excluded intentionally: coordinates are expressed relative to that target, and the old segment walk stops before applying it. The call site's BoxToRect constructor already dereferences a nonnull target; the helper also explicitly rejects null. A missing target in the actual parent chain rejects instead of crossing documents. |
| Every new integer operation | CheckedInt guards each x/y prefix and both final endpoint additions. Value extraction occurs only after validity checks. No unbounded chain-length assumption is used to justify a wide unchecked accumulator. Existing getter/frame-lifetime/acyclic-chain invariants are native provider obligations, not proved here. |
| Collection and observers | The callback receives one rectangle as before. Table/caption traversal, continuations, union accumulation and non-transform flags remain intact. DOMRect conversion preserves the existing 1/65536px endpoint rounding; it removes only the subsequent float parameter narrowing. It does not prove arbitrary union arithmetic safe. |

The actual frame predicates and positions are admitted as returned by their native getters. This source audit does not prove frame construction, cached flags, arbitrary mutation/lifecycle coherence, or every getter implementation. The exact callback branches and source methods are retained for review; no abstract assertion that current equals primary or that all ancestors are ordinary substitutes for their explicit run-time checks.

## Calibration

`calibrate.py` extracts the complete proposed integer helper and DOMRect conversion. It uses a small frame/rectangle facade and the retained actual Mozilla CheckedInt header closure. It does not compile nsIFrame, execute the full matrix path, or run a browser. Nineteen checks cover exact position, final DOM edge, both transformed-frame locations, SVG text/layout exclusions, context rejection, detached/null ancestry, checked prefix/endpoint failure, coordinate limits, overwide/negative/empty extents, intermediate cancellation and fractional/exponent-boundary DOM observations.

Candidate execution and six intended mutants run at O0/O2 with UBSan. Mutants omit transform, SVG-text, context, position or extent handling, or restore the old float DOMRect conversion. This checks the significance of the tested predicates; it is not an independent proof of the full Gecko provider chain.

Development history is retained: the first C++17 extraction failed because the real CheckedInt header requires C++20 std::in_range. C++20 succeeded. Later runs use the copied nine-header dependency closure rather than the live build directory. Temporary executables are removed automatically.

The final canonical and relocated replays agree, including all mutant outcomes. `verify.py` checks a closed file/directory roster and fixed source/header roles; `--replay-out` requires an output directory outside the capsule. The three-file patch applied and reversed in an isolated temporary tree with byte-exact candidate/original checks. Node syntax checking passed for the WPT script; no browser, WPT lint, actual translation-unit build or main-tree test execution occurred here.

Root's clipping review exposed an omitted extent cap in the initial proposal. The retained development source would admit x=-Q,width=2Q even though ConstrainToCoordValues reduces that extent to Q. The final proposal rejects such inputs; a dedicated mutant and challenge retain the distinction. This correction is required scope preservation, not a change in the observer target.

## Proposed WPT and remaining gates

`getBoundingClientRect-large-absolute-edge.html` proposes 52 subtests: 48 axis/size/padding/host-size combinations and four transform/zoom/scroll controls. Large ordinary boxes use 139808.125px; 131072.0666667px targets the independent DOM setter boundary. The expected aligned edge is measured on the small containing box, avoiding assumptions about engine-specific fractional layout grids. A zero-size CSS-positioned marker calibrates that edge independently of the large rectangle width. Bounding and single client rectangles must agree with the calibrated edge within 0.0001px; the original exact origin contract is not replaced with a large tolerance. The broader numeric-size check has its separate 0.05px calibration threshold.

Before native acceptance:

- Independently inspect the admission argument and two-file scope; then compile the actual Gecko translation units.
- Run paired standalone WPT and the 56 observer records. Preserve actual API differences and failed calibrations.
- Run existing CSSOM geometry, transforms, SVG, iframe, scrolling and zoom regressions. Existing matrix paths remain source-identical, but the double DOMRect observation change affects their final precision too.
- Confirm the actual native integer and matrix stages for a reduced witness if source/API observations leave attribution ambiguous. A source-shaped replay is not a replacement for recorded native values.
- Audit hot-path cost: successful ordinary cases replace a matrix ancestor walk with one checked walk; rejected transformed cases can add a partial ancestor walk before the existing path. No performance claim is made.

The [CSSOM View geometry algorithms](https://drafts.csswg.org/cssom-view/#dom-element-getboundingclientrect) require the enclosing border geometry; the proposal preserves the geometry effects while addressing precision loss. No implementation change is justified for arbitrary full transforms, cross-document scaling or visual viewport conversion by these ordinary controls alone.
