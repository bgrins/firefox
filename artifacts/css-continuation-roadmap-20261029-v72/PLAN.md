# CSS verification plan of record

Native acceptance remains **149 fixes across 150 tracked IDs**; held ID 120 is excluded. HEAD remains `ecfe313d582a335c04d80bfd360fd3a591defdb7`. Bloom milestones 1–6 retain their previously documented bounds; this experiment adds no canonical Lean coverage or accepted fix.

| Work | Evidence | Next action |
| --- | --- | --- |
| Animation-duration update | The guarded proposal repairs five reproduced failures; all 50 normative callbacks and the infinite-duration reftest pass. The existing restyle comparison retains all 170 assertion signatures under its reviewed timestamp projection. | Hold native acceptance while investigating feedback composition. |
| Fresh feedback comparison | Original and candidate each completed three callbacks and retained three eight-sample records. Candidate owner `57530/da3880/0`; root independently replayed the raw results and verified restoration in `7399/d39f08/0`. | Use the new observations to test composition and timing consistency, rather than treating completion as convergence. |
| Composition mismatch | Candidate coupled output stays at opacity `0.428571` while its captured effect reports progress `0.5251641137855579`. Font remains `22.85px`; effect duration is `1428.125ms`. Zero-start output remains `0px` while the effect reports progress `1`. All eight samples repeat. | Check current animation membership, getter order, initial acquisition, real `751→750ms` seeking, ordinary restyle, and a script-owned `2000ms` duration against a literal-duration control. The separate observation fixture is being prepared. |
| Min/max and logarithm fixes | Individual, combined and provider-free comparisons are complete; standalone payloads and the disabled MinMax installer are reviewed. | Publish preceding research, then install and commit each native fix with its own WPTs. |
| Signed research publication | V69 failed with `1Password: failed to fill whole buffer`; no commit was created. | Await evidence that signing availability changed before preparing another signing owner. Keep V69's actual failure intact; no unsigned fallback. |

The coupled values are consistent with composition at the previous `1750ms` duration followed by a timing update. That history is a hypothesis, not an established cause. The existing fixture retains captured handles without rechecking current membership, and its getters are sequential rather than an atomic snapshot. The zero-start observation does not satisfy the positive synchronized starting-state assumptions of the Lean two-cycle model. These measurements establish neither a native loop nor a unique normative cycle policy.

The original source, browser bundle and extra build outputs were independently verified after restoration. The owned `1,008,605,176`-byte backup was removed. The successful bookkeeping refresh changed only `raw_index_observation.current`; current epoch is `f6593a502953ccbc3ebb633b82d0e3138aa1b3e96c46c9627b92ffcc1c60dfb6`. Staging is empty, the held custom-properties provider remains the only tracked edit, and all 563 untracked names remain expected. No build, browser, signer or source-transition process remains active at this checkpoint.

Evidence:

- [Fresh original terminal](../css-contextual-duration-feedback-original-runtime-2/ROOT-TERMINAL.json)
- [Candidate terminal and independent restoration](../css-contextual-duration-feedback-candidate-runtime-2/ROOT-TERMINAL.json)
- [Candidate raw assessment](../css-contextual-duration-feedback-candidate-runtime-2/feedback-wpt/ASSESSMENT.json)
- [Sampling and scheduling review](../css-contextual-duration-feedback-sampling-review-v1/README.md)
- [Self-dependency spec boundary](../css-contextual-duration-self-dependency-spec-trace-v1/TRACE.md)
- [Bookkeeping refresh](../css-contextual-duration-index-refresh-v4/ROOT-TERMINAL.json)
- [Untracked audit](../css-untracked-audit-user-followup-20261029-v5.json)
- [Full work table](../css-research-checkpoint-20261029-v69/WORK-TABLE.md)
- [Individual accepted commits](../css-pow-special-value-acceptance-publisher-v2/readout/README.md)
- [Previous plan and publication status](../css-continuation-roadmap-20261029-v71/PLAN.md)
