# Registered-number admission refinement model

The executable model checks the order selected substitution → number-grammar admission → structural context-dependency collection. The final replay passes 20 audited declarations, 14 kernel examples and seven decisive negative controls. It is a proposed semantic boundary for a future implementation, not a proof that Stylo already implements that boundary.

`Admission.lean` represents a finite normalized expression grammar with number and length literals, sums and quotients. Its type checker admits number-producing length division while rejecting a bare length for a number registration. A provider can be ready, invalid or pending. Selection reads a ready provider without evaluating its fallback, uses the fallback only for invalid providers, and reports pending separately. A ready provider whose text later fails the consuming registration does not retry that var fallback.

The admitted result contains a proof that its raw expression has number type. Scheduling is collected only from that admitted expression. An em leaf creates a current-font requirement, including inside a dimension-cancelling quotient. An independent evaluator provides an actual semantic witness: the normalized expression for `calc(1em / 1px)` evaluates to the supplied current font for every natural-number font, while an expression without em leaves evaluates identically under any two fonts.

## Generalized results

The main laws quantify over arbitrary finite expressions or provider environments, rather than enumerating the eight proposed browser cases:

- Admission is sound and complete with respect to the model's dimension checker. Ready plans have passed number admission, and their scheduling flag equals the admitted expression's structural font requirement.
- Replacing an unused fallback by any other expression leaves the full plan unchanged. Invalid primaries select the fallback; pending primaries produce demand; wrong-type ready primaries fail admission without retrying fallback.
- Rejected raw expressions produce no scheduling requirement for their discarded text. Every bare length is rejected, independently of its unit and magnitude.
- Any modeled length/length quotient is number-admitted and retains the font requirements of its operands. In particular, em/px requires current-font preparation for all literal magnitudes.
- No em leaves implies evaluation is font-independent for all font pairs. The converse is deliberately not claimed: algebraic cancellation or multiplication by zero can make a structurally context-reading expression numerically constant.
- Two different source expressions/environments yielding the same selected expression have the same plan. This is a normalized selection-refinement law, not a refinement relation to Rust or CSS tokenization.
- Scheduling does not determine invalidating cycle policy. Policies that retain, defer or invalidate may share the same scheduling requirement; no numeric self-font-cycle default is proved.

The proof of policy independence is intentionally a product projection. Its value is preventing the API from treating a scheduling flag as a normative invalidation verdict; it is not a proof of any cycle algorithm. The context-independence proof is structural induction over the normalized arithmetic grammar.

## Mutants and nonvacuity

Two mutations correspond to the distinct lexical flag entry points in the captured native design:

1. `seedMutation` eagerly includes root lexical flags before admission. The generalized `seed_false_edge_general` shows a false font edge for every bare em magnitude, despite rejected number admission. This mirrors the WIP widened numeric type-mask entry path.
2. `visitorMutation` adds the lexical fallback inventory whenever a reference is visited. `visitor_false_edge_general` shows a false edge for every ready numeric provider and every fallback whose lexical inventory contains em, even though the selected numeric value requires no font. This mirrors the release-facing visitor union that bypasses the initial registration mask.

These mutants isolate the faulty decisions. They do not reproduce the complete native flag inventory, registered-value cache or Tarjan traversal. The model does not claim a bit-for-bit simulation of either function.

Seven false propositions are each separately rejected by Lean's kernel-backed `decide` tactic: agreement of each mutation with the admitted schedule; removing every number font dependency with a type mask; scanning selected tokens before admission; retrying a fallback after wrong-type ready-primary admission fails; treating pending as invalid; and deriving a cycle policy from scheduling. The runner requires the precise false-proposition diagnostic and rejects unrelated compiler errors, stuck reduction and extra diagnostics. Five diagnostic-gate controls exercise this distinction. Positive examples include ready, rejected and pending outcomes, used/unused math fallbacks, arithmetic grammar failures, and both 20→30 font results.

## Boundaries and implementation obligations

The raw grammar is a strict finite subset, not the CSS parser. It omits arbitrary token streams, dynamic computed custom-property names, DOM reads, typed attributes, namespace resolution, URL/attr taint, arbitrary math functions, percentages, multiple registration alternatives and multipliers, numeric overflow/ranges and non-finite values. Its dimension algebra only represents number and length; it cannot establish correctness of general exponent cancellation. The natural-number evaluator is an illustrative nonnegative integer fragment, not CSS floating-point arithmetic. General division by zero inherits natural-number behavior and is not offered as a CSS oracle; the current-font semantic witness uses a denominator of one.

Provider readiness is supplied by the environment. There is no recursive unresolved token graph, cycle participant poisoning, effectful evaluation or production completion scheduler in this model. It therefore cannot authorize treating an unresolved SCC member as an invalid provider. The earlier guarded-cycle model and native design's settled-provider precondition remain necessary, independent obligations.

An invalid plan describes failed registration admission, not complete invalid-at-computed-value handling. The browser's registered initial value, inheritance, CSS-wide keywords and the consumer's computed value are outside the model. No theorem here alone proves the expected 3px initial-value result. The pinned normative trace supplies the eight browser oracles and leaves numeric self-font defaulting explicitly underspecified. No additional spec interpretation is introduced by this model.

To connect this artifact to Stylo, a later proof or reviewed implementation must establish that selected tokens match the normalized selection semantics; real registration parsing matches admission; the real specified numeric AST's required-context collector is complete; pending requests are preserved; and preparation effects and publication remain correctly ordered around SCC settlement. The model does not implement the cache extraction, AST collector or native fix.

## Reproduction and provenance

Run from the repository root with a fresh absolute output directory:

```
python3 -I -S -B artifacts/css-registered-number-admission-model-v1/replay.py --output /private/tmp/registered-number-admission-replay
```

The replay authenticates the pinned local Lean compiler, Init import, source files and referenced research manifests; compiles in a unique owned temporary directory with one thread; checks the audit's exact declaration set; rejects unproved/admitted source constructs; and removes compiled scratch files before returning. This is the project's existing compiler workflow. It does not pin every transitive toolchain file or constitute an independent compiler build.

The authoritative completed replay is `replay-complete/CHECK.json`. It records 20 audits using only the allowed foundational `propext` axiom where needed; no theorem depends on `sorryAx` or a user-declared axiom. All 14 examples and seven negatives use `decide +kernel`, not native evaluation. The first draft had a tactic case-split error in `ready_requires_admission`; `replay.log` preserves that failed draft. A subsequent 19-declaration replay passed before the structural evaluation-independence theorem was added; its redundant outputs were removed, and the final full replay covers all current source bytes.

No browser, build, live native source, epoch, Git, canonical library or ledger was changed. Owned compile scratch was removed. Normative coverage credit and accepted-bug credit are both zero.
