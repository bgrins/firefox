# Rollback commit boundary recommendation

Recommend one coherent production commit for A+B+D, with the two underlying defects explicitly listed in its description, followed by a separate C commit only after its own validation. The production commit contains exactly two Rust files and A16+B16+D48. Keep supporting tools/proofs/docs in the preceding research commit. This is a narrow exception to the requested one-commit-per-bug convention: six failing callbacks are not six bugs, and D is required preservation coverage for these repairs.

The candidate build/comparison is still owned by root. This recommendation does not claim current candidate success or add a fixed-bug count. Root reported the fresh baseline completed all 80 callbacks with 74 PASS / 6 FAIL (A1, B1, D4); that report is distinct from the retained historical evidence below.

## Why the two small historical fixes are not independent

| Unit | Retained behavior | Packaging implication |
|---|---|---|
| A alone: important-inline Layer predicate | A16 passed, B remained 15/16; later D coverage exposed four Layer-to-Layer failures | Predicate-only A lacks its necessary preservation repair. |
| B alone: do not replace cutoff on Rule | B16 passed but A worsened from 15/16 to 14/16 | Cannot land alone on the original base without a known regression. |
| A+B without accumulated Layer state | D had four failures | A/B together still need D. |
| Accumulated state without A | Four different D rows failed | State repair cannot replace the predicate correction. |
| A+B+D | Historical assigned A16+B16+D48 all passed | Smallest retained coherent candidate; fresh runtime comparison remains required. |

The current `RevertState` is shared production logic, not optional verification tooling. Its Origin/ordinary-Layer/important-inline representatives intersect prior exclusions. Both longhand and custom-property consumers use it. Rule preserves those representatives, which already implements B. D's cumulative state and B's preservation are therefore overlapping semantics in this candidate; labeling the shared state a neutral prerequisite would be inaccurate.

## Alternatives if exactly two bug commits are mandatory

1. **A dependent stack is possible in principle, but is not the retained verified boundary.** A first could implement the corrected predicate plus cumulative non-Rule cutoffs while explicitly retaining the old reset-on-Rule behavior. B second would remove that reset. This manufactures a different intermediate implementation, preserves the known B defect intentionally, and requires a new baseline/intermediate/final browser matrix and formal correspondence for the restricted first-stage behavior. The existing `exact_representative_fold` does not justify a Rule-reset intermediate. Do not present it as already validated or introduce it just to achieve a cosmetic split.
2. **Two alternatives independently applicable to the same original base cannot both be small disjoint patches here.** The B alternative must carry the prerequisite A/D corrections and their WPT coverage to avoid its known regression. An A/D alternative that uses the current coherent state already fixes B and needs the B witness too. The resulting alternatives overlap substantially; they are alternatives, not two additive landings or two independent fixes in Git history.
3. A genuinely behavior-preserving representation-only prerequisite could be authored first, but it would not remove the semantic dependency. It adds another implementation/validation boundary without making either historical partial repair safe by itself.

Do not duplicate the shared fix into successive commits, submit an empty B commit after A+B+D, or move necessary production state into a tooling commit. If the two defects need separate bug tracker records, link both to the coherent production patch and explain the interaction. Keep C's source-block identity implementation, logical/physical WPT and sixteen held inline-Rule D rows separate.

## Concrete candidate and evidence

- Candidate: `artifacts/css-rollback-cutoff-e86-rebase-v1/native.patch` (two native files plus three WPTs).
- Original A/B matrix: `artifacts/css-rollback-compound-fix-v1/ROOT-NATIVE-WPT-v1.json`.
- D interactions: `artifacts/css-layer-cutoff-composition-probe-v1/current-a-b-c-v1.jsonl` and `without-a-v1.jsonl`.
- Assigned no-C historical execution: `artifacts/css-layer-cutoff-composition-probe-v1/without-c-v1.jsonl`.
- Existing source/proof boundary review: `artifacts/css-shadow-context-order-proof-v1/cutoff-native-review-v1/REVIEW.md`.

Historical runs used the combined research worktree. Current candidate acceptance requires root's fresh 80-callback and four-page regression-control comparisons, exact source/binary binding, preservation and cleanup checks. This read-only review created only this new artifact; it did not alter native sources, tests, Git state, existing artifacts, or running processes.
