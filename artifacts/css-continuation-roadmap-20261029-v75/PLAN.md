# CSS verification plan of record

The animation-duration repair now passes both targeted and broader browser comparisons. Native acceptance remains **149 fixes across 150 tracked IDs**; held ID 120 is excluded. The reduced test still needs a matching-only arm before it can establish regression coverage for the scheduling repair.

| Work | Evidence | Next action |
| --- | --- | --- |
| Duration scheduling repair | The three-source candidate built successfully and passed both fixed-duration override callbacks, including timing, composition, animation identity and literal controls. Actual run 7257/7a7e91/0; root restoration/replay 6594/d8d32b/0. | Complete reduced-test discrimination, then prepare one native/WPT commit with its preceding research. |
| Broader validation | Actual owner 15747/d43598/0 passed all 50 normative/reactivation callbacks, the infinite-duration reftest and both reduced callbacks. Restyles preserved 162 PASS and eight expected FAIL. Root replay/restoration verifier 11257/3cfa9f/0 passed. | Broader validation is complete for this exact candidate and roster. Only the already reviewed timestamp/port projections were used; no new normalization was added. |
| Reduced landing WPT | V2 passes both callbacks on the original application (68662/634d07/0) and the combined repair (15747/d43598/0). Raw replay verifies both results. | Compare the identical test against the matching-only candidate. Original and combined passing alone do not show that this reduction detects the scheduling regression. |
| Conditional dispatch model | Six Lean obligations and five rejected false controls distinguish pending eligibility from a dispatch attempt. | Keep the external safe-boundary assumption explicit; an attempt does not establish delivery or composition. |
| Queue bookkeeping model | Thirteen Lean obligations and six rejected false controls extend the model to throttling, forced visits, absence, Layer generation and arbitrary finite operation sequences. | Preserve the source mapping and its exclusions. This is a handwritten model, not native C++ refinement. |
| Min/max and logarithm repairs | Individual, combined and provider-free comparisons are complete. | Publish preceding research, then each separate native/WPT fix when signing is available. |
| Research publication | Last signed checkpoint failed in the configured 1Password signer. No unsigned fallback or new retry has occurred. | Prepare a fresh checkpoint against the final restored state; retain the failed attempt's receipt. |
| Bloom and canonical CSS library | Bloom milestones 1–6 retain their documented bounds. Canonical Lean HEAD and coverage are unchanged. | Keep these isolated scheduling proofs separate from canonical coverage and any claim of complete CSS verification. |

The repair splits the compositor's old boolean into Throttled, Pending and DispatchAttempted. Pending and DispatchAttempted remain eligible for non-throttled traversal. A pending request may retry at an external boundary only outside Servo traversal, PreTraverse and style refresh; attempted requests continue to coalesce. Forced throttled processing still selects only Throttled entries. The patch adds no repeated drain, iteration cap or self-feedback convergence rule.

The target trial's fixed 2000ms overrides now compose the expected 22px and 12px fonts; the earlier matching-only candidate reported the same effect timing while retaining 22.85px and 0px fonts. Self-dependent initial values remain measurements rather than a convergence oracle. The instrumented pair supports the scheduling hypothesis but does not prove all wakeups or native causality.

After the broader run, HEAD remains `ecfe313d582a335c04d80bfd360fd3a591defdb7`. Root independently verified source identities, original application contents, binaries, accepted payloads and staging. The only canonical update was the recorded raw Git index observation: epoch `789e4344` to `3c7e314e23a71c7c13547d9f93e03c718fe4bea17692e3104ca9c13a23a2eed1`, raw index `2278f8ff035e420179e2de37fc16bb83a509fa00f7c4d1029919009a2e109f81`. The verified 1,008,605,176-byte temporary application backup was removed. No owned build/browser process or transition lock remains.

Staging is empty and the held custom-properties provider remains the sole tracked edit. The fresh post-run audit found all 563 expected paths: 68 project prototypes matching committed recovery copies and 495 unrelated paths with unchanged metadata. The nested Lean repository has an untracked `.DS_Store`. The tests use direct font-relative durations without registered custom properties, but validation remains against this branch and its documented prerequisites; it is not a clean-upstream or provider-free comparison.

Evidence:

- [Targeted trial terminal](../css-contextual-duration-restyle-tristate-browser-runtime-1/ROOT-TERMINAL.json).
- [Reduced original terminal](../css-contextual-duration-reduced-queue-original-runtime-1/ROOT-TERMINAL.json).
- [Broader comparison](../css-contextual-duration-restyle-tristate-broader-v1/README.md) and [root activation](../css-contextual-duration-restyle-tristate-broader-root-activation.json).
- [Queue bookkeeping model](../css-contextual-duration-queue-state-model-v1/README.md) and [dispatch-attempt model](../css-contextual-duration-dispatch-attempt-model-v1/README.md).
- [Landing test plan](../css-contextual-duration-landing-test-plan-v1/README.md).
- [Fresh post-run untracked audit](AUDIT.json) and [current branch work table](WORK-TABLE.md).
- [Broader trial terminal](../css-contextual-duration-restyle-tristate-broader-runtime-1/ROOT-TERMINAL.json) and [verified state reconciliation](../css-contextual-duration-restyle-tristate-broader-root-refresh.json).
- [Individual accepted commits](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).
- [Previous roadmap](../css-continuation-roadmap-20261029-v74/PLAN.md).
