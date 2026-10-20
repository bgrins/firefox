# Independent review: CSSOM rectangle precision proposal

Verdict: **GO for the reversible native/browser experiment; no source blocker found in the bounded ordinary path. Native landing remains conditional on actual build, paired tests and regression gates.** This is independent review of another producer's proposal, not a review of my own earlier numeric model.

Authenticated proposal: `css-exact-size-observer-repair-proposal-v1`, FILES `e004c9cb0243fbe6ecf0c74d48d84eb87e5c64e4dec72e5c6a3dad87372dfbd1`; all 175 payloads match. REPORT `50235ceb0e3effb19b756e7d794a58e732aaadc495d6098593864313f400a710`. Exact originals, candidates, patch, provider files, header closure, calibration and checker were inspected. The proposal has not been treated as a complete native translation proof.

## Required correction and tests

The original report says52 proposed WPT subtests. Actual registration is **28: 2 axes × 3 sizes × 2 host sizes × 2 padding modes, plus 4 controls**. `WPT-REGISTRATIONS.json` independently executes registration in a Node VM without invoking test callbacks and records all 28 unique names. This does not run a browser or establish any assertion's success. The producer's separate correction was authenticated after the source review; `CORRECTION-RECEIPT.json` retains its exact text and pins. The old report remains immutable.

The calibrated containing edge and small marker are appropriate independent geometric oracles. The size calibration prevents silently clamped enormous boxes from being counted as successful cases. The marker's -3px correction in padded cases reaches the border end rather than the padding end. Fixed integer host controls, fractional host cases, both axes and padding variants are materially distinct. The0.0001px assertion allowance is smaller than the1/64px and1/128px defects; it is a test tolerance, not a replacement theorem for exact safe-origin containment.

The four small coordinate controls have coherent expected values: explicit translation adds7/11; host scale2 and zoom2 double its100px edges; the scrolling control places the400px-wide box at350 after scrollLeft50 and leaves its40px bottom unchanged. Source checks do not establish these controls pass at runtime.

## Integer path: independent admission analysis

The changed `BoxToRect::AddBox` branch is reached only for AccountForTransforms, `outer != mRelativeTo`, a root-relative target and no substituted SVG outer frame. Other callback modes and arbitrary non-root relative frames keep their original path. The root predicate alone is insufficient; the new helper additionally must reach that exact ancestor by actual GetParent links.

`RelativeTo` defaults to Layout. This call does not ask for Visual coordinates or IgnoreScrolling. In complete retained `nsIFrame::GetTransformMatrix`, the visual-viewport inversion is conditional on a Visual target. The remaining ordinary branch accumulates GetPosition. `GetCrossDocParentFrameInProcess` returns GetParent directly when present, with no extra offset. A same-prescontext GetParent chain reaching the target therefore selects the same translation contributors. This argument is about the existing source branch and intended integer displacement, not old float bit-for-bit equality.

- **Transform and perspective:** each traversed frame is rejected if IsTransformed. Its source includes CSS transform/transform-animation and parent SVG transforms. Actual perspective incorporation occurs in the transformed matrix branch, which therefore remains on the original route. A perspective style without a transformed descendant does not cause a hidden extra operation in this ordinary source branch. A potentially stale transform flag would also be a provider/lifecycle defect outside this review; it is not assumed to be independently repaired.
- **SVG:** the call site rejects a substituted SVG outer frame, and the helper rejects SVG-layout and SVG-text-subtree frames along the chain. ForeignObject/ordinary descendants whose chain reaches SVG are conservatively rejected. The original SVG-text-special transform code is retained. Excluding only CSS transforms would not have been sufficient.
- **Scale, documents, root and viewport:** every traversed prescontext must match the target. The helper cannot traverse a cross-document embedder through GetParent; if the target is not reached, it returns Nothing. The target's own transform/position is intentionally excluded because output is relative to that target; the old walk likewise stops there. No general claim is made for APZ/Visual coordinates or arbitrary cross-document geometry.
- **Scrolling, relative/sticky position and CSS zoom:** the helper uses actual stored GetPosition, matching the old default flag branch. It does not recompute offsets from styles or use GetPositionIgnoringScrollingAndSticky. Same-prescontext ordinary CSS zoom does not introduce an extra transform branch in the retained old source; positions and sizes carry layout zoom. The real getter/state coherence remains a source-provider assumption.
- **Clipping:** TransformGfxRectToAncestor applies its maximum-coordinate clip once after matrix composition. On the admitted pure translation route there is no projective W clipping or intermediate coordinate clip to preserve. CSS overflow/clip-path paint clipping is not performed by this bounding-box route and must not be added to the new path. The new final endpoint checks keep the exact rectangle inside the existing coordinate domain.
- **Extent cap:** endpoint checks alone are insufficient. `ConstrainToCoordValues` separately caps the span to Q and recenters it. The proposed width/height bounds0..Q are necessary and present. The prior development omission is not in the authenticated final candidate. Empty rectangles are admitted with their location preserved.
- **Arithmetic:** CheckedInt guards both coordinate prefixes and both final endpoints before extraction. Since width/height are nonnegative, checking the near edge against MIN and the far edge against MAX also bounds the other two inequalities. Prefixes may exceed the narrower nscoord coordinate limit while staying inside signed32 and later cancel; this does not bypass any old intermediate coordinate clip. Rejected integer overflows return to the old matrix route, so this is not a repair of preexisting arithmetic risks on rejected inputs. The old grouping of offsets can differ from the new checked grouping; no old-definedness theorem is inferred from candidate safety.
- **Lifetime and graph:** the actual frame tree must be acyclic, live and stable during traversal. No universal frame-construction/callback theorem is proved here. These are existing native execution requirements, not a fuel cutoff silently treated as valid geometry.
- **Collection and consumers:** table/caption traversal, continuation traversal and callback union are unchanged. The helper affects all root-relative AccountForTransforms users of BoxToRect, not only the two Element APIs in the new WPT. Existing callback union arithmetic remains a separate domain. The source review does not treat finite helper-facade tests as proof of every caller's input validity.

The actual CheckedInt header is already included by the original translation unit; no missing new include was found. Successful ordinary calls replace the existing matrix ancestor traversal with a checked traversal. Failed calls can pay a partial additional walk before the old path; no performance improvement or absence of regression is asserted.

## DOMRect conversion

`SetLayoutRect` keeps the existing 1/65536px endpoint preparation and changes only publication into double fields. The inspected SetX/SetY/SetWidth/SetHeight methods directly assign those fields; they do not invoke script, notification or additional computation. Existing SetRect(float,...) and its other callers remain unchanged.

This is independently useful and affects all SetLayoutRect consumers, including results that still use transformed/SVG paths. It does not fix errors already introduced by matrix geometry or app-unit reconversion. It also does not address preexisting signed endpoint overflow in an invalid nsRect. Actual build and relevant geometry regressions are required despite the small implementation change.

## Split into two changes

The one-file slices `dom-only.patch` and `integer-only.patch` are exact differences of the authenticated candidate/original files. Their code edits commute and have no compile dependency on each other. This is snapshot application evidence, not a Git/upstream standalone packaging claim.

| Change | Distinguishing standalone test proposal | Source-shaped prediction |
| --- | --- | --- |
| DOMRect double publication | `dom-only.html`: explicit identity transform, width/height131072.0666667px, integer100px host, small120.125px controls | The transform forces the original matrix route even when the integer helper exists. At the independently demonstrated app-unit inputs, base/integer-only gives99.9921875; DOM-only/both gives100. |
| Ordinary integer translation | `integer-only.html`: no transform, width/height139808.125px, integer100px host, small120.125px controls | At the demonstrated app-unit inputs, base gives100.015625; DOM-only gives100.01666259765625; integer-only/both gives100. |

Each proposed split file registers four tests, with marker/size/containing-edge/client-count calibration. Their browser outcomes have **not** been observed by this reviewer. The exact source path, chosen app-unit inputs and device factor still need the root runtime evidence; identity CSS transform is a source-backed selector of the matrix route, not a direct observation of its internal values.

Do not put fractional-host100.1 cases into an integer-only landing test without independent verification: they can expose the separate DOMRect publication boundary. The combined28 suite remains useful after both fixes but is not a causality oracle by itself. The root's four-variant experiment should record failures as well as improvements, and the additional identity-transform test should be run before choosing split landing witnesses.

## Scope and remaining gates

Root owns the actual reversible builds and browser experiments. This report does not report their unfinished runs as passes. Retain separate gates for native compilation/formatting, baseline and each candidate, current CSSOM/geometry/transform/SVG/iframe/scroll/zoom regressions, and source/binary restoration. Existing source-identical fallback code is evidence of preservation intent, not a substitute for those gates; the DOMRect precision change affects fallback observations too.

The original exact safe-origin F1–F12 obligations remain unmodified. This bounded source review does not establish actual layout output size, arbitrary reflow/cache lifecycle, full machine geometry, or all reachable overflow. The independent numeric component provides exact local conditions and counterexamples, not a general frame/matrix correspondence theorem.

Primary semantics: [CSSOM View client and bounding rectangles](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects), [Geometry Interfaces rectangle accessors](https://drafts.csswg.org/geometry/#DOMRectReadOnly). These were verified during the associated numeric review on20October2026. No global tolerance, clipping of CSSOM rectangles to paint overflow, or numeric source-translation guarantee is inferred from them.
