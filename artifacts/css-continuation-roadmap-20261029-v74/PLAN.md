# CSS verification plan of record

The duration candidate remains unaccepted. A paired instrumented browser comparison reproduced both fixed-duration override regressions and exposed a scheduling pattern absent from the original. Native acceptance remains **149 fixes across 150 tracked IDs**; held ID 120 is excluded. Both experiments restored their source/application state, and their verified temporary backups were removed.

| Evidence | Instrumented original | Instrumented candidate |
| --- | --- | --- |
| Actual owner terminal | 52738 / 320f89 / exit 0 | 12619 / d85f20 / exit 1 |
| Browser callbacks | 2 PASS, one OK ending | 2 FAIL, one OK ending |
| Trace | 385 events, all ten IDs, no cap or syntax/sequence errors | 887 events, all ten IDs, no cap or syntax/sequence errors |
| Bounded deferred-to-outside-coalesced intervals | 0 | 13 intervals sharing six deferred seeds |
| Fixed 2-second override | Fonts 22px and 12px; timing/composition controls pass | Effects report duration 2000ms and progress .375, but fonts remain 22.85px and 0px |
| Independent root restoration/replay | 12936 / e5fc47 / exit 0 | 65323 / 7496ff / exit 0; comparison failure preserved |

Both arms used the identical EffectCompositor diagnostic logger and ten-ID fixture. The candidate additionally installed matching.rs c3b2ddf2. The logger is temporary diagnostic code, not part of an accepted native repair. Both newly built instrumented applications report the actual ecfe313d revision; the separately restored original application retains its historical 20ab7e build identity.

The candidate intervals cover both override targets, both seek targets, and the zero-start passive/outline targets. Each bounded witness records a deferred request followed by an outside-Servo/outside-PreTraverse Layer request coalescing against the same table key, without an intervening logged post attempt, hint or removal boundary. The two override targets each have two such intervals. The baseline also has ordinary coalesced requests, but its intervening boundaries prevent this witness criterion.

This supports the pending-versus-posting hypothesis, not a complete causal or refinement proof. The logger does not record IsInStyleRefresh or align native requests to exact JavaScript phases. It also does not establish effective timing changes, actual composition, all wakeups or globally absent queued work. In particular, leaving Servo and PreTraverse does not establish a safe dispatch boundary: post-traversal tasks can execute while the broader style refresh remains active.

| Work | Current result | Next action |
| --- | --- | --- |
| Duration scheduling repair | Existing bool combines non-throttled eligibility with suppression of another post, including when the first post was deferred. The instrumented comparison distinguishes the candidate from the original. | The two-file tri-state proposal and consumer audit are complete; independent patch review is pending. Next compile/test it with the duration change, preserving eligibility, forced-throttled selection, coalescing and all three context guards. |
| Corrected protocol model | Six Lean obligations pass; five false controls are rejected; independent review is clear. An arbitrary positive blocked batch stays eligible/unattempted; a request at an explicitly safe external boundary makes one attempt, and further requests coalesce until invalidation/consumption. | Check the native representation against the model. Attempted posting is not delivery or composition; throttled entries, cancellation and attempt invalidation require native-specific obligations. |
| Regression validation | Both fixed-duration override failures reproduced under instrumentation. Earlier broader checks repaired five failures and passed 50 normative callbacks, the infinite-duration reftest and the reviewed restyle comparison. | A disabled three-source trial is being prepared against the corrected uninstrumented baseline. After changing native behavior, rerun the fixed overrides and seeks first, then the relevant broader callbacks, reftest and restyle checks. Do not drain repeatedly to an arbitrary cap or assume self-feedback converges. |
| Min/max and logarithm repairs | Individual, combined and provider-free comparisons remain complete. | Publish preceding research, then each separate native/WPT commit when signing is available. |
| Research publication | Last signed checkpoint failed in the configured 1Password signer. No unsigned fallback or new retry occurred in this experiment. | Preserve the failed receipt; use a fresh checkpoint after signing availability is established. |
| Bloom and canonical CSS library | Bloom milestones 1–6 retain their documented bounds. Canonical Lean coverage and HEAD are unchanged. | Keep isolated scheduling-model results separate from canonical coverage and native refinement claims. |

HEAD remains ecfe313d582a335c04d80bfd360fd3a591defdb7. The final epoch is 807ea08a3c1ad0c3cdd9f9e6ff17a2d7cb5920c06819202e6bcae06783eb4d47; only raw_index_observation.current changed during each post-restoration reconciliation. Final raw index is ed5f768e5548bc7c76134ac88e86d0ea1f338e730446c77cc7e76ed1366d5e6d. Staging remains empty, the held custom-properties provider is the sole tracked edit, all 563 untracked paths match the expected inventory and all 68 project prototype hashes remain unchanged. No build/browser process or source-transition lock remains from these experiments.

Evidence:

- [Original terminal](../css-contextual-duration-feedback-trace-original-runtime-1/ROOT-TERMINAL.json) and [candidate terminal](../css-contextual-duration-feedback-trace-candidate-runtime-1/ROOT-TERMINAL.json).
- [Original independent replay](../css-contextual-duration-trace-original-replay-v1/README.md) and [candidate independent replay](../css-contextual-duration-trace-candidate-replay-v1/README.md).
- [Paired trace interpretation](../css-contextual-duration-paired-trace-observation-v1/INTERPRETATION.md).
- [Corrected protocol model and limitations](../css-contextual-duration-dispatch-attempt-model-v1/README.md).
- [Uncompiled tri-state proposal and consumer audit](../css-contextual-duration-restyle-tristate-proposal-v1/README.md).
- [Source repair options](../css-contextual-duration-restyle-repair-options-v1/README.md).
- [Final canonical reconciliation](../css-contextual-duration-feedback-trace-candidate-root-refresh.json).
- [Branch work table](../css-worktree-user-audit-4te_t5ca/WORK-TABLE.md) and [individual accepted commits](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).
- [Previous roadmap](../css-continuation-roadmap-20261029-v73/PLAN.md).
