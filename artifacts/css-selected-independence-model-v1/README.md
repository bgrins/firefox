# Selected-value independence contract

The pinned Lean 4.35.0-rc4 kernel checked 22 declarations and rejected six false claims. Only propext and Quot.sound appear in the axiom audit. Owned temporary olean files were removed. Admission.lean is copied exactly from the sealed prior model; its numeric no-font-leaves theorem is reused. No native refinement, canonical coverage increment or accepted bug credit is claimed.

Replay into an absent absolute directory:

```
python3 -I -S -B artifacts/css-selected-independence-model-v1/replay.py --output /private/tmp/selected-independence-replay
```

The replay pins compiler, Init import, sources and references; audits all listed theorems; and requires each false claim to fail with exactly the intended kernel decide diagnostic. Unexpected parse/type errors do not count. The retained draft-check-1 failed because congrArg₂ was unavailable; the corrected final run is check/CHECK.json.

## Model and assumptions

Value contains literals, contextual reads, nested wrappers and sequences. Computed preserves that structure. Natural-number keys denote abstract CSS-controlled inputs, not actual CSS units or colors. A literal can represent an opaque fixed identifier, including Canvas admitted as an identifier; a contextual read can represent a scheme-dependent color. That interpretation is an external premise, not a theorem about Stylo.

Each Attempt represents complete parsing of the SAME input against one syntax alternative, with either a parsed value or failure. Its inspected list separately records contextual information encountered during the attempt. Correct complete-input parsing, grammar priority and rollback are premises. There is no token parser or registration-map implementation here.

The dependency collector is a structural sufficient certificate. agreement_suffices proves by induction that agreement on its keys preserves computation. independent_stable and accepted_context_stable then derive context stability from an empty certificate. This is not a characterization of all CSS independence: cancellation, conditional/equal branches, global/device information, correlations among valid CSS environments and symbolic used-value behavior are outside the language. Equal light-dark image/color cases are explicitly not settled.

## Checked obligations

- choice_append and failed_prefix_ignored establish that failed attempts cannot contaminate the later selected result.
- dependent_selection_rejects forbids retrying a later alternative after a successful dependent parse. accepted_certificate joins the actual selected value to the dependency certificate.
- The Canvas witnesses distinguish color-first rejection from identifier-first admission. rejectInsideParse is a deliberately wrong algorithm that changes selection; contaminatedAccepts is a second mutant that leaks failed-attempt flags. Neither is claimed to be the exact native implementation.
- Nested/list theorems preserve every contextual child. The later-member witness changes computed output under two environments despite an independent first member.
- Sound is an explicit semantic certificate obligation. track_sound proves it for the actual model collector; arbitrary empty metadata is not assumed sound. erased_evidence_is_unsound supplies a counterexample.
- simplification_preserves_certificate requires unchanged evidence AND equal computation for every environment. A sampled fold can agree in one context and disagree in another, as the concrete witness shows. No claim is made that Stylo performs that sampled fold.

Six separately compiled false controls reject prefilter/selection equivalence, failed-prefix contamination acceptance, later-member independence, nested-child independence, computation equality after evidence erasure, and generalization of a sampled fold. These concrete controls complement the general inductive theorems.

## Browser probes and attribution

1. Canvas under `<color> | <custom-ident>` must reject while the reversed order admits. This detects independence rejection incorrectly placed inside alternative parsing.
2. `Canvas blue` under `<color> | <custom-ident>+` must admit: the color parse fails whole-input consumption, then the identifier list succeeds. A failed color attempt must not contaminate it. This distinct control was sent to the fixture agent.
3. `2px 1cqw` as `<length>+`, or a later transform containing 1cqw, must reject; independent px/percentage controls must admit. Existing probe-v2 already covers these families.
4. Re-register the same name with an independent value after a rejected attempt. This checks exit-before-insertion, a spec obligation outside the Outcome-only state machine.

These are proposed probes, not new browser observations. Prior API21 failures motivated the design; Lean did not automatically discover or prove native defects. No WebIDL, numeric rounding, references/cycles, taint, initial-cache effects, @property policy or source equivalence is proved.
