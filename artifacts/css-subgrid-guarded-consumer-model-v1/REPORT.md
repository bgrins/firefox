# Guarded subgrid consumer companion

One new general Lean theorem and eight checked examples pass. This immutable companion preserves the earlier five-result model unchanged and reuses its cache invariant. It covers a proposed full-width guarded consumer, not a selected native fix, observed browser result or complete layout proof.

Let native cap c be an integer, signedMax and storage cap M be natural numbers, c≤signedMax and signedMax≤M. Let K be the capped nonnegative weighted count cache from the previous model, so K=min(M,total). Define C=c.toNat=max(0,c), compare K with C at full width, and return C−K only if K<C, otherwise0.

`guarded_transport` proves together:

- The returned natural number, embedded into Int, equals mathematical max(0,c−total).
- The return value is≤signedMax.
- On the subtraction branch, C−K is≤signedMax. Its nonnegativity follows from natural subtraction and the strict guard.

The mathematical c−total expression is unbounded Int specification arithmetic, not permission to perform that subtraction in signed32 native code. The native path first normalizes c to a nonnegative capacity and never subtracts a larger cache from it. M can exceed signedMax; the previous `signed_transport_safe` theorem is deliberately not used. Only `cache_correct` supplies K's relation to the exact total.

## Proposed source correspondence

PROSPECTIVE.patch freezes the currently proposed three-path expressions; SOURCE-CONTRACT pins their exact artifact candidate hashes. The producer uses usize saturating multiplication and saturating prefix addition; the consumer uses `std::max<int32_t>(0, mClampMaxLine)` converted to size_t, compares it to the size_t fixed count, then casts only the guarded difference to uint32. The proposal was not sealed when snapshotted, so this capsule binds exact bytes, not a final proposal manifest or acceptance.

Taking M=usize::MAX on32/64-bit and signedMax=INT32_MAX satisfies the capacity budget. A signed32 native cap has the required upper bound even when negative. The subtraction result then fits both signed32 and uint32 before its cast. The previous guarded mathematical producer is equivalent to saturation at M, but Rust's saturation implementation, source parser/domain mapping and compiler semantics remain explicit external contracts. This is not a machine-code refinement theorem.

For negative native caps, the proposed remaining count is0 and agrees with mathematical max(0,c−total). This proves only the consumer arithmetic. It does not repair negative-cap construction, abspos/implicit-origin translation, append-cap casts, fixed-repeat traversal or overall subgrid placement. Nonnegative resolved repeat counts, matching stored groups, complete producer coverage and faithful derived transfers remain required for the cache invariant. Negative boxed counts cast to usize before correct range enforcement remain outside that semantic premise.

Eight kernel-checked examples cover INT32_MIN, negative/zero capacity, the large positive count on both usize widths, maximum representable returned count, a storage cap below the actual capacity (negative control), and the old signed narrowing applied to a wide saturated cache (negative control). None executes overflowing native arithmetic or constructs a large expanded list.

## Replay

```
python3 artifacts/css-subgrid-guarded-consumer-model-v1/replay.py --output /tmp/absent-guarded-consumer-review
```

The script authenticates the prior capsule, exact copied dependency, new module, prospective patch and pinned Lean executable. It rebuilds the dependency in an owned temporary directory, checks its five prior axiom reports without crediting them again, and checks the one new report. LEAN_NUM_THREADS=2; both invocations exit0 and contain no sorryAx. Temporary .olean and source copies are removed. Retained logs/receipt are under results/.

No canonical registration, native/index edit, browser or Gecko build was performed. No duplicate theorem aliases were added.
