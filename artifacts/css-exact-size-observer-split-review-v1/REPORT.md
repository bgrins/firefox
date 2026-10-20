# Observer repair split and count correction

## Count correction

`CORRECTION.md` supersedes only the WPT counts in the sealed proposal and draft messages: the final unchanged test registers **28 tests**, comprising 24 parameterized tests and four controls. Individual rectangle assertions do not increase that count. No source, test, failure or acceptance obligation in the earlier sealed artifact is rewritten.

## Independent landing structure

Two separately landable repairs are plausible and preferable to bundling the causes, subject to root's actual four-variant experiment:

| Repair | Native change | Distinguishing candidate witness | Conditional result |
| --- | --- | --- | --- |
| DOMRect layout conversion | Only DOMRect.cpp: route existing computed doubles through double setters | Width 131072.0666667px aligned at edge100; an explicit identity CSS transform can force the unchanged matrix path | At native width7864324au: baseline and integer-only99.9921875; DOM-only and both100 |
| Ordinary rectangle translation | Only nsLayoutUtils.cpp: checked integer path under explicit root/layout/same-prescontext/untransformed predicates | Width139808.125px aligned at edge100, no transform | At native width8388488au: baseline100.015625; DOM-only100.0166626; integer-only and both100 |

The independent reviewer owns exact one-file slices and small standalone WPT proposals in `css-exact-size-observer-repair-review-v1`. This artifact does not create competing versions. Each proposed landing must pair its own native file with its own WPT and pass without the other repair installed. The combined 28-test proposal remains integration evidence; in particular the 139808.125px box in a fractional100.1px host needs both corrections in the conditional model and does not belong in an integer-only independently passing test.

`numeric.py` reproduces the conditional four-variant matrix using binary32 scalar operations. It is a diagnostic model, not the complete TransformAndClipBounds implementation or actual browser source trace. Its numeric expectations do not substitute for the root experiment. The original 32 supplemental failures and the exact observer obligation remain unchanged.

## Existing offset API and hot-path design

Searchfox found `nsIFrame::GetOffsetTo` and its retained `OffsetCalculator`; no `GetOffsetToAncestor` identifier was found. GetOffsetTo performs unchecked nsPoint additions, does not inspect transforms or SVG state, and deliberately supports a non-ancestor target by walking back from that target. Its prescontext equality is asserted, not a run-time rejection.

Reusing it safely here would first require an actual-ancestor/transform/SVG/context scan and a proof that its independent offset prefixes fit. That is a second traversal; the current helper already combines those checks and arithmetic into one. Merely checking the final accumulated offset does not prove that earlier additions were defined. Generalizing OffsetCalculator to add predicates and checked return semantics would broaden the shared API and its consumers. For this bounded repair, retain the fused local helper unless broader review identifies an existing equivalent checked traversal.

A computed matrix classified as a translation is insufficient to justify substituting GetPosition sums: a CSS translate can itself yield a translation matrix, and its displacement is absent from GetPosition. The actual ancestor predicates must remain. Likewise an identity matrix resulting from cancelling transforms is not proof that their intermediate processing or SVG semantics can be skipped.

Successful ordinary calls replace matrix setup/conversion and the old ancestor walk with a checked walk. Failed candidates add a partial walk before fallback; a deeply nested transformed ancestor can therefore add work. This is a concrete cost to measure, not a demonstrated regression or claimed speedup. No broader transform, visual viewport/APZ or cross-document path is changed by the proposed integer admission. The double DOMRect conversion affects the final precision of those paths, so they still need regression coverage.

## Focused existing regression gate

`REGRESSIONS.json` lists eight additive tests, selected by Searchfox and read in full. They complement the root's existing thirteen rather than requesting a broad unrelated suite. Retained indexed sources are compared against local bytes in `TEST-PINS.json`; resources remain dependencies of the normal WPT runner.

| Test (under testing/web-platform/tests/) | Relevant behavior |
| --- | --- |
| css/css-transforms/3d-rendering-context-behavior.html | Nested preserve-3D, perspective, and absolute/fixed descendants must retain their matrix route. |
| svg/extensibility/foreignObject/getboundingclientrect.html | SVG covered-region handling and HTML descendant coordinates. |
| svg/extensibility/foreignObject/containing-block.html | Relative, absolute and fixed HTML descendants across foreignObject. |
| css/cssom-view/getClientRects-inline-with-block-child.html | IB-split collection and zero-width/height rectangles. |
| css/cssom-view/elementsFromPoint-iframes.html | Iframe/scroll-frame geometry feeds four-corner hit-testing points. |
| resize-observer/notify.html | Direct contentRect conversion, including fractional dimensions and padding origins. |
| intersection-observer/client-rect.html | Observer entry versus element rectangle in an iframe with fractional margins. |
| intersection-observer/iframe-root-with-overflow-propagation.html | Explicit iframe document root, overflow propagation, scrolling and clipping. |

The existing root gate already covers getBoundingClientRect-scroll, getBoundingClientRect-zoom, getClientRects-zoom, SVG/tspan/Range, vertical-rl, and ordinary client rectangles. GeometryUtils/getBoxQuads tests are not offered as passing coverage under defaults: that API was unavailable in the actual browser probe.

## Separate test-quality lead

While reading `css/css-transforms/preserve-3d-flat-grouping-properties.html`, I found `assert_not_equals(mixBlendMode.getBoundingClientRect().width), nonflatWidth;`. The second argument is outside the call. This appears to be a narrow good-first-bug test correction; it is not a Gecko geometry defect or accepted project bugfix. The file is retained as discovery evidence but is not needed in the eight-file gate. No production test was changed.

## Scope and status

This is a correction/source-review receipt, not a native acceptance. Root owns the four-variant browser/build experiment and the independent reviewer owns standalone split WPTs. Main native files, browser, build and index were not changed here. Sealed predecessor artifacts remain byte-identical.
