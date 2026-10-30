# Clear logarithm dispatch model

The 12 new Lean theorems establish agreement between an explicit table of the two clear CSS logarithm rules and a separately written, source-shaped conditional dispatch. They also establish invalid-base precedence, unchanged delegation outside those clear cases, and observation of the two prescribed special results. This is a bounded dispatch proof, not native floating-point logarithm correctness or a resolution of specification ambiguities.

`Argument` distinguishes one from other arguments. `Base` distinguishes one, zero, negative, NaN, and other positive bases. The latter includes positive values below/above one and positive infinity; the zero class abstracts either signed zero. The model does not decode IEEE values or prove that native comparisons implement this classification. It does not retain magnitude distinctions inside each class. Each choice of a host-result function is universally quantified; no particular host result is assumed correct.

`clearRules` is a pattern-matching table: every argument at base one produces NaN, and argument one at any other positive base produces positive zero. All other combinations delegate. `source` separately expresses the proposal's ordered tests: reject base one, then return positive zero for argument one with positive base, otherwise delegate. `source_matches_clear_rules` checks every abstract argument/base combination. The evaluator is polymorphic over its result type, so its delegated result can represent arbitrary finite values as well as exceptional values; it is not confined to the five observer classes.

The delegation theorems deliberately say nothing about what zero, negative, or NaN bases should produce. The other-argument/positive-base theorem likewise leaves argument zero and infinity at bases below one entirely to the host. Those clauses prove that the proposed dispatch imposes no new answer there, not that the delegated answer conforms to CSS. Natural logarithms without an explicit base are outside this model and unchanged in the proposal.

The model imports the exact `SpecialValueObserver.lean` from the earlier sealed audit. Instantiating the evaluator with its five special values proves observation of prescribed NaN and positive zero. A separate theorem distinguishes negative-zero leakage. The observer's CSS arithmetic and opacity-clamping premises remain abstract assumptions; this does not prove browser parsing, property conversion, native resolver execution, all finite-value discrimination, or mutation invalidation.

Actual replay 9cb97a/0, inspected in 0a6c6b/0, compiled the unchanged observer and the new model, audited all 12 theorem axioms, and rejected three deliberately false claims: putting the argument-one rule before invalid-base rejection; equating negative-zero and positive-zero observations; and forcing a positive-zero result for a delegated zero-base input even when the arbitrary host supplies NaN. Only `propext` appeared. Lean version and command exit records are retained. This adds no canonical proof coverage or accepted native fix.

Replay into a fresh output directory with:

    python3 -I -S -B artifacts/css-log-clear-dispatch-model-v1/replay.py run-2

The runner pins the existing Lean executable and imported observer, compiles only in an owned temporary directory, and checks that directory was removed. No native source, index, application, build tree, or canonical state was mutated. All `.olean` targets were removed with scratch; only bounded source and logs remain.

This models the proposal in `css-log-clear-special-values-proposal-v1`, whose patch is based on accepted pow source b291d6e9. If MinMax is accepted first, the native patch must be rebased onto that accepted source, preserving its changes, before integration. The clear dispatch model is not a claim that the old patch preimage remains current.
