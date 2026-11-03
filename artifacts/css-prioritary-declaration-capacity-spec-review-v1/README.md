# Declaration-capacity specification review

Reviewed on 2026-11-02. This is a bounded review of the candidate in `css-prioritary-declaration-capacity-probe-v1`, not a browser result or a claim about every CSS implementation limit.

CSS Cascade 5 defines value collection and cascading separately for each property on each element. Filtering admits declarations according to stylesheet applicability, conditions, selector matching and validity. The candidate has one valid matching `font-size: 37px` declaration for each target. Adding matching declarations for `color` supplies no competing font-size value. The expected font-size therefore remains 37px. See [value processing](https://drafts.csswg.org/css-cascade-5/#value-stages), [filtering](https://drafts.csswg.org/css-cascade-5/#filtering), and [cascading](https://drafts.csswg.org/css-cascade-5/#cascade).

CSS 2's [UA conformance requirements](https://drafts.csswg.org/css2/#conformance) require parsing valid declarations and assigning values through the cascade. They also acknowledge device limitations, exemplified by monochrome displays. That exception does not itself establish that a 16-bit declaration-link index may omit one property's valid declaration while retaining other declarations in the same stylesheet. This last judgment is an interpretation, not an explicit statement about this particular limit.

A bounded inspection found no declaration-count exception in the retrieved CSS Cascade 5 and CSS Syntax 3 documents: the rendered text search for `limit` returned no matches in either. CSS 2 contains specific limits for other subjects, such as negative margins. Absence from this search is not proof that no applicable allowance exists anywhere else in the platform specifications or CSSWG resolutions.

The practical review question remains narrower than unbounded conformance: does a parsed stylesheet within available resources lose an otherwise winning declaration solely because unrelated declarations exhaust the index? The proposed browser test checks stylesheet rule count, both targets' color, and the late font-size/width control before checking the early font-size. A timeout, crash, rejected stylesheet, or failure of those controls is not confirmation of this route.

The proposed u32 index still has a finite limit. The Lean model explicitly preserves that limitation. Neither this review nor the patch establishes correctness for arbitrarily large declaration vectors. Browser validation and native layout/cast review remain required before acceptance.

The `webspec-index` query failed with a read-only database error, so this review used the official drafts directly. Versions displayed by those pages were CSS Cascade 5 dated 2026-04-13, CSS Syntax 3 dated 2026-10-20, and CSS 2 dated 2025-12-30. No automated spec-call-chain proof was performed.
