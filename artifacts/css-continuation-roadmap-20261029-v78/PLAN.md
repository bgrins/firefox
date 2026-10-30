# CSS verification plan of record

The duration repair fixes the five new bounded failures, but **four first computed-style reads remain stale**. It is not ready for native acceptance. Accepted fixes remain **149 across 150 tracked IDs**, excluding held ID 120.

| Diagnostic | Original bounded result | Candidate bounded result | Candidate first read |
| --- | --- | --- | --- |
| rem/em chain, ordinary and animated | 2 FAIL | 2 PASS | Both stale; recover at sampled frame 2 |
| em/lh chain, ordinary and animated | 2 FAIL | 2 PASS | Both stale; recover at sampled frame 1 |
| Animated width with script-owned duration | FAIL | PASS | Correct immediately |
| Three literal controls and ordinary width control | 4 PASS | 4 PASS | Correct immediately |

Both runs retained all nine private traces and three OK page endings. Original session 84260/c64017/0 has browser exit 1; candidate session 8127/bef82f/0 has browser exit 0. The old fixtures assert later values, so their nine candidate PASS results remain valid evidence for those assertions only. Independent replay 222243/0 confirms the four stale first samples. Opacity is initially 0.428571 instead of 0.545455; property-only width is now 56px immediately instead of 28px.

These findings came from source-guided browser probes. They test a boundary the existing Lean models leave unproved: queue eligibility and dispatch-attempt bookkeeping do not establish observable style freshness. Canonical Lean coverage is unchanged. The normative first-read requirement follows the reviewed Web Animations model-liveness, dependency-ordering and CSSOM resolved-value rules for these acquired, paused, acyclic cases.

Next work, in order:

1. Use the prepared first-read assertion successors for the rem and lh chains. They add only the assertion after unchanged collection/recording; manifests and lint pass, but these exact successors have not run in a browser.
2. Implement and independently review bounded native tracing over the exact tested tri-state candidate. Distinguish Pending already present at getter entry from Pending created late during its flush; record actual flush gates and compositor consumption. Preserve JavaScript sampling. No extra drain, retry, loop or arbitrary iteration cap belongs in the diagnostic patch.
3. Run the reversible trace comparison and connect the observed sequence to the branch code before choosing a repair or extending the formal scheduling model. The confirmed PresShell gate alone does not prove which path produced the stale value. The upstream nsIContent forwarding definition remains outside the completed branch join.
4. Require immediate observable correctness as well as the prior broad controls before native acceptance. Add concise dependency-chain and property-only WPT coverage to the standalone native patch; keep tooling, research and proofs in preceding commits.
5. Publish completed research, then the separately validated min/max and logarithm repairs when signed commits work. V77 failed in 1Password; no unsigned fallback or new commit was made.

Original sources and application are restored. Root verification 13873/ca26e6/0 checked source/app/build joins, raw results and all nine records; the authenticated 1,008,605,176-byte temporary backup was removed. Only the recorded Git index observation changed. Current epoch is 563a559e97af05577b5cebdcaaccd605971202419533b5f99e29fe5cca6ac06f. The fresh audit 90920/605768/0 confirms unchanged HEAD, empty staging, the sole held custom-properties edit, and all 563 expected untracked paths. The 68 prototypes still match committed recovery; 495 unrelated files remain untouched.

Bloom milestones 1–6 remain complete within documented bounds. Canonical CSS Lean remains at 162b20fb7c53, with 11,840 audits, 12,438 cases, 173 rejected false cases and 2,155 fingerprints. No full CSS/Stylo refinement or native liveness claim is added.

[Original result](../css-contextual-duration-progress-original-runtime-1/ROOT-TERMINAL.json), [candidate result](../css-contextual-duration-progress-candidate-runtime-1/ROOT-TERMINAL.json), [candidate sample analysis](../css-contextual-duration-progress-candidate-runtime-1/RECORD-ANALYSIS.json), [specification interpretation](../css-contextual-duration-progress-original-interpretation-v1/README.md), [branch applicability](../css-contextual-duration-first-read-branch-join-v1/README.md), [trace plan](../css-contextual-duration-first-read-trace-plan-v1/README.md), [frozen trace admission](../css-contextual-duration-first-read-trace-admission-v1/README.md), [rem first-read successor](../css-contextual-duration-acyclic-two-hop-probe-v3/README.md), [lh first-read successor](../css-contextual-duration-lh-chain-probe-v2/README.md), [worktree audit](AUDIT.json), [branch table](WORK-TABLE.md), [individual fixes](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).
