# CSSOM rectangle numeric conversion

Status: **bounded numeric component and two exactness counterexamples**. No production repair, browser execution, or full safe-origin acceptance. The original F1–F12 contract is retained in `FORMAL-SCOPE-PLAN.md`.

## Findings

There are two independent boundaries. An app-unit rectangle first becomes a float graphics rectangle, passes through the actual ancestor matrix/clipping operation, then is scaled and rounded back to app units. `DOMRect::SetLayoutRect` subsequently prepares rounded endpoints in double but calls `SetRect(float,float,float,float)`. That call narrows the start and width independently. Double storage afterward cannot recover the lost bits.

| Conditional input | Actual extracted conversion | Result |
| --- | --- | --- |
| x=-8,382,488au, width=8,388,488au; exact end=6,000au | scalar graphics round trip at 60au/pixel, constraint/rounding, then DOMRect | x=-139708.140625, width=139808.15625, right=100.015625 |
| Same integer input, omit graphics round trip | DOMRect only | right=100 |
| x=-7,858,324au, width=7,864,324au; exact end=6,000au | DOMRect only | x=-130972.0703125, width=131072.0625, right=99.9921875 |
| x=-1,208au, width=7,208au | scalar graphics round trip and DOMRect | right=100 |

The third row is an independent exponent-boundary counterexample: an integer geometry fast path alone cannot establish universal exact CSSOM edge preservation while this float setter remains. It is a numeric provider witness, not a claim that a particular browser layout produced those app units. The other agent's proposed repair separately addresses both boundaries; its source and acceptance are outside this capsule.

## Exact contract, not a tolerance

The model uses integer units of 1/65536 CSS pixel. `grid` independently computes nearest-grid rounding from integral app units. `narrow` computes nearest-even quantization on the binary32 significant-bit lattice for integral grid units. It is a mathematical integer definition, not Lean's native floating-point implementation.

For prepared start X and prepared end E, the observed edge is `narrow X + narrow(E-X)`. Its difference from E is exactly the sum of the two component quantization errors. `exact_edge_iff_cancel` proves the necessary and sufficient cancellation condition. `exact_original_edge_iff` includes the original app-unit endpoint, so it does not silently discard an earlier changed endpoint or grid rounding.

`app_round_exact_iff` independently characterizes nearest-app-unit rounding by the half-open cell around the original integer (ties go upward, including negative ties). Its input is an integer representation in units of 2^-32 app units. This is a bounded dyadic interface, not a claim that every possible graphics input has that representation.

`local_domains_join_exact_edge` combines those rounding cells with a representable start and representable width and an endpoint divisible by 15 app units. Divisibility by 15 makes the original endpoint exactly representable on the 1/65536 grid. Component representability is expressed by remainder modulo their independently calculated binary32 quantum. These are sufficient local numerical conditions, not an assumed equality of the final observer with the desired edge. Other inputs can preserve the edge by cancellation; the iff theorem covers that possibility. No tolerance replaces the original exact containment requirement.

The finite kernel witnesses preserve both losses, the direct-DOM control, half ties, small control and failure of universal cancellation. The general kernel result is an integer/dyadic composition result. The mapping from IEEE operations to that model, actual runtime matrix values, and the chosen app-unit scale remain separate boundaries below.

## Native and independent reference

`native/run.py` extracts eleven complete bodies: the scalar app-unit-to-float helper; double app-unit rounding and its clamp; both coordinate-constraint helpers; `ScaleThenRoundGfxRectToAppRect`; `RoundFloat`; both DOMRect setters; the right accessor; and the two-axis rectangle scale method. `BINDINGS.json` authenticates each source/anchor/body. Extraction is repeated during replay.

The harness executes the actual constraint/recentering and integer-clamp logic, including large-span and coordinate-boundary controls. It runs 53 fixed input cases at O0 and O2 with UBSan. The source-shaped rectangle facade preserves named scalar fields and width-zero behavior; coordinate wrappers, nsRect endpoint accessors, finite NaN-safe maximum, and app-unit constant are explicit adapters. Matrix/frame traversal is not stubbed and advertised as complete: it is outside this execution boundary.

The reference uses Python exact fractions and independent nearest-even rounding to 24/53 significant bits. It models intermediate binary32 casts/division/multiplication, clamp/recenter, integer rounding, binary64 endpoint preparation, binary32 parameter conversion and binary64 addition. Its domain is finite normal numbers plus zero, without subnormals, NaNs, infinities, alternate rounding modes or fast-math. It does not invoke native output as an oracle. The 53-case roster is checked in full, with nine output fields per case. Equality is exact, without epsilon.

Three compiled semantic controls must produce differences from this original policy: double DOMRect parameters (a candidate-style improvement, not labeled a bad repair), omitted graphics round trip, and truncating app-unit conversion. Three independently false Lean claims must be rejected. These are controls for the scoped model; no claim of universal compiler/IEEE correctness follows from finite agreement.

## Browser calibration

Root supplied `css-exact-size-observer-runtime-v1` release and project results, copied unchanged here with their source/binary/test pins. Both have 56 rows and stable before/after pins. Replay checks all eight non-flex calibrations per profile: small boxes end at100; large boxes end at100.015625; small descendant markers end at100; ResizeObserver callbacks are present. The large border size is139808.140625 and matches the independent scalar conversion of8,388,488au at60au/pixel. Both axes and padded/unpadded cases agree.

This is stronger evidence than the earlier flex-only residual, but still does not trace actual frame integers, matrices or clipping. The test input139808.125px, native candidate size8,388,488au and observed scalar are consistent; inverse uniqueness of all possible native states is not asserted. The exponent-boundary counterexample is not in that browser capsule.

## Source/native admission frontier

`SOURCE-MAPPING.md` retains the complete caller path and open providers. In particular:

- Actual frame size, selected boxes/continuations, table captions, accumulated matrix, zoom/device scale, SVG handling, and clipping are not derived here. A no-CSS-transform declaration alone is not a proof that the native accumulated matrix is identity.
- The native harness begins with already selected root-relative scalar coordinates, converted by the real scalar helper. Supplying the observed start directly has the same scalar operations as a suitable simple translation case, but does not prove the actual `TransformAndClipBounds` execution produces it.
- The Lean grid formula does not prove the binary64 constant/multiply implementation equals ideal rational grid rounding for every nscoord. The finite rational oracle models those operations separately. Likewise a complete formal IEEE32 encoding/rounding theorem is not supplied for `narrow`.
- Integer endpoint additions must fit signed32; finite native cases satisfy this. General frame arithmetic and clipped/negative/NaN rectangles remain outside the exact-edge theorem. Nonnegative width makes right equal the start-plus-width branch. The actual accessor is executed in native cases.
- The checker pins executable files. Lean's installed standard library, the compiler's SDK/resources and Python's standard library remain external trusted installations, not hermetically copied inputs.

## Original goal disposition

F8 actual returned frame/position correspondence remains a provider obligation. F9 overflow geometry and F10 scroll offset/extent observers are distinct from DOMRect and remain governed by their original contracts. This component identifies and characterizes an additional CSSOM rectangle observation boundary; it does not replace exact reachability with approximate geometry, prove all overflow is reachable, or close the full safe-origin companion.

Current primary sources: [CSSOM View element rectangles](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects) and [Geometry Interfaces DOMRectReadOnly](https://drafts.csswg.org/geometry/#DOMRectReadOnly), verified20October2026. They specify box geometry and edge accessors; this artifact does not infer a universal implementation tolerance or a whole-CSS numeric model from them.

## Replay

Authenticate `FILES.json` against the externally supplied SHA before running:

```
python3 -I -S check.py --files-sha256 EXTERNAL_SHA --output NEW_EXTERNAL_DIRECTORY
```

Outputs include exact audit/axiom reports, rejected false claims, extracted C++ sources, nine-field native traces, independently computed expected rows and semantic-control differences. Generated executable files are removed only after each successful recorded run. Canonical/relocated receipts and bounded integrity challenges are retained separately from this immutable source capsule.
