# Acquired MBP accumulator target

This target accompanies the proposed native change of `FlexLine::mTotalItemMBP` from `nscoord` to `AuCoord64`. It starts from already acquired signed-int32 item contributions. It neither derives those contributions from CSS nor treats overflowing C++ as wrapping arithmetic.

`Acquired mbp items` requires every contribution in [-2^31, 2^31−1] and at most 2^32−1 items. There is no premise that the final sum, any prefix sum, or any intermediate wide sum fits. `PrefixTarget` must derive every prefix bound and signed-int64 representability from that input domain. The extremal bounds at maximum count are −9223372034707292160 and 9223372030412324865, strictly inside signed int64.

`fold` is a source-shaped recursive left fold, initialized at zero by `oldFold`/`wideFold`. Each step first adds its contribution mathematically and returns `none` if the requested signed range is exceeded. It does not saturate, wrap, skip a contribution or restart the running total. A failed old-fold result is a failed representability check, not an execution or prediction of overflowing C++.

The public `accumulate` wrapper pairs the total with the original complete input list. Its identity/order property concerns immutable Lean input values. It is not a proof that native frames or nsTArray storage are preserved; the accumulation loop itself only returns the total.

The final `UniversalTarget` contains nine obligations:

1. Every prefix has the per-count contribution bounds and fits signed int64.
2. The wide left fold succeeds with the exact mathematical sum, preserving the complete input identity list in `accumulate`.
3. Any successful old checked-int32 result agrees with the wide result on the acquired domain.
4. The checked free-space expression equals the mathematical expression under explicit downstream range assumptions.
5. The old fold first rejects at exactly 35,792 copies of −60,000; 358 copies of −6,000,000; and four copies of −600,000,000. **Every** preceding count, including zero, must succeed with its exact product, not only the immediately preceding count.
6. Empty, positive, negative, mixed, repeated-contribution/distinct-identity and positive-free-space examples execute as specified.
7. A symbolic compensated family derives both Acquired and DownstreamFits: for every nonnegative int32 magnitude m and count n≤UINT32_MAX, n contributions −m with used-main m, inner m and zero gap sum produce wide total −m*n and free space m. DownstreamFits is concluded, not assumed, for this family.
8. Each of the three exact old first-failure counts belongs to that compensated family, with explicit acquired/wide-success/downstream/free-space conclusions.
9. Mixed and negative nonempty examples jointly establish their input domain and result; the compensated two-item example jointly establishes its domain, downstream ranges and result.

`DownstreamFits` preserves the actual widened expression order: first total MBP plus supplied gap sum, then container minus occupied space, then sequential subtraction of each supplied used main size. It requires the acquired container, gap sum and used main operands to fit int32, the occupied-space sum to fit int64, and every mathematical subtraction prefix to fit int64. This is independently stated using list sums, not by assuming executor success. It does not derive the gap sum from `SumOfGaps()` or prove that computation safe. It also does not implement grow/shrink selection, early freezing, setting the current used sizes, repeated flex iterations, min/max freezing or layout placement.

The target proves a restricted source-shaped arithmetic fact over all admitted lists, including signed and repeated/equal contributions. Allocation, frame lifetime, acquisition, compiler semantics and whole `ResolveFlexibleLengths` remain outside it. The main accumulator range is derived; the downstream range assumptions remain explicit. No changes to native, WPT, canonical or previously frozen artifacts are part of this capsule.

`draft-1` and `typecheck-1` preserve the original typed draft. Root's pre-proof review requested joint domain/result witnesses; the final target adds them without weakening or deleting any original obligation. The Model is byte-identical. No target theorem was proved in either draft.
