# Exact-size observer boundary review

Outcome: **DIAGNOSTIC_ORACLE_CORRECTION_AND_OBSERVER_LEAD**. No native repair or full safe-origin acceptance. The original 32 failed supplemental diagnostics remain recorded. Their current measurements do not establish 32 layout defects.

## Findings

1. The original table interpretation was wrong. `Element::GetBoundingClientRect` reaches `nsIFrame::GetBoundingClientRect`, `GetAllInFlowRectsUnion`, `GetAllInFlowRects`, and `AddBoxesForFrame`. The latter traverses a table wrapper's principal children. `BoxCallback::mIncludeCaptionBoxForTable` defaults to true; `BoxToRect` does not disable it. Each child contributes its own border rectangle. Thus the table element's bounding rectangle unions the inner table and caption, rather than exposing only the inner table or the wrapper. The original `wrapperEnd` reconstruction is not a reliable wrapper measurement. This corrects the README and interpretation in the immutable `css-exact-size-override-diagnostics-v1`; it does not modify that artifact or its failed tests.

2. The current CSSOM View draft agrees with this table collection. Its `getClientRects` algorithm includes table and caption boxes and excludes the anonymous container; bounding geometry encloses the nonempty collected rectangles. See [CSSOM View element geometry](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects), read 20 October 2026 (draft dated 8 October 2026). A finite non-transformed absolute box with right:0 and zero margin in a 100px containing block should consequently have its right border edge at 100px. The spec does not prescribe a numeric tolerance that excuses this particular residual. This remains an observer investigation, not an accepted browser bug.

3. An exact native edge can produce the observed image residual through geometry conversion. `BoxToRect` requests transforms even when no CSS transform is present. With the root frame as relative frame, it takes `TransformFrameRectToAncestor`: local app units become a float `LayoutDeviceRect`, the accumulated matrix maps the float rectangle, and `ScaleThenRoundGfxRectToAppRect` scales float components and rounds them back to integers. `DOMRect::SetLayoutRect` then rounds integer endpoints in double, but passes coordinates and dimensions to **`SetRect(float,float,float,float)`**, narrowing them separately. DOMRect's final members are double, which does not recover these losses.

4. The retained numeric challenge starts with native width 8,388,488au and x=-8,382,488au, so the native edge is exactly 6,000au. A conditional float rectangle round trip at 60au/device pixel produces x=-8,382,488 and width=8,388,489. The exact extracted DOMRect methods return x=-139708.140625, width=139808.15625, and right=100.015625. Those three numbers equal the candidate image border-box observation. The corresponding content-box width 8,389,448au gives right=100. The challenge therefore explains the pattern **without requiring any returned-size mismatch**. It is not a runtime trace of actual frame dimensions or the full matrix algorithm. A different native size plus a different conversion could also explain an observed rectangle.

5. My first interim source message incorrectly implied that double edge rounding in `SetLayoutRect` ruled out that method as part of the error. Inspection of its callee's float parameter types corrected this before the sealed report. The retained replay includes the full two-method call and both with/without preceding round-trip controls.

## Evidence and identity

`source/` contains exact Git HEAD snapshots of nine relevant files; `SOURCE-PINS.json` records independent live hashes, all equal at capture. Indexed discovery logs are retained separately. The indexed DOMRect CPP/header are byte-identical to these snapshots; whole indexed layout utility files differ from HEAD, so the retained HEAD implementations are authoritative for this review. The relevant transform and collection methods were inspected in those HEAD files. No production file was edited.

`baseline-observations.json` and `candidate-observations.json` preserve the root runtime observations, source/binary pins and stable flag as seen at review time. `RUNTIME-INPUTS.json` pins their original result files. The root runtime capsule was not yet sealed at capture; these are subordinate observation snapshots, not independent browser executions or root-package authentication.

`replay.py` extracts complete `DOMRect::SetRect` and `DOMRect::SetLayoutRect` methods from the retained source. Its nsRect facade supplies ordinary signed integer coordinates and endpoint accessors. The preceding scalar float divide/multiply/round sequence is an explicit conditional model: it does not execute `GetTransformToAncestor`, `TransformAndClipBounds`, frame traversal, clipping, device scaling, or the coordinate constraint helper. Eight controls/challenges pass at O0 and O2 with UBSan. The two compiler outputs agree. No Lean theorem or universal geometry result is claimed.

## Discriminating browser proposal

Open `probe.html`, await `window.observerBoundaryPromise`, and collect `window.observerBoundaryResults`. There are 56 records:

- Eight minimal ordinary non-flex absolute boxes: small/large fractional width or height, zero/ordinary border-padding. Each has a zero-size descendant placed at its actual border end by CSS, not by arithmetic on its DOMRect.
- Forty-eight supplemental observations: original image and ordinary ratio configurations plus all column-reverse table variants, each at small and large sizes. Original fixture CSS and factory JS are copied byte-for-byte.

Every observation retains bounding rects, all client rects, computed scalars, optional border/margin quads relative to the host, ResizeObserver border/content sizes, host geometry, and available markers. No tolerance or original assertion is changed. No unexecuted probe result is reported as a pass. JavaScript syntax was checked with Node.

Interpretation:

- ResizeObserver's ordinary border-box path reads the primary frame's GetSize directly, unzooms, and converts to CSS float size. It avoids the rectangle matrix and independent x/width cancellation, but still rounds and is not an exact integer oracle. For the illustrated 8,388,488 vs 8,388,489au alternatives its scalar values differ, making it discriminating here.
- Border quads use corner points and `TransformPoints`, without the rect width round-trip or DOMRect SetRect. They still use float points/matrices. Agreement with a marker is useful evidence, not universal exactness.
- Table border quads and client rectangles include caption and inner table. Table **margin** quads explicitly suppress the caption and substitute the wrapper frame for the inner table; here zero table margins make this a useful wrapper-edge observation. It remains a separately implemented, rounded observer.
- A small ordinary marker tests a locally small rectangle positioned at the intended edge. Images cannot contain it, so nonreplaced controls and native tracing are retained as separate gates.

## Native trace if observations remain ambiguous

Root can instrument only tagged subjects, preserving pointer identity and integer units:

1. In `ReflowFlexItem`, log planned main/cross content and BP, computed child RI sizes, returned child desired size, logical position, and physical container size before FinishReflowChild. For the non-flex reduction, record its actual frame size and position after layout instead.
2. In `BoxToRect::AddBox`, log frame type/content tag and integer rectangle before transform, the actual relative frame, and integer rectangle after transform. This also identifies table/caption participation.
3. In `TransformFrameRectToAncestor`, log app-units/device-pixel factors, float rect before and after the real accumulated matrix, and rounded integer output. Record matrix and transform/zoom/scroll ancestry rather than assuming identity or translation-only eligibility.
4. At `DOMRect::SetLayoutRect`, log integer input plus double prepared endpoints and final float-passed x/width. Correlate the final element/client rectangle event.

The native and observer events together distinguish transport error, actual returned-size error, matrix rounding, scalar rounding, and table aggregation. Until then no source fast path is proposed. A future geometry repair must cover transforms, scroll offsets, cross-document coordinates, zoom/device scaling, clipping, SVG and continuation aggregation before changing this general path; the non-transform fixture alone cannot justify it.

Full safe-origin F1–F12 remains open. This artifact neither substitutes a tolerance-based origin contract nor claims exact transport guarantees arbitrary frame output.
