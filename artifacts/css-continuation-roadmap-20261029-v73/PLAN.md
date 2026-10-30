# CSS verification plan of record

The guarded animation-duration candidate is **not ready to land**. A corrected browser comparison reproduces two regressions in script-owned fixed-duration overrides. Native acceptance remains **149 fixes across 150 tracked IDs**; held ID 120 is excluded. No candidate source remains installed.

| Work | Result | Next action |
| --- | --- | --- |
| Duration repair | Earlier broad checks repaired five failures and passed 50 normative callbacks, the infinite-duration reftest and the reviewed restyle comparison. The new baseline passes both consistency callbacks; the candidate fails both. | Revise the candidate only after investigating the missed recomposition. Rerun the fixed-override controls and the broader regression checks after a source change. |
| Fixed override regression | After `updateTiming({duration: 2000})`, current effects report progress `0.375`, but candidate fonts stay at `22.85px` and `0px`, instead of `22px` and `12px`. The baseline passes these assertions. Coupled opacity is also stale in the saved measurements; its assertion was not reached. | Instrument the pending-entry and restyle-posting decisions, final traversal boundary, pending-entry consumption and last-composed timing. |
| Scheduling evidence | Real seeks change reported timing without updating composition. Ordinary outline changes update composition. All recorded animation/effect identities remain current, and both getter orders and repeated reads agree. Literal-duration measurements remain coherent. | Test the hypothesis that an entry left pending without a posted restyle suppresses later Layer requests. The measurements do not establish that internal path. |
| Lean protocol model | Seven theorems and three intended false controls passed. The model separates pending work, posted work, traversal state and logical timing/composition versions. An independent review found no overclaim. | Establish or falsify the explicit `exitWithoutDrain` premise in native execution before claiming a refinement result. No fairness, native cause, feedback convergence or canonical coverage increment is proved here. |
| Min/max and logarithm fixes | Individual, combined and provider-free comparisons and standalone payload reviews remain complete. | Publish preceding research, then install and commit each fix with its own WPTs once signing works. |
| Research publication | V69 created no commit: 1Password returned `failed to fill whole buffer`. | Preserve the failed signing receipt; prepare a fresh signing owner after evidence of restored signing availability. No unsigned fallback or push. |

The first consistency fixture incorrectly assumed a default computed outline width of `0px`; both callbacks failed at that setup assertion after saving their observations. Its successor adds only an explicit zero-width outline. The corrected baseline actually passed, so the candidate's later fixed-override failures are not attributed to that fixture error. All failed runs remain intact.

The decisive candidate owner was `66670/684695/1`. Root independently replayed its raw results, verified original source/application restoration, and verified then removed its owned backup (`35467/4d6357/0`). The earlier feedback-only candidate also restored and removed its backup. No build, browser or signing process remains active at this checkpoint.

HEAD remains `ecfe313d582a335c04d80bfd360fd3a591defdb7`. The final bookkeeping refresh changed only `raw_index_observation.current`; epoch is `7563d82dc2ad9e452bf8e1b3eb2e6b899e5603f4ea8c8aeea0884919ed924bfb`. Staging is empty, the held custom-properties provider remains the sole tracked edit, all 563 untracked names match the inventory, and all 68 project prototype hashes remain unchanged. Bloom milestones 1–6 retain their existing documented bounds.

Evidence:

- [Comparison and measured intervention table](../css-contextual-duration-feedback-consistency-interpretation-v1/INTERPRETATION.md)
- [Corrected passing baseline](../css-contextual-duration-feedback-consistency-original-runtime-2/ROOT-TERMINAL.json)
- [Failed candidate and independent restoration](../css-contextual-duration-feedback-consistency-candidate-runtime-1/ROOT-TERMINAL.json)
- [Preserved fixture failure](../css-contextual-duration-feedback-consistency-original-runtime-1/ROOT-TERMINAL.json)
- [Native hypothesis and instrumentation points](../css-contextual-duration-feedback-pending-restyle-review-v1/README.md)
- [Lean model and limitations](../css-contextual-duration-pending-posted-model-v1/README.md)
- [Final bookkeeping and worktree audit](../css-contextual-duration-index-refresh-v6/ROOT-TERMINAL.json)
- [Full work table](../css-research-checkpoint-20261029-v69/WORK-TABLE.md)
- [Individual accepted commits](../css-pow-special-value-acceptance-publisher-v2/readout/README.md)
- [Previous checkpoint](../css-continuation-roadmap-20261029-v72/PLAN.md)
