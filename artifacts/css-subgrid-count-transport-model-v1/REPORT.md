# Subgrid count transport: conditional capped-cache model

Five general Lean results and eight anonymous checked examples pass using Lean4.35.0-rc4 with two threads. This is research support for a possible cache strategy, not a selected native repair, browser observation, accepted fix or canonical integration. Discovery remains the source arithmetic audit. No new credit is assigned for restating aliases or registering prior theorems.

## Two capacities, not a parser-dependent layout cap

`cap` is the storage cap M; `capacity` is the actual layout line cap C, with0≤C≤M. `total` sums nonnegative count×group products for fixed entries, excluding auto-fill. An ordinary name group is represented by(1,1). The source-domain assumptions require correctly resolved nonnegative counts and matching group lists; the separate Integer range-policy repair is not silently assumed installed.

The leading strategy discussed with hidden_provider_scan is M=INT32_MAX, avoiding a duplicate10000 layout constant. This remains a proposal. The theorem uses arbitrary M and explicitly requires C≤M. A cap below C is shown to lose remaining-capacity information.

## Proved operations and sequence invariant

- `addCap_correct`: normalize the prior accumulator to min(M,a), compare b with M−bounded, and perform bounded+b only on the nonsaturating branch. The result equals min(M,a+b); the result and actually evaluated addition fit any supplied machine budget≥M. The subtraction is nonnegative because bounded≤M.
- `mulCap_correct`: handle a zero right operand first; otherwise multiply only after left≤M/right. The product on that branch fits M, and the result equals min(M,left×right). The unbounded multiplication in the specification is not an instruction that a native implementation may evaluate before the guard.
- `cache_correct`: a left-to-right recursive accumulator, with capped product and capped addition at every entry, equals min(M,initial+exact weighted total). This covers parser prefix accumulation, not merely a final clamp after an overflowing sum.
- `remaining_capacity_preserved`: for C≤M, `C−cache = C−total` as natural truncated subtraction. This is the nonnegative remaining-capacity operation max(0,C−total).
- `signed_transport_safe`: if also M≤signedMax, the stored cache is representable and signed C−cache lies in[−signedMax,signedMax]. Taking signed max with0 equals the exact natural remaining capacity, including total≫C.

These proofs do not assume a small exact total. Natural numbers represent the mathematical counts and may exceed either machine width. For machine code, inputs, capacities and divisor must already be valid machine values; guarded subtraction/division/comparison must obey their unsigned semantics, and lazy branches must prevent unguarded product/sum evaluation. Induction supplies the accumulator cap. A storage cap≤2147483647 fits both32-bit and64-bit usize, and signed subtraction is within signed32. No32-bit target or native compiler was run here.

## Fixed-prefix order and auto-fill

The pinned native expansion retains the original computed fixed-repeat count; only auto-fill uses the cached total. Equal remaining capacity implies equal `remaining−remaining%fillLen` for every common positive fillLen. With identical original entry order, group lists, fixed counts, append cap and allocation outcomes, both expansions therefore execute the same fixed iterations and the same auto-fill iterations and retain the same prefix of line-name groups. This is a conditional program correspondence argument from the proved numeric equality, not a new named theorem or a proof of all layout effects. No claim is made for empty fill lists, changed counts/order, allocation failures, unrelated implicit-name processing or other producers.

## Negative and concrete checks

Kernel-checked examples retain the source witness: total2147483647×2 narrows ordinarily to−2 and produces signed spare5 at C=3 instead of0. A universal ordinary-narrowing preservation claim is refuted. Further controls show:

- Choosing storage cap2 when C=3 changes the result.
- Three groups at INT32_MAX exceed32-bit usize.
- Applying an INT32_MAX clamp after a32-bit wrapped product is too late.
- Saturating at64-bit usizeMAX while retaining the old int32 cast gives−1 and spare4; that alternative requires a changed consumer comparison/subtraction policy.
- INT32_MAX fits both usize widths, and the capped safe witness yields spare0.

These checks use exact arithmetic, not a claim that undefined signed arithmetic was executed. No resource-heavy expansion is constructed.

## Source and replay boundary

SOURCE-PINS/EXCERPTS are copied from the corrected positive-count audit, with explicit HEAD90 hashes and the reserved-line-name correction already preserved there. They map parser product/sum, usize storage/derived transfer, positive literal admission, native fixed/auto loops and append cap. REFERENCES also binds the separate cache strategy note. Nonnegative C is not established universally: the parallel source audit is investigating abspos/implicit-origin translation and extent-wrap states. Negative native caps are outside this Nat model. A future native proposal must verify all constructors, conversions, integer-range premises, C bounds and consumers against these obligations; this capsule does not establish that refinement.

Replay to a fresh absent directory:

```
python3 artifacts/css-subgrid-count-transport-model-v1/replay.py --output /tmp/subgrid-count-review
```

The script authenticates the module/toolchain and both source capsules, invokes Lean with LEAN_NUM_THREADS=2 in an owned temporary directory, checks all five axiom reports (no sorryAx), and removes the temporary directory. It does not create a build target, .olean product or canonical registration. The successful log/receipt is retained under results/. One initial development compile needed let-reduction before splitting the addition guard; it was corrected before the successful audited run. No browser/native/index/canonical changes occurred.
