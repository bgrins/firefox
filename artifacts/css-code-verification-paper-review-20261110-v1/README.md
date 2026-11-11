# Code-verification paper: application to CSS work

Read on 2026-11-10. This is an adoption plan, not a verification result.

The highest-value next change is a protected challenge/solution gate for a small existing numeric correspondence theorem. The installed Lean 4.35.0-rc4 exposes `lake comparator` and `lake check`; their actual help output is retained here. The comparator requires Linux bubblewrap for its isolated build path. The local macOS help check does not establish working isolated verification.

Use the gate against deliberate transitive-definition and added-premise changes before extending it to the library. Keep approved challenge exports and configuration outside proof-worker write access. Source hashing remains useful but is not that access boundary.

For every new contract, record its admitted domain, a witness satisfying all assumptions together, and the caller-to-domain argument where native reachability is claimed. For bug demonstrations, distinguish failure to prove a theorem from a checked counterexample, and distinguish a Lean model counterexample from a native or binary execution witness.

A later machine-code pilot should use an unmodified small Rust leaf and a pinned AArch64 Linux harness. Bloom operations or numeric lexical scanning are candidates; a proof about that harness would not automatically apply to the running macOS Firefox build. Keep floating-point conversion out of the initial numeric contract.

Our structured grammar work should retain a requirement-to-theorem ledger separating source extraction, manually chosen operator semantics, normalized-token assumptions, and native behavior. No mechanism here establishes that natural-language CSS prose has been formalized correctly.

Detailed adoption order and acceptance criteria are in ASSESSMENT.json.

Sources: [paper](https://google-deepmind.github.io/code-verification/), [released artifact](https://github.com/google-deepmind/code-verification), [comparator](https://github.com/leanprover/comparator), [machine-code proof library](https://github.com/google-deepmind/code-verification/blob/main/arm64-semantics/ProofLib/README.md).
