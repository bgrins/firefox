# Relative stepped operations at a zero basis

One common premature-evaluation workstream, with no fix ID or acceptance. Source inspection preceded the release probe and this formal witness. Root's explicit Firefox158 run found9 zero-basis discrepancies (mod/rem/nearest round across em/rem/cqw),45 matching rows, and all54 resolved-pixel/literal/unit calibrations matching. The original saved raw evidence is separately pinned; this proposal has not been built or run.

## Candidate

The one Rust source change requires canonical values for both leaf operands before attempting Round or ModRem simplification. Unknown or nonleaf operands remain as operation nodes. This leaves the shared coefficient-level try_op unchanged: unit-preserving addition and multiplication legitimately use it. Once contextual conversion supplies resolved operands, the existing operation path can evaluate the zero divisor/step and propagate NaN through the enclosing calculation.

This conservative guard also defers nested inputs not yet leaves. It does not claim maximal simplification, performance neutrality, or a proof of the canonical_value provider contract. It preserves numeric scalar evaluation rules and existing accepted arithmetic repairs. For Round it runs before the special-value shortcuts; this overlaps and subsumes the separately held infinite-value/contextual-step guard at that knowledge boundary. Do not count or land those as unrelated repairs without reconciling the overlap.

## Integration prerequisites

Not independently landable yet. Deferring formerly folded relative expressions can expose unresolved integer counts in steps() and other consumers. Accepted subgrid work exists, but contextual easing publication/invalidation and generic WAAPI easing context remain incomplete. The six-source keyframe prototype is groundwork, not an activated prerequisite. No grammar guard is removed here. A concrete source-shaped boundary is steps(calc(1 + sign(mod(3em, 2em))), end): the current stepped fold feeds a relative leaf to the held Sign fold, producing a constant count; deferring the stepped operation exposes an unresolved count to the retained steps guard. This admission-regression prediction has not been run. Actual build and paired broad cross-consumer tests must establish preservation, and any standalone export must retain required accepted arithmetic fixes or prove they are unnecessary.

The WPT has18 operation/unit cases, each using the exact standalone probe's three-state capture. Nine cases expose the stepped-operation failure and nine preserve division/cancellation/zero-product behavior. All snapshots are collected before assertions; support or calibration failure is a test failure, not a skipped success. The fixture has not run.

## Formal scope

Stepped.lean models positive integer-basis mod/rem and nearest rounding for coefficients3/2; Option.none represents NaN, and the outer bias is added before top-level NaN censorship. It proves a zero-basis counterexample for every nonzero outer bias, kernel-checks192 nonzero calibration combinations, checks the three-state recovery, and states the explicit known-basis scheduling contract. Two false controls reject the wrong zero result and unknown-as-known scheduling.

This is exact natural-number arithmetic, not arbitrary floating-point or Rust refinement. The nearest-round formula is valid for these positive inputs and upward ties; signed zero, negative values, overflow, infinities, arbitrary CSS domains and general unit conversion remain outside it. The model's known basis is only a manual abstraction of native canonical operands. No Lean discovery credit or canonical-library coverage increase is claimed.

## Validation

See CHECK.json and lean-replay/RESULT.json. No live source/index/epoch/build/browser changes. All compilation scratch is private and removed. The first author driver wrongly expected every proof to be axiom-free; LEAN-PREPARATION-1 preserves that failed driver check. The final audit allows exactly standard propext for two general proofs and no axioms for the three kernel/rfl checks.

Replay:

    python3 artifacts/css-relative-stepped-zero-repair-proposal-v1/replay-lean.py --output /private/tmp/css-stepped-proof-review-unique

The output directory must be fresh.
