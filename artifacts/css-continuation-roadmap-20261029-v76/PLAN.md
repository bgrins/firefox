# CSS verification plan of record

The combined duration and compositor repair passes broader validation, and the reduced regression test now distinguishes the duration-only candidate from the combined repair. Native acceptance remains **149 fixes across 150 tracked IDs**; held ID 120 is excluded. No duration fix has been accepted or committed yet.

| Reduced WPT arm | Actual result |
| --- | --- |
| Original application | 2 PASS / one OK; 68662/634d07/0 |
| Duration change alone | 2 FAIL / one OK; 46219/d97e6b/1 |
| Duration plus compositor repair | 2 PASS / one OK, within broader run 15747/d43598/0 |

The duration-only failures reproduce the stale composed fonts: 22.85px instead of 22px and 0px instead of 12px after the fixed 2000ms override. The fixture checks literal calibration first. Both failures occur at the override font assertion after timing checks; this does not imply that every later override assertion ran. The inherited assessor's error text mentions 32 callbacks, but this experiment contains exactly two. The failed owner receipt remains a failure; successful replay/restoration does not relabel it.

| Work | Evidence and next action |
| --- | --- |
| Broader repair validation | 50 normative/reactivation callbacks and two reduced callbacks PASS; infinite-duration reftest PASS; restyles preserve 162 PASS and eight expected FAIL. Root verification 11257/3cfa9f/0 and independent frozen replay 825b5e/0. |
| Reduced-test discrimination | Complete. Root verification 12971/3b5293/0 preserves the actual negative result and independently verifies restoration. Frozen replay cb788e/0 confirms the exact two font failures. |
| Native landing candidate | Seven-file patch: three native changes and four focused WPTs, with five original failures repaired across 11 focused callbacks. Source/fixture bytes match tested captures. Keep research in its preceding commit. Installation and native acceptance remain pending. |
| Scheduling boundary validation | The source audit identifies a conditional automatic timeline wakeup after changed timing, but that does not cover every producer of pending work. Test an acyclic timing chain and property-only changes under an unchanged script-owned duration before landing. No starvation counterexample has been demonstrated. |
| New diagnostic probes | Rem-based two-hop and property-only probes are prepared with literal/ordinary controls and post-capture records. First/intermediate samples survive passing results. They have not run in a browser. A stronger inherited-font/explicit-line-height chain is being prepared to avoid broad root-rem invalidation. |
| Formal verification | Dispatch-attempt model: six audits/five false controls. Queue bookkeeping companion: 13 audits/six false controls. These preserve documented conditional and finite scope, not native liveness, delivery, composition or complete CSS refinement. Canonical Lean coverage is unchanged. |
| Research publication | A fresh signed checkpoint is being prepared using the reviewed temporary-index protocol. The earlier V69 1Password failure is retained; no unsigned fallback. This roadmap records the state before that new attempt. |
| Min/max and logarithm repairs | Individual, combined and provider-free comparisons remain complete. Publish preceding research and each separate native/WPT repair after signing and admission checks. |
| Bloom and canonical CSS library | Bloom milestones 1–6 remain complete within documented bounds. Canonical Lean HEAD and coverage remain unchanged. |

Both completed comparisons restored original sources and application contents. Their verified temporary backups were removed, 1,008,605,176 bytes per run. After matching-only restoration, HEAD remains `ecfe313d582a335c04d80bfd360fd3a591defdb7`; epoch is `d6d794c8b544e791805ef374036fa570f262c5ef7696a993aa2ebe4704ffc513`, and raw index observation is `26587b94c1f15c92a7ab67c06fb394f80a4cb1185d525d57e4e0824d54982975`. Only the recorded raw-index observation changed in each reconciliation. No owned experiment process or transition lock remains.

The worktree retains the unfinished custom-properties provider and the known prototypes. This branch-level validation includes documented prior fixes; it is not a clean-upstream or provider-free duration comparison. A passing diagnostic probe will not establish native liveness: style getters may flush, and the rem-based variant may trigger broader invalidation. Full first/passive records must be inspected separately from the bounded assertion verdict.

Evidence:

- [Broader trial](../css-contextual-duration-restyle-tristate-broader-runtime-1/ROOT-TERMINAL.json) and [matching-only trial](../css-contextual-duration-reduced-queue-matching-only-runtime-1/ROOT-TERMINAL.json).
- [Matching-only replay and failures](../css-contextual-duration-reduced-queue-matching-only-runtime-1/ROOT-REPLAY.json), [verified backup removal](../css-contextual-duration-reduced-queue-matching-only-runtime-1/ROOT-BACKUP-CLEANUP.json), and [state reconciliation](../css-contextual-duration-reduced-queue-matching-only-root-refresh.json).
- [Seven-file landing patch](../css-contextual-duration-landing-package-v2/landing.patch) and [prerequisites](../css-contextual-duration-landing-package-v2/PREREQUISITES.md).
- [Scheduling progress audit](../css-contextual-duration-pending-progress-audit-v1/README.md) and [exact branch applicability](../css-contextual-duration-pending-progress-branch-join-v1/README.md).
- [Two-hop diagnostic](../css-contextual-duration-acyclic-two-hop-probe-v2/README.md) and [property-only diagnostic](../css-contextual-duration-property-only-wakeup-probe-v2/README.md).
- [Fresh worktree audit](AUDIT.json), [branch work table](WORK-TABLE.md), and [individual accepted commits](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).
- [Previous roadmap](../css-continuation-roadmap-20261029-v75/PLAN.md).
