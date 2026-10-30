# CSS verification plan of record

The instrumented duration experiment finished and all temporary source/application changes were restored. It confirms four stale first reads with new child work left Pending inside an admitted flush. The duration candidate is not ready for a native fix commit. Accepted fix count remains 149; held ID 120 is excluded.

| Completed evidence | Result |
| --- | --- |
| Instrumented native build | `mach build binaries -j2` succeeded; owner terminal 61350/6fb92f/0. |
| Browser comparison | Nine PASS callbacks and three OK endings under historical bounded assertions. Four first reads still return 0.428571 instead of 0.545455. |
| Strict trace/record alignment | All 258 getter positions and 204 posted CSS values match; 54 setup reads have no posted value. 9,174 events, no reported cap or scope ambiguity. |
| Independent replay | All 71 runtime files authenticated; exact strict join reproduced. Root also replayed the independent full-key witness successfully (c18962/0). |
| Four stale intervals | Entry child queue absent; initial flush admitted; middle consumption marker precedes a new child Pending request; no matching child dispatch/hint/removal/clear before stale return. |
| Controls | Literal chains return 0.545455 immediately; all width controls return 56px immediately. |
| Restoration | Root terminal verifier 44172/bb8547/0 verified all five source preimages, application restoration and process cleanup. Verified 1,008,605,176-byte backup removed. |
| Worktree audit | Latest audit 38702/4485db/0: 563 expected untracked files, 68 prototype bytes match committed recovery, 495 unrelated metadata records unchanged, staging empty. Only held custom_properties.rs is modified. |
| Same-element original diagnostic | 55405/658b02/0: WPT exit 1, one acyclic FAIL and one observation/calibration PASS, one OK ending, both records complete. Acyclic opacity stays 0.75 while CSS duration changes to 1.375s; literal control is 0.545455. Native/app/index/controls preserved. |
| Completion model | Final Lean run 77876/8b2a30/0 checks 17 declarations and rejects seven false controls. Independent source/audit review clear; native correspondence remains unproved. |

The observed mechanism is narrower than a general animation failure: child work is generated after the last observed middle consumption within a getter's flush. Entry flush rejection does not explain these four reads. Queue removal and WillComposeStyle remain bookkeeping observations, not proof of completed value evaluation. The trace alone does not prove causality, a native pass bound, or a correct repair.

Next work, in order:

1. Compare the new same-element acyclic reproducer against the tri-state duration candidate in the next reversible build. Original-only observations are complete: contextual opacity remains stale for all four samples, the literal control passes, and the stepped feedback diagnostic terminates without observed alternation. Its cyclic endpoint remains observational while specification treatment is unresolved. The initial zero-test harness attempt is retained as a failure, not evidence.
2. Assess the now-captured exact-branch traversal and flush boundaries for a completion mechanism. A constant extra pass needs a depth-independent argument; an unrestricted drain needs a valid feedback/termination policy. Repeated element keys alone do not distinguish cyclic from acyclic cross-property dependencies. The [source analysis](../css-contextual-duration-same-query-repair-plan-v1/README.md) records the central completion seam and outstanding obligations.
3. Use the completed isolated QueueState extension to review repair proposals: its concrete evaluator proves reachable queued/in-flight coverage, a stale depth-(k+1) counterexample for every fixed k-round budget, and completion after the chain depth. The native refinement obligations and cycle policy remain open; no arbitrary native pass-count claim follows.
4. Implement and build the justified repair; run the stronger first-read fixtures, deeper chains, same-element cases and prior broad controls. Native acceptance requires immediate correctness and preserved behavior, not eventual recovery or historical PASS labels.
5. Publish completed research in a signed checkpoint, then the separately validated min/max and logarithm fixes in individual native-plus-WPT commits. The latest signing attempt failed in 1Password; it produced no commit and must not be rerun. A fresh attempt needs current state bindings. No unsigned fallback or push.

Bloom milestones 1–6 remain complete within their documented bounds. Canonical CSS Lean remains at 162b20fb7c53a0ab89b20875a965baee98fb66bb: 11,840 audits, 12,438 cases, 173 rejected false cases, 2,155 fingerprints. New completion-model work is isolated and does not increase those counts or establish full CSS/Stylo refinement.

Current restored branch HEAD: ecfe313d582a335c04d80bfd360fd3a591defdb7. Canonical epoch: 1c63d31d17f335b0988b3183da09d47e7e52cf1dc9a5eca09966582579ce45b8. The transition from the previous epoch changed only the raw-index observation, not accepted native claims.

[Work table](WORK-TABLE.md), [instrumented runtime](../css-contextual-duration-first-read-trace-browser-runtime-1/ROOT-TERMINAL.json), [strict join](../css-contextual-duration-first-read-trace-root-join-v1.json), [independent witness](../css-contextual-duration-first-read-trace-independent-review-v1/README.md), [feedback specification review](../css-contextual-duration-feedback-spec-review-v1/README.md), [completion model plan](../css-contextual-duration-first-read-completion-model-plan-v1/README.md), [untracked audit](../css-untracked-user-recheck-20261029-v2.json), [failed signing](../css-research-checkpoint-20261029-v78-root-terminal.json).

[New browser observations](../css-contextual-duration-feedback-spec-review-v1/OBSERVED.md), [checked completion model](../css-contextual-duration-first-read-completion-model-v1/README.md), [independent model review](../css-contextual-duration-first-read-completion-model-review-v1/README.md).
