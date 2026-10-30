# CSS verification continuation — V86

The four-file prototype fixes the masked font-change probe while all four descendant first-read tests still fail. It built successfully; seven callbacks produced two passes and five failures, with three OK endings and complete calibrated records. The original run had one pass and six failures. The comparison failure is preserved. Independent verification confirmed restoration of all four sources and the application, and removal of the owned backup.

| Case | Original Firefox | Earlier three-source candidate | New timing candidate | Chrome 156 |
| --- | --- | --- | --- | --- |
| Masked final opacity / effect duration | .75 / 1000 ms | Not tested | .375 / 2000 ms | .375 / 2000 ms |
| Same-element acyclic opacity / effect duration | .75 / 1000 ms | .545455 / 1375 ms | .75 / 1000 ms | .75 / 1000 ms |
| Stepped self-feedback font | 32 px | 16 px | 32 px | 32 px |
| Descendant first reads, depths 1/2/4/8 | Four FAIL | Four FAIL | Four FAIL | Four PASS |

These are sampled outputs; later timing snapshots are not atomic first-getter measurements. Literal trajectories and depth initial calibrations agree across the applicable runs. Computed CSS remains distinct from applied timing: original/new Firefox reports same-element 1.375 s and feedback 1 s while Chrome reports 1 s and .5 s. The new manager changes timing selection, not CSS serialization. The tentative same-element acyclic FAIL is not an established release bug or regression. Feedback endpoints are diagnostic; no observed alternating cycle, fixed point or universal policy follows.

Masked final authored and animated font are both 32 px, so either investigated input interpretation gives 2 s. The combined trial repairs that concrete update. It does not prove which source changes are necessary, that normal unconditional admission is safe, or a complete normative first-getter call chain. The separate final-only WPT and one-line admission experiment are unexecuted.

Priority order:

1. Isolate a minimal masked update fix. Run the final-only standalone WPT and exact diagnostic with original manager/compositor plus the narrow admission experiment. Add unrelated normal-restyle, same-value update, script-owned timing/currentTime and inactive/pseudo controls; measure repeated-work cost. Do not land unconditional admission merely because final 2 s passes. Replace it with a justified selected-input snapshot/generation condition, not composed-style equality or rule-pointer guesses.
2. Implement actual descendant publication ordering. Reviewed task transfer and publication prerequisites are concrete but lack the staged driver/child continuation and exact-target compositor phase. Release all TLS/data borrows before native tasks, sample actual animation rules, publish final parent/root inputs, then release descendants. Preserve unprocessed work, transition-before-change semantics and unsupported-path handling. Do not use a guessed pass budget or unbounded queue drain.
3. Connect the input model and native implementation. Formal DAG completion assumes fixed rules, complete dependency notification and actual evaluation. Native Pending/removal/timing equality do not supply those facts. Establish selected timing inputs, generation/invalidation provenance, endpoint/composite coverage and termination for the supported family; explicitly exclude or resolve local cycles, SMIL, custom properties, layout/timeline and root-unit feedback.
4. Commit completed research with a fresh signed checkpoint, then publish the already validated min/max and logarithm native/WPT fixes separately. The V80 signing attempt failed in 1Password without creating a commit. V81 preparation must bind the verified post-trial state and completed cutoff. Existing user authorization for local commits persists; do not retry an old owner or substitute an unsigned commit.

Accepted native fixes remain 149 across 150 tracked IDs; held ID 120 and test-only repairs remain excluded. Canonical Lean counts do not include isolated experimental models. The final post-bootstrap audit confirms 563 expected untracked paths, exact committed recovery matches for all 68 project files, unchanged metadata for 495 unrelated paths, empty staging and the same held provider edit. Restored application identities and the complete saved state were rechecked. These receipts document the completed cutoff; future execution still requires fresh admission.

The missing specification tool is now installed: webspec-index 0.14.0 successfully read the pending-style section. This restores tooling availability, not the missing end-to-end normative argument. The complete first-getter trace remains INCONCLUSIVE. Exact terminals, hashes and state bindings are in [EVIDENCE.json](EVIDENCE.json) and [REFERENCES.json](REFERENCES.json).

[Full work table](WORK-TABLE.md), [exact trial comparison](../css-contextual-duration-base-timing-comparison-v1/README.md), [masked isolation](../css-contextual-duration-masked-admission-isolation-v1/README.md), [historical V85](../css-continuation-roadmap-20261030-v85/PLAN.md).
