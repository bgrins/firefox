# CSS verification plan of record

The goal remains observable CSS/Stylo bug finding, independently reviewable native/WPT commits, and a standalone formal model that can evolve with the specifications. Work stays local. There are still 149 committed accepted fixes across 150 tracked IDs; held ID 120 is excluded. HEAD remains ecfe313d582a. This iteration adds no accepted fix or canonical Lean coverage.

| Work | Completed evidence | Next step |
| --- | --- | --- |
| Min/max contextual infinity and logarithm special values | Both individual comparisons and combined 578-case comparison pass their repair gates; 33 repaired cases, 576 PASS and two preserved legacy failures; provider-free candidate has identical results | Fresh signed research checkpoint, then the two prepared standalone native/WPT commits and ledger entries |
| Animated inherited-font duration | Original has two PASS and one FAIL: CSS duration changes to 1.5s while the effect remains 1000ms/.75. One-file experimental candidate builds and all three callbacks PASS; both prior passes and ending preserved | Test guarded successor and broader regression/feedback suite before accepting or assigning a fix ID |
| Duration scheduling model | Seven audited claims and three rejected false controls; computed/applied-state distinction explains persistence after a later equality check | Preserve initial-synchronization, external-input and ownership premises; no native-refinement claim |
| Duration feedback model | Five audited claims and two rejected false controls; conditional exact 1000/1500ms two-cycle never reaches a fixed scheduling state | Retrieve real browser feedback samples with an external watchdog; the model does not establish that the engine follows this loop |
| Contextual easing | Original three-case animated-input probe fails at parsing, reproducing known feature bug 2037743; ordinary-property probe prepared; older 315-case candidate evidence retained | Lower priority than the supported-duration defect; keep unresolved keyframe-local metadata oracle separate |
| Literal negative zero | Earlier six-case observation and 16-audit model retained | Known CSSWG 7472 compatibility/spec boundary, not a new accepted bug |
| Bloom milestones and canonical library | Milestones 1–6 remain complete within their bounds; canonical library retains 11,840 audits, 12,438 cases, 173 false cases and 2,155 fingerprints | Continue scoped coverage and source/spec correspondence without claiming full CSS or compiler verification |

## New browser evidence

The supported-duration witness was found through source/spec analysis and browser testing; the Lean models subsequently formalized the stale-state mechanism and a feedback hazard. It was not an automatic discovery by a proved native verifier.

Original observation: session 85926, terminal b0ef4d, exit 0; root exact replay 46db76. Candidate experiment: session 97737, terminal 887220, exit 0; root original/candidate replay 6bcf59. The candidate build succeeded, with the existing build-progress export diagnostic still present. All three candidate callbacks pass, including ordinary mutation and script-owned updateTiming controls. The candidate is a bounded experiment, not a landable safety conclusion.

The original sources and application were restored. The verified 1,008,605,176-byte backup was removed. The raw Git index digest changed while semantic Git state stayed the same; the compact index-refresh receipt records reconciliation. No explanation of that byte change is inferred.

[Pair evidence](../css-contextual-duration-animated-input-browser-runtime-1/CANDIDATE-ROOT-REPLAY.json)
[Scheduling model](../css-contextual-duration-scheduling-model-v1/README.md)
[Feedback model](../css-contextual-duration-feedback-model-v1/README.md)

## Next execution and acceptance gates

1. Use the guarded source proposal V2, which adds the existing-or-specified CSS-animation filter while preserving inactive-but-specified eligibility. The first three-case run tested V1; V2 is not compiled or validated yet. Keep normal traversal and script ownership intact.
2. Execute fresh original/candidate normative regression observations from the captured suite. Confirm the DOM-dependent page roster in the actual browser; do not turn a predicted callback count into observed evidence. Preserve exact originally passing signatures and existing failure/ending signatures. Run the infinite-duration reftest through the reftest harness separately.
3. Use the V2 feedback overlay: all three measurement callbacks, including zero-start self-font feedback. Add transport-only capture so the recorded eight-sample JSON is retained before page teardown. Completion-only WPT PASS does not prove measured values or convergence. Maintain an external process watchdog; do not use an arbitrary retry cap as a semantic fix.
4. Run the existing restyle-count mochitest and inspect unrelated-effect/pseudo cases before accepting the scheduling change. The model assumes an exogenous fixed ancestor input; it proves no feedback convergence or native task bounds.
5. Once validated, keep the duration repair and relevant WPT coverage in one standalone native commit with preceding research. The min/max and logarithm commits are already prepared separately. Update the accepted-fix ledger only with actual signed commit IDs.

[Guarded source proposal](../css-contextual-duration-animation-only-proposal-v2/README.md)
[Regression inputs](../css-contextual-duration-regression-plan-v1/README.md)
[Feedback overlay](../css-contextual-duration-regression-plan-v2/README.md)
[Runner plan](../css-contextual-duration-regression-runner-plan-v1/README.md)
[Three-feedback-record addendum](../css-contextual-duration-regression-runner-plan-v2/README.md)

## Publication and preservation

The V68 research checkpoint passed its read-only preflight: 1,211 selected paths and full current state verified. Its signer was not run. The previous V66 attempt failed in 1Password; a pending user question asks whether signing is available. No unsigned fallback or automatic retry was used. V68 needs a fresh epoch binding after the duration experiment, and this iteration's completed research must be included in a subsequent checkpoint. Do not replay a stale binding.

[Prepared checkpoint](../css-research-checkpoint-20261029-v68/README.md)
[Preflight receipt](../css-research-checkpoint-20261029-v68/CHECK-RECEIPT.json)

The latest explicit untracked audit found the same 563 expected paths: 68 project prototypes matching committed recovery copies and 495 unrelated paths with unchanged names/metadata. The held custom-properties provider remains unfinished. The earlier 7.99 GiB cache cleanup stands; new Lean scratch directories were removed, with source and proof evidence retained. All publication, acceptance and coverage limits above remain explicit.

Current state after refresh 28390/7d4c0d/0: epoch 35b1752b613ad257ec96ccf7ff84da8152180728cdf9d4492b516abf2e88b606. Independent reconstruction confirms that only raw_index_observation.current changed from the prior epoch. Staging is empty, the 563 untracked names match the existing audit, and only the held provider remains a tracked edit.
