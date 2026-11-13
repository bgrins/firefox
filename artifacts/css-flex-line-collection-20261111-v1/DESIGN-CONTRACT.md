# Proposed signed line-collection contract

Review checkpoint only; no substantive Lean proofs or canonical changes yet.

Input: finite already ordered list of full item values `List α`, an outer hypothetical main-size function `α → Rat`, used inner main size `T : Rat`, and fixed used main-axis gap `G : Rat`. CSS-facing domain requires `0 ≤ T` and `0 ≤ G`; item sizes are unrestricted signed rationals. Preserve full values and repetitions, not just numeric sizes. Source acquisition, DOM ordering/filtering, collapse/struts, forced breaks, fragmentation, intrinsic sizing, percentages/cyclic gap resolution, native app-unit rounding and actual positions are outside this target.

For a nonempty line `L`, its span is `sum (L.map size) + G * (L.length - 1)`. Empty span is0. Gaps occur only between consecutive actual items on the same line, not at line edges. A zero-size item still has an inter-item gap. This models the minimum fixed gutter contribution used for collection, not later content-distribution extra spacing.

Executable wrapping policy:

1. Empty input returns no occupied lines. This does not claim Gecko has no internal empty FlexLine for an empty container.
2. Start a nonempty line from the first uncollected item. If that item's outer size exceeds T, immediately emit its singleton line. Do not inspect later negative sizes to rescue it.
3. Otherwise extend one item at a time while the next whole-prefix span is `≤ T`. Stop at the **first** failing extension, emit the accepted prefix and restart from the failed item.
4. No lookahead across a failed extension, even if later negative sizes would make a longer total fit. Negative prefixes are retained without zero flooring. Equality fits. All zero-gap zero-size successors fit an exactly full ordinary line. With a positive gap that extension may fail.

This is first-failure greedy collection, not the longest prefix whose final sum fits. The difference is material for signed sizes: T100, G0, [80,30,−50] must produce [[80],[30,−50]], not one line. Similarly [150,−50] gives [[150],[−50]], even though the combined span is100. Conversely [−50,150] fits as one line: the first item fits, then the complete prefix is100. There is no blanket rule forbidding a large individual item later in an already fitting line.

Independent relation `NextLine size T G input line rest` will require `input = line ++ rest`, nonempty line, and exactly one of:

- Oversized-first: line is a singleton whose size exceeds T. Remainder unconstrained by lookahead.
- Ordinary: every nonempty prefix of line has span `≤ T`, and either rest is empty or appending its first item would produce span `> T`.

`Collected` is the inductive empty/next-line relation over the exact residual list, not membership in the executable's output. This relation records stop conditions independently of execution. The mathematical operator can be total on arbitrary Rat parameters, while CSS interpretation is restricted to the stated domain.

Planned universal targets: executable iff Collected; `flatten output = input` (full item identity/order/multiplicity); all occupied lines nonempty; output line count ≤ input item count; NextLine's exact prefix/remainder and first-failure/oversized-singleton laws; deterministic relation. Termination uses finite remaining input length/structural tail recursion, with at least one item removed per emitted line, not monotonicity of signed spans. No arbitrary fuel bound or size cap.

Optional `nowrap` entrypoint returns `[input]` for nonempty input and `[]` for empty input and has the same partition/order laws. No wrapped-fit property is asserted for nowrap. Adding this does not silently choose an empty-container internal-line convention.

Planned checked examples are the16 rows in CASES.json plus an exact rational boundary (T=7/4, G=1/4, sizes[1,1/2] fit exactly), distinct item identities with equal sizes, and a third-item preservation witness after the primary singleton. False-claim controls will refute absorbing the oversized first item, looking past first failure, using `<` instead of `≤`, zero-flooring signed prefixes, dropping duplicates, and charging a gap at a line edge. These are model semantic controls, not compiled native mutants.

No `sorry`, `native_decide`, trusted evaluator or extra axiom. Use the already pinned Lean4.35.0-rc4 tool and bounded one-worker local compilation; only standard logical axioms allowed in final theorem audit. Freeze definitions/targets separately from proof outputs after this review. Existing browser data remain supporting evidence, never premises in the mathematical proof.
