# Central synthesis origin arithmetic

The proposed adjusted-group expression encodes one physical midpoint for both first and last requests. Seventeen Lean declarations compile and their axiom reports contain no `sorryAx` or custom axioms. This is an integer arithmetic model and source correspondence review, not a native overflow proof or accepted browser fix. No native, test-install, index, browser, or standalone-library changes were made.

## Source expression and two interpretations

Let `E` be the border-box block size, `s/e` the logical start/end additions for the selected box, and `T = E+s+e`. The pinned HEAD central/mathematical/middle branch computes `h = trunc(T/2) + T%2`, then `r = h-s` normally or `r = h-e` when line-inverted. It returns `r` for either source group. The logical-baseline caller decodes First directly and Last as `E-r`.

The root proposal retains this `r`, then returns `r` when the already-adjusted local group is First and `E-r` otherwise. `sourceExpression_eq` matches that expression exactly. `same_physical_point` proves both requests decode to `A = h-s` normally or `A = E+e-h` when inverted. In either orientation, the exact geometric midpoint measured from logical block-start is `(E-s+e)/2`.

The alternative `firstAnchored` preserves the old First result and complements only Last. It also makes the two requests consistent, but chooses `h-e` as the inverted physical point. For `E=100,s=10,e=30`, that point is 40 instead of 60. It cannot satisfy the physical midpoint oracle in the reviewed empty-inline-block path. This alternative remains modeled explicitly to distinguish origin consistency from correct physical placement.

The caller review establishes that the baseline branch sets logical BStart to the shared baseline coordinate minus ascent. Subsequent shared line adjustment and LogicalRect conversion do not add an inverted-line correction in vertical-lr. This source correspondence is reviewed evidence, not a Lean theorem about Gecko. It selects the origin-aware interpretation for that path; it does not establish every synthesis caller.

## Rounding

`half_error` proves `2h-T = T%2` using signed truncating quotient/remainder. Thus even totals are exact, positive odd totals round upward, and negative odd totals round downward: half rounded away from zero. `midpoint_error` proves the doubled midpoint error is `T%2` normally and its negation when inverted; its magnitude is at most one integer unit. Here an integer unit corresponds to an app unit when mapping native coordinates.

Independently rounding each endpoint as `h-s` and `h-e` is incorrect: their sum is `E + T%2`, so odd totals disagree by one app unit. The proposed complement encodes the already-selected rounded point instead. Examples include total 141 giving 71, total -141 giving -71, and inverted/noninverted points 60/61 for extent 101 and margins 10/30. Negative-total examples describe existing arithmetic policy; they do not resolve CSS semantics for inverted or overlapping margin edges.

## Independent v2 fixture review

The authenticated v2 oracle uses `left + (width + marginRight - marginLeft)/2`. This is precisely the midpoint of the physical margin edges `left-marginLeft` and `right+marginRight`. Separate First and Last assertions compare against a symmetric 20/20 reference in the same line. This catches an implementation that makes both sources agree at the wrong inverted point. Size, applied styles, empty content, one-line placement, finiteness, and repeated observations are calibrated.

Predicted physical center differences from that reference, in CSS pixels, are:

| Writing mode | Start/end margins | HEAD First | HEAD Last | Proposed First/Last |
|---|---|---:|---:|---:|
| vertical-rl | 10/30 | 0 | -20 | 0 / 0 |
| vertical-rl | 30/10 | 0 | 20 | 0 / 0 |
| vertical-lr | 10/30 | 20 | 0 | 0 / 0 |
| vertical-lr | 30/10 | -20 | 0 | 0 / 0 |
| either | 20/20 | 0 | 0 | 0 / 0 |

These are predictions: eight passing and four failing HEAD assertions, twelve proposed passes. No browser was run for this report. The even pixel fixture does not test odd app-unit rounding.

The physical midpoint oracle follows [CSS Inline 3 atomic-inline synthesis](https://drafts.csswg.org/css-inline-3/#baseline-synthesis-box); first/last preference follows [baseline-source](https://drafts.csswg.org/css-inline-3/#baseline-source). The official 14 October 2026 draft was read on 23 October 2026. It does not prescribe the app-unit tie policy proved here.

## Remaining obligations

The model uses unbounded `Int`. Correspondence requires native margin sums, total, unary negation, raw offset, and the new complement subtraction to remain representable. This does not repair existing narrow arithmetic or establish the new subtraction's complete production domain. Optional absence, provider selection, font baselines, fragmentation/skip sides, synthesis from content or padding, and other alignment-baseline values are outside this fixture review. Small fixture values are representable. Browser reproduction, isolated candidate comparison, and broader preservation remain root-owned.

`VALIDATION.json` binds the final proof, compiler, and clean 17-declaration log. `lean-attempt-1.log` records an earlier failed proof attempt and is not successful validation. `BINDINGS.json` authenticates the saved HEAD body, the immutable v2 oracle, and the exact unsealed root patch snapshot reviewed here. No native patch is proposed by this capsule.
