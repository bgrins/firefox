# Correction to the frozen reload source trace

The probe files and expected values in reload-probe-v1 are unchanged. Its SOURCE-TRACE.md step 4 inaccurately described the visit_link branch for the shortest two-reference --out witness.

For that witness, --out is index 0 and its completed cyclic attribute x is index 1. The repeated x visit returns index 1. visit_link takes `next_index > index` and assigns `min(0, 1) = 0`, without checking VarInfo.var. It does not take the finished-marker skip branch in that case.

The skip branch applies when a later child references an earlier finished index, as in the shared-dependency witness. Neither branch re-traverses x or prevents the raw reload. Thus the proposed observable hypothesis and probe expectations remain unchanged; the branch-level source argument is corrected here.

VisitLinkState.lean models all three comparisons and the active-marker branch directly. It proves the larger-finished-index branch still uses lowlink, the zero-root case remains zero, an earlier finished index leaves state unchanged, a different finished index cannot set self_ref, and lowlink never increases.

This addendum preserves the original frozen source trace as historical evidence instead of silently editing it. Root was notified when this correction was found.
