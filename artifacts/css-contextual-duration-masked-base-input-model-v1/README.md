# Masked base-input admission model

Source reasoning and browser discovery preceded this isolated Lean model. The completed Firefox original7 and Chrome masked records motivate a counterexample to using equality of composed animation style as a certificate that the relevant base timing input is unchanged. This package changes no native code or canonical Lean library and adds no canonical coverage.

`State` distinguishes the last input, composed view, applied duration and ownership of that duration field. `maskedView` is the observed Firefox projection: font 32px and durations [2000, 2000]ms for both authored inputs 16px and 32px. `duration` is the explicit pre-own-input interpretation of the fixed expression, font × 1000 / 16. The two witness divisions are exact. General theorems instead accept any abstract input type, composed projection and deterministic timing function; they are not floating-point or CSS evaluation proofs.

The concrete counterexample starts with input 16, applied 1000ms and the already-masked composed view. Moving to input 32 leaves the composed view equal. `composedStep` therefore skips the update and retains 1000ms while recording input 32. The theorem establishes both loss of the input distinction and the stale applied result. It does not assert that an actual native equality branch was observed.

`inputStep` admits CSS-owned updates when either the composed view or the recorded input differs. The one-step invariant and arbitrary finite-history induction prove synchronization given an initially synchronized CSS-owned state. A separate finite-history theorem preserves script-owned applied duration. The captured input must be the complete, stable input that the timing function actually uses, and old input must be recorded truthfully. The model does not prove Stylo retains such an input or propose a specific cache. Ownership acquisition/transfers and repairing arbitrarily stale initial states are outside these invariants.

The generation theorem states an alternative obligation precisely: if equal generation values guarantee equal relevant timing results, then a timing change must change generation and a generation-sensitive admission test detects it. This completeness premise is essential; the model neither implements nor authenticates a native generation counter. Missing invalidations, reset/wraparound collisions or incomplete dependency coverage can violate it. Exact input comparison supplies a different sufficient admission condition without that generation premise.

The final witness applies the input-sensitive rule to 16→32 and obtains 2000ms while keeping the composed view equal. Integer cross-products represent the exact paused-time ratios 750/1000 = 3/4 and 750/2000 = 3/8. Browser serialization/interpolation accuracy is not proved. Firefox recorded .75 at the first getter and three frames, while Chrome and the literal controls recorded .375. Chrome's initial CSS duration list is [2000, 1000], so Chrome is not being identified with the constant Firefox `maskedView` projection. Both engines initially applied 1000ms. In the final state both base and animated font are 32px, so 2000ms follows either proposed timing input; the final update mismatch does not require resolving normative initial timing policy.

Six focused declarations compile, including the one-step lemma used by the history theorem. Four separately compiled false controls reject unchanged-input certification, composed-only synchronization, constant-generation detection and overwriting a script-owned duration. Run2 audited only `propext` or no axioms; no sorryAx/custom axiom/native_decide reduction is accepted. Actual Lean session 77775, launch 200f88, terminal 231c73/0, pinned Lean 4.35.0-rc4. The first attempt failed from structure-update indentation; its exact source/logs are retained without a proof claim. Both owned scratch directories were removed, with no retained targets or dependency caches.

No theorem establishes native refinement, task transfer, traversal ordering, progress across dependency edges, same-query completion, fixed-point convergence, cyclic semantics or clean-upstream validity. The finite-history proof processes an externally supplied finite input list; it does not prove that a browser's resampling loop terminates. Typed's separate task-boundary prototype addresses a different implementation obligation and is not assumed correct by this model.

Replay in a fresh result directory:

```sh
python3 -I -S -B artifacts/css-contextual-duration-masked-base-input-model-v1/replay.py fresh-run
```

OBSERVATION-JOIN.json and REFERENCES.json authenticate both frozen records and the exact authored fixture. Their saved-only check was 472486/0. No browser, native build, Git/index or canonical mutation occurred here.
