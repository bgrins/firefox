This model separates registered-provider defaulting from cycle classification. Lean checked 19 declarations and rejected six false claims. It reuses exact copies of the existing guard-participant and numeric-admission models; the new extension is Defaults.lean. No native source or canonical library changed.

The key result is conditional: after every actual participant has been marked, publishing a registered default preserves those marks, so each participant still obtains its own default. A fallback may run while unwinding, but it cannot erase a mark. A nonparticipant may consume the completed registered default without becoming cyclic itself.

The executable examples distinguish ordinary missing-provider fallback, selected grammar rejection, self/mutual recursion, and exhausted evaluation. In a mutual numeric example A references B and B adds one to A. Correct classification yields initials A=3/B=7. Replacing reentry with an unmarked initial produces A=4. The keyword-shaped example uses no arithmetic and yields each participant's distinct default plus a nonparticipant consumer of B=7.

The six controls reject: equivalence of early defaulting; rescue of a self-cycle by its inner fallback; poisoning every dependent; treating pending as missing; retrying a consumer fallback after a registered provider defaults; and dropping the poison-preservation premise. Every rejection is a kernel `decide` proof of falsity, not a syntax/type failure.

Replay from the repository root with an absent absolute output directory:

    python3 -I -S -B artifacts/css-registered-provider-cycle-default-model-v1/replay.py --output /private/tmp/provider-default-replay-output

The output is intentionally retained for inspection. Compiler/intermediate module scratch is independently allocated and removed. INPUTS pins Lean 4.35.0-rc4, Init and all four Lean files. REFERENCES pins predecessor models and the native research proposal. `validation-complete/CHECK.json` is the successful run; earlier draft logs record corrected keyword/import syntax errors, not successful negative controls.

This is a normalized property-only model. It does not prove native SCC/guard construction, parser correctness, registration validity, inheritance, CSS-wide keyword semantics, contextual value computation, taint/effects, cache publication, invalidation or real-number arithmetic. Nat atoms abstract admitted values; plusOne is only an admitted numeric example. Fuel exhaustion means pending and never CSS invalidity. The generic fallback theorem explicitly assumes marks survive the fallback; an executable negative control shows that premise matters. Exact guard-stack participation is reused from the existing model, not asserted as native equivalence. There is no native bug credit, accepted-fix credit or canonical spec-coverage increment.
