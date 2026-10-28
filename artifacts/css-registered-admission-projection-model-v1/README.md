# Admission projection contract

This isolated Lean artifact proves the local intersection contract for proposed refinement A. `project old requested bit = old bit && requested bit` retains exactly the bits present in both inputs. It cannot add a bit, and an empty old set stays empty. The bit type is arbitrary: the law does not depend on four particular units or a finite enumerated test domain.

For an explicitly fixed original directed graph, any positive-length path in an edge subset remains a path in the original graph. Consequently, restricting original edges cannot create a new positive-length cycle. Paths are inductive nonempty paths; a length-zero reflexive path is not counted as a cycle. Both results hold for arbitrary node types and arbitrary allowed-edge predicates. Unrestricted edges can be represented with an always-true allowed predicate.

The artifact includes an explicit counterexample graph: adding a self-loop to an empty graph creates a positive-length cycle. A kernel-rejected union mutant also demonstrates that replacing AND with OR can add a requested bit absent from the old set. The runner accepts this negative result only when Lean decisively proves the closed proposition false; unrelated diagnostics do not pass its gate.

This is not a theorem about the whole Stylo cascade. Provider readiness, attribute reads, fallback selection, grammar admission, and subsequent evaluation may change graph construction. No identity between those dynamically constructed graphs is assumed or established here. The cycle-subset result applies only once the original graph and edge restriction are fixed. It neither settles self-font invalidation policy nor justifies withholding required numeric scheduling work B.

Native correspondence is manual. Source pins and the exact relevant expressions are recorded in MAPPING.md. The native caller must keep the original scheduling prefilter and use AND on the original contextual flags; selected semantic flags or conservative flags are the second operand. Preserving intrinsic COLOR_SCHEME in the requested mask does not add an edge if the final operation is intersection. No theorem here proves parser equivalence, SCC cache safety, attribute/provider graph preservation, effects, DOM invalidation, Rust refinement, or bitflag encoding.

Run from the repository root with a fresh absolute output directory:

```sh
python3 artifacts/css-registered-admission-projection-model-v1/replay.py --output /private/tmp/admission-projection-replay-1
```

The runner pins Lean and Init.olean, authenticates sources and external references, compiles in an owned temporary directory, audits the six substantive declarations, and checks the decisive mutant. Only `propext` and `Quot.sound` occur; the path, cycle, and added-loop proofs use no axioms. Temporary compiled outputs are removed. Saved validation is in validation-bound/CHECK.json (tool1fd0e2 exit0; final source references authenticated). No canonical library change or coverage increment, no native acceptance, and no new bug count.
