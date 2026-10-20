# Dispatch-only successor: review in progress

The early delta moves the empty-flags/layout-viewports predicate ahead of the null-output test. It adds `<false, true>` for null metadata only when those predicates hold. The four states are legacy generic, legacy common layout, wide generic and wide common layout.

Within the previously reviewed shared traversal, CommonLayout changes only position selection and stopping. Empty flags make GetPositionIgnoringScrollingAndSticky unselected and the stacking/display-port stopping clause false. Layout target makes the visual-root stopping clause false. Therefore the fourth instantiation preserves the old provider order/results on admitted ordinary calls; it does not introduce wide arithmetic to legacy callers or change the exact-result predicate.

The transformed/zoom source early branch precedes this dispatch and is unchanged. On a wide arithmetic failure, the recursive null call may now enter the common legacy specialization, but the same arguments make its provider operations equivalent to the old generic legacy path. Undefined legacy arithmetic outside the supported domains remains undefined; this is not a new recovery policy.

Required final checks: authenticate frozen roles and byte equality of loop/wrapper/headers; replay old-defined original/v2/v3/v4 behavior and full v3 exact-domain controls; independently check null calls with IgnoreScrolling, stacking/display-port flags and a visual-target zoomed ancestor. The producer is adding null-only negative dispatch mutants. More template instantiations and earlier predicate evaluation may affect code generation, code size or entry cost. No source-level argument establishes a speedup.
