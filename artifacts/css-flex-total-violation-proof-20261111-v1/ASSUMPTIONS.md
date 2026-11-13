# Scope and remaining assumptions

The immutable V2 target describes one acquired min/max clamp and sign-selection pass. The input list is the current unfrozen subset of a valid31-bit-capacity array, with signed32 pre-clamp sizes, nonnegative ordered effective bounds and fresh violation flags. Every signed64 subtraction and sum range is derived; no final/prefix-fit premise is added.

This is not a proof of native acquisition, memory validity, compiler correspondence or complete iterative sizing. In particular upstream `SetMainSize(MainSize()+nscoord(sizeDelta.ToMinMaxClamped()))` contains a narrow addition before the modeled input exists. Its definedness is not established by receiving an int32 `before`. Floating-point distribution, min/max acquisition and all original caller/provider obligations remain open.

The native final-iteration fallback can freeze unmatched records. The model describes intended sign selection. Exact whole-helper correspondence requires the final flag false or caller-history/count invariants making fallback unreachable. Nonempty progress supports a future remaining-count induction, but does not alone prove that caller invariant. Native flags are cleared only for surviving unfrozen records; already frozen records are skipped.

`oldFold` models both checked subtraction and checked accumulation. A mathematical rejection is not native rejection or a statement about compiler overflow policy. `wrap32` and four wrong models are explicit mathematical mutations; the controls do not claim compiled native bugs or machine-code disproofs.

`Cases.lean` imports only the frozen Target and proves both witnesses by direct kernel reasoning/calculation, independently of the universal proof. The substitution witness has every running total fitting32 while its third difference does not. Negative, mixed-zero, repeated-identity and empty cases demonstrate admitted domains. FinalFallbackItems records the selection boundary, not a refined native execution.

Only the standard logical axioms propext, Classical.choice and Quot.sound are allowed by the final checker. No native_decide, custom axiom, sorry or trusted evaluator is introduced. Current browser evidence is supporting predecessor context, not a proof premise. No native/WPT/canonical/Git files are modified.
