# Independent v2 total-violation amendment review

Verdict: PASS for the strengthened pre-proof target. No blocker or further target change requested. V1 author/reviewer capsules remain unchanged. No correctness proof, compiler replay, native command or browser execution was performed by this reviewer.

V1 checked only accumulator prefixes. Its compatibility theorem was valid for that checked-sum abstraction, but did not establish definedness of every original int32 subtraction. Root's concrete counterexample exposes that missing distinction; the v1 review must not be promoted to full old-expression correspondence.

V2 fixes the precise issue. checkedFold checks the contribution against its selected bounds and separately checks the next accumulated sum before recursing. Both oldFold and wideFold start from zero, so the unchecked generic empty-case accumulator does not weaken either public entrypoint. Non-violating native records skip addition while the model adds zero; this is exact under the acquired domain. No valid-input premise is strengthened.

The added subtractionWitness is jointly acquired. Its deltas are−2147483647,−1,4294967295 and prefixes0,−2147483647,−2147483648,2147483647. Thus the sum-only v1 model accepts, the strengthened oldFold rejects the third subtraction, and wideFold returns2147483647. WitnessTarget now demands these outcomes. This is mathematical checked-expression admission; rejection does not claim native rejection, wrapping, undefined-behavior exploitation or a native binary counterexample.

The amendment also rejects the complementary partial fix: checking only individual deltas admits positiveWitness's2400000000 aggregate even though its32-bit prefix range fails. Independent pure-integer controls distinguish both missing-check mutants. Empty and mixed-sign safe controls remain accepted. These are review diagnostics, not Lean proofs or compiled native mutants.

The exact old-to-new comparison authenticates only the new checkedFold guard and witness definition, strengthened WitnessTarget, and the documented contract clarification. All other Model/Target bytes remain exact. PrefixTarget and DifferenceTarget together discharge both new wide checks in the future FoldTarget proof; the signed64 bound remains9223372030412324865<INT64_MAX. The seven top-level obligations, independent list sum, ordered selection, acquired premises and progress statement are preserved.

The final-iteration qualification is now explicit in CONTRACT.md. Exact whole-helper correspondence needs aIsFinalIteration=false or a caller-history/count invariant making its unmatched-item fallback unreachable. The admitted two-item example(0,1,1),(0,0,1) still selects only the first item mathematically while arbitrary finalIteration=true freezes both natively. ProgressTarget alone does not prove the full loop invariant. The model describes the intended sign selector and the current unfrozen subset, not that fallback or a complete native state transition.

The v1 native/spec/WPT review carries forward unchanged. The actual current native candidate remains SHA cc649bb12d69438bcc84f67e77dcafa25f58a574475f8235211cc6da3de9822c and the WPT bytes match v1. Per-item subtraction operands, accumulator and helper parameter remain wide before sign selection; browser evidence and abstract wrap32 witness stay separate. No native/WPT retest was necessary for this target-only amendment.

Authentication covers frozen target v1, v2 and v1 review inventories. Recorded root session22029/terminal9a9cb2 is exit0 with three definition-only modules and eight exact axiom-free target-definition audit lines. This review authenticates those retained receipts; it does not independently rerun Lean or observe their historical process cleanup. No target correctness theorem is yet supplied.

Recheck: `python3 -I -B artifacts/css-flex-total-violation-independent-review-20261111-v2/check.py`. The recipe authenticates the exact target amendment and reruns only the small integer controls. All reviewer files are isolated here; no compiled scratch was created.
