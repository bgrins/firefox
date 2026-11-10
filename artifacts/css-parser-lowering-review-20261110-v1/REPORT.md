# Independent ParserIR lowering source review

Verdict: no blocking source-level finding. The artifact proves a useful reusable lowering theorem, rather than merely comparing a handful of examples or calling the source interpreter as an oracle. It does not mechanically derive a parser from CSS prose. The reviewed MAPPING.md and verification flags make that distinction accurately.

This review reads the Lean definitions/proofs, mappings and checker, authenticates the 36 inputs named by verification/report.json, and checks the 19 preserved module hashes. It does not independently execute Lean or attest to the author's source-only replay; root owns that gate. The retained author receipt reports 229 theorem audits, 18 new declarations, 28 observations, six type-correct semantic mutants and three input-drift controls. Its new lowering theorem's reported axiom dependency is propext; the number-instance relations also use the standard Quot.sound/Classical.choice dependencies listed in the receipt.

## The theorem's useful strength

`CssParserLowering.lowering_correct` quantifies over every typed Parser shape and every State:

    run (lower parser) state = observed state (ParserIR.run parser state)

`observed` maps success to the exact returned value and exact final State, and maps failure to `(none, originalState)`. Thus this is complete-value and complete-modeled-state equality on success, together with a proved atomic-failure policy. “Complete state” here means both fields of this model: remaining `List Char` and Boolean error flag. It does not mean every field or diagnostic effect of a native CSS parser.

The failure clause is an explicit strengthening: the source interpreter returns `none` and exposes no final state on failure. Its missing state cannot itself justify rollback. The target proof supplies that obligation using transactions. `observable_lowering` subsequently erases the backend failure state and recovers the original Option interface; that corollary alone would be weaker and would not catch a backend that leaked failed input consumption or error changes. The main theorem does catch them.

| Constructor | Source review |
| --- | --- |
| take | The backend may consume a mismatching character, but the transaction restores the full pre-read state. EOF also preserves an existing error flag. |
| scan | The scanner uses the remaining input length, not an arbitrary fixed cap. `maximal_scan` connects independently defined bounded and unbounded scans. |
| nonempty | A child returning an empty list becomes failure; the outer transaction rolls back any child error change as well as input. |
| pair / right | The outer transaction snapshots before the left parser. A failing right parser therefore rolls back successful left consumption too; success preserves value order or the right-only value. |
| optional | No redundant outer transaction is required: the induction hypothesis already proves child failure restores its input State. Wrapping the child Option turns failure into successful absence without losing state. |
| legacy | Reuses the earlier proved FirstOrder lowering under the old effect interpreter; old error-state behavior is preserved. |

Nested rollback therefore returns to the start of the failing inner operation, while retaining earlier successful outer consumption. The `nestedOptional` observation is an appropriate example of that distinction. The error-raising empty-child examples and corresponding semantic mutant test the state field most easily missed by cursor-only rollback.

## No high-level interpreter oracle

The executable `lower` clauses construct state effects, sequencing and primitive reads/scans. Neither `ParserLowering.lower` nor `ExtendedBackend.run` calls `ParserIR.run`, `CssNumberSyntax.consume`, or the number reference relation to obtain runtime answers. `executeNumber` executes `run (lower numberTree)` and then applies the unchanged numeric projection. References to source interpretation in LoweringLaws and LoweredNumber occur in theorem statements/proofs, where they belong.

This is not complete implementation independence. Both sides use `accepts`, backed by `FirstOrder.eval`, for predicate semantics; old FirstOrder lowering also shares that pure expression evaluator. Char comparison, mathematical Nat/Int arithmetic, and prior primitive/legacy semantics remain shared foundations. The proof can detect incorrect consumption, sequencing, return construction, state/error propagation and rollback; it cannot expose a common erroneous predicate definition by comparing the two implementations alone.

The target Program has ordinary Lean-function continuations and embeds the old higher-order effect program. The source AST remains typed data, but this target is not a first-order serialized machine language. There is no theorem here for a JSON codec, emitter, native compiler, allocations, stack usage, asymptotic cost or floating-point behavior.

## Number and specification boundary

`number_parts` transfers exact lexical parts, remainder and prior error. `number_execute_equal` and `number_relation` compose with the prior number bridge and its independently written `Consumed` relation. Numeric projection is unchanged ordinary Lean applied after parsing; it is not lowered by this new compiler. The mathematical representation retains explicit sign, significand and scale. Off-domain sign-only/empty examples are identified as total-model behavior; `StartsNumber` remains an explicit CSS caller obligation.

SOURCE.json pins CSS Syntax revision c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67. The byte-span/digest mapping authenticates the consume-number, digit and caller-precondition clauses. It does not prove their English meaning. `source_map.py` selects source spans and stores manually supplied interpretation strings; it is not a prose-to-ParserIR translator. CLAUSES.json explicitly marks the mapping manual and prose correspondence unproved.

The appropriate claim is: a verified, reusable lowering from an already authored typed parser model to a state-effect backend, instantiated for the manually reviewed CSS number model. It is a meaningful internal correctness edge toward a mechanical pipeline. It is not evidence that CSS prose extraction or the native Stylo implementation has been verified.

Recommendation: accept this lowering milestone subject to root's clean source-only replay. Preserve the existing mapping/projection/primitive limitations in future summaries. No source changes are requested by this review.
