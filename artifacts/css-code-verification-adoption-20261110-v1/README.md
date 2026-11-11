# Applying the code-verification paper to the CSS project

The assessment is in ../css-code-verification-paper-review-20261110-v1. The completed numeric-model comparator prototype and its independent replay are in ../css-lean-comparator-pilot-20261110-v1 and ../css-lean-comparator-pilot-review-20261110-v1.

## Completed

The local diagnostic gate accepts the unchanged numeric theorem and rejects three separate failures: a changed transitive digit predicate, an added impossible premise, and a forbidden axiom. Root independently replayed all 28 source inputs and 34 command outcomes; the five export hashes and semantic report matched. Six bundled checkers accepted the unchanged export. This demonstrates specification comparison and axiom checking, not isolated proof acceptance or native implementation correctness.

The official installed Lake commands refuse Darwin. The optional Linux launcher has only intercepted orchestration checks here. A protected challenge, configuration and toolchain outside proof-worker write access, followed by a real Linux isolated run, remain outstanding. No VM or cloud changes were made.

## Next acceptance gates

1. Run the official comparator on Linux against an independently protected approved challenge. Preserve the three negative controls, exact toolchain and deterministic acceptance script. Local hashes alone are not an access boundary.
2. For newly introduced invariants, retain a concrete witness satisfying all premises together. Where browser correctness is claimed, also explain how a real caller reaches those states. Keep intentional domain restrictions visible.
3. Pick a historical Bloom or lexical defect and connect a kernel-checked model counterexample to the actual old-code failure and fixed-code test. Do not label a failed proof attempt a disproof.
4. Pilot the released AArch64 proof infrastructure on one unmodified small numeric lexical routine, excluding floating-point conversion. Pin the Rust source, compiler, target, flags, wrapper and exact emitted bytes. Prove memory bounds, termination and correspondence to the reviewed lexical contract; inventory every external assumption. This would apply to the selected Linux artifact, not automatically to our macOS Firefox build.
5. Preserve a CSS requirement ledger distinguishing exact extracted source, chosen semantics, normalized input assumptions, theorem statement, native correspondence and unresolved interpretations. Review semantic amendments independently before proofs are changed.

The ongoing unordered-combinator experiment applies this last discipline: the source-derived 38-sequence oracle and nonnullable-operand restriction were frozen before implementation and independently reviewed. It does not claim the full nullable CSS combinator semantics.

## Sources and scope

- Paper: https://google-deepmind.github.io/code-verification/
- Released infrastructure: https://github.com/google-deepmind/code-verification/tree/main/arm64-semantics
- Proof-author interface: https://github.com/google-deepmind/code-verification/blob/main/arm64-semantics/ProofLib/README.md

The paper proves selected properties of libsignal compiled into a constrained command-line harness, with explicit trusted contracts. Its AArch64 process model is single-threaded and does not support Firefox's complete execution environment. Human review of formalized intent remains necessary; neither a kernel proof nor binary refinement establishes that a Lean interpretation faithfully captures CSS prose.
