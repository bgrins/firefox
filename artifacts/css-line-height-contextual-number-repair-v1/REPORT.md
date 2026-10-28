# Compute contextual leaves in unitless line-height

The captured local Nightly calibration establishes a distinct computation failure: named random Number line-height and a named random Length/Length ratio produce0px and a zero-height text box, while the same-key Length expression produces a positive value. Literal2/calc2 produce20px at font10; fixed-.25 random produces15px. All nine calibration inputs are supported. This does not rely on generated random indexes and is separate from speculative-parser counter rollback. No fix ID or acceptance is assigned here.

## Cause and repair

LineHeight::to_computed_value resolves its Number calc through map_line_height_leaf. The mapper correctly handles Percentage by converting to em, and Length through resolve_line_height_length with inherited line-height/text scaling. It clones every other leaf. RandomKey::CacheKey has no context-free canonical number, so generic Random evaluation cannot extract its base; the existing error path produces NaN, subsequently normalized/clamped to0. A fixed scalar key can simplify before this path, explaining the passing .25 control. TreeCountingFunction is another contextual leaf cloned by the same mapper.

The one-file patch keeps the special Percentage/Length branches and delegates all remaining leaves to the existing Leaf::to_computed_value with the actual Context. It propagates Result through resolve_map. The shared method resolves RandomKey and TreeCountingFunction to Number and leaves absolute numeric leaves unchanged; ColorComponent remains symbolic with no origin color, as before. Existing normalization, clamping and Number storage/inheritance stay in their original owner. This is not a replacement of the special line-height length mapper with generic current-line-height conversion.

The same mapper and shared-method signature exist in the captured indexed upstream source. upstream-fix.patch applies the identical semantic change and exact WPT against that capture. Both branch and upstream exports transport exactly without offsets/fuzz, but neither has been compiled here. No provider, random-index rollback, or new API prerequisite is introduced. The source captures are authoritative for transport; no fabricated Searchfox revision or release-source equivalence is claimed.

## WPT and validation

The12-test standalone page is under css-values, where existing metadata enables random. Ten expression/control cases capture10→20→10 font mutations before asserting: literal/calc/fixed/named/stepped/sum/ratio/nested-fixed forms and Percentage/inherited-lh preservation. Named keys and fixed values avoid index-rollback dependence. Same-key length references share the random base; no assertion requires distinct samples to differ. Floating line-height/geometry comparisons tolerate one app unit plus serialization margin. Two source-grounded sibling-count/index cases check2→3→2 numeric evaluation and invalidation on actual child insertion/removal. These tree cases and the full new WPT have not run yet.

Exact branch and captured-upstream two-path forward/reverse/reapply, Rust formatting, JavaScript syntax and12 unique names passed d0c6ba/0. Test callbacks were not executed. Private scratch was removed. Counter reviewed source and fixture7ab273/5bd0e6/abf570 with no concrete blocker; native typechecking, browser comparison, invalidation and normal lint remain required.

## Limits

This fixes the missing contextual-leaf computation boundary; it is not a proof of every nested random key, percentage hint, arbitrary numeric simplification or font/zoom policy. The preexisting RandomKey::Fixed(Number) TODO for computed-node handling remains outside scope; the nested named/fixed WPT is a concrete calibration rather than a declaration that every such representation is correct. No unrelated random parser change is included. The bounded ledger search found no current entry for this mapper omission; existing keyframe tree-counting work is a different path, not evidence of standalone line-height correctness. Local Nightly evidence is not stock-release confirmation.
