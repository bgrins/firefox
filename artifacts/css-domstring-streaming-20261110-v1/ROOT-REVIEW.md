# Root review and replay

The source-only replay passed from the 26 declared inputs: 66 audited theorems
(27 new), 32 observations, six semantic mutants and three source/library drift
controls. `ROOT-ORIGINS.json` independently authenticates nine exact normative
spans and four reference modules against their pinned origins. Temporary Lean
objects and copied replay sources were removed.

The key proof obligation is `Machine.unheld`: immediately emitted input cannot
combine with a later item. `accept_continuation` uses that obligation to establish
the continuation invariant, which lifts over individual feeds and arbitrary
finite chunk partitions. The UTF-16 and CR specializations satisfy it. Both
adapters are connected to the existing whole-input relations.

`pipe_chunks_factor` proves that the incremental implementation preserves both
carries. `pipe_finish_factor` accounts for flushing the first carry through the
second stage before flushing the second carry. `domstring_prepared_iff` then
connects the composed algorithm to `DomString.Prepared`. This includes empty
chunks and the unmatched-surrogate/CR end conditions; it does not infer general
correctness from the executable observations.

This remains a manually mapped refinement of the retained spec model. The proof
does not establish that the prose was translated correctly, validate a Firefox
input adapter, or prove memory, stack, allocation, infinite-stream, or byte
decoding properties. No native repair or additional CSS feature coverage is
counted. The separate library remains unchanged pending integration review.
