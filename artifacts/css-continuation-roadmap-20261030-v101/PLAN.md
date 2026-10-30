# CSS and Stylo verification — V101

The selected-color clean original built successfully and ran 42 callbacks across three pages: 29 PASS, 13 FAIL, three OK page endings. Independent replay verified the complete results and source/application restoration. Eight failures concern identifier/color union dependencies or cyclic defaults; five concern registered images. These are failing cases, not thirteen independently established bugs. HEAD remains ecfe313d582a and the accepted native-fix count remains 149.

The corrected proposal retains the selected parsed value, determines ColorScheme dependencies from that value, and preserves invalid-value defaults reached through dependency cycles. V3 changed only formatting from reviewed V2. Its first actual native build failed with E0502: extracting apply_substituted_value extended a borrow from the substitution map across a mutable context argument. No browser tests ran, so there is no candidate42 result yet. An input-enum correction is being reviewed to move substitution inside the helper and retain the original borrowing/allocation behavior.

Actual candidate owner 85310/e7082d/51ecf0 exited 1; build exit was 2. Independent reviewer 72917/51f609/3abddc/0 verified restoration of source bytes/identities, application, semantic index, staging and processes. Root rechecked source/application and backup inventory, then removed 1,008,605,176 backup bytes. Runtime2 is frozen at fd1e00f74639dd2364859118bf1c68135158be9df980ee9d0196c1e8a69e53f4. The current raw-only refreshed epoch is cdc3499409e08688a1dfc37ec4640b95832d5d3df9a9cdf79ee1ebf106f9596a; native acceptance remains false.

The clean-original42 evidence remains unchanged: owner 57577/eb6f51/d1cec3/0, independent reviewer 18962/2e16ba/4cb7ca/0, frozen runtime f061027414e062cb620a6c9bf33addcc15468871d19dc396180d66d4a95e350d. The restored application has build ID 20261029165244 and is distinct from temporary tested builds.

## Evidence and limits

- The selected-color Lean model has 15 theorem audits and seven semantic false controls. A separate default-selection model has ten audits and four false controls. They prove statements in their stated abstract models, not equivalence to Rust or full CSS coverage.
- An exhaustive three-node graph experiment covered 98,304 graph/default/root/neighbor-order combinations against an independent closure oracle. It checks the proposed cyclic-default edge placement in a bounded model, not native scheduling or arbitrary graphs.
- The 42-case matrix includes contextual registered initials as conditional preservation checks. A separate spec trace supports a tentative JavaScript registration-independence test; newer stylesheet descriptor wording remains a separate question. Neither those conditional checks nor browser agreement determines the normative answer.
- Three prepared absolute-color image unit cases remove system-color dependencies that could conceal a font-unit scheduling bug. They have not run. The separate three-case initial-independence page has been root-read but has not run in browsers.

## Next actions

1. Review the no-copy borrow-boundary correction, compile a fresh candidate and run the exact42 comparison. Inspect every changed failure and every previously passing case. Independently verify source, application, index, processes and backup restoration before another native experiment.
2. Run the absolute-color image unit controls against appropriate original and candidate builds. Separate false union edges from missing image dependencies using actual intermediate-patch evidence. The provisional A/B split makes B depend on A; that does not yet satisfy the requested independently cherry-pickable bug commits. An image-only alternative is under review.
3. Run the separate registration-independence page in installed Firefox and Chrome, retaining actual acceptance/exception diagnostics. Keep this distinct from invalid-default preservation and resolve spec ambiguity before proposing a native change.
4. Continue contextual attr work on the remaining consuming-property-context failure: selected dependency closure, request identity, SCC invalidation and session applicability. The clean animation-taint candidate previously changed 19 failures to passes (124 PASS, one FAIL, 18 OK); its lifetime/ownership semantics still need resolution before acceptance.
5. Resume signed publication when available. The last checkpoint failed with the 1Password buffer error. Validated min/max-relative-infinity and explicit-base-log changes still await preceding research and separate native+WPT commits. No unsigned fallback, push or Try run.

Bloom milestones 1–6 retain their recorded bounded completion; the standalone CSS Lean library remains partial. The latest untracked audit (V16) found exactly 563 expected paths: 53 WPT and 15 native/support files match committed recovery copies; 495 unrelated entries retain their metadata. Nothing was staged. Recovery snapshots are not finished native patches.

[Previous roadmap](../css-continuation-roadmap-20261030-v100/PLAN.md) · [Original42 evidence](../css-registered-selected-color-original-runtime-1/ROOT-SUMMARY.md) · [Corrected proposal](../css-registered-selected-color-dependency-proposal-v3/README.md) · [Branch table](../css-branch-work-readout-20261030-v4/README.md) · [Untracked audit](../css-untracked-user-recheck-20261030-v16.json).

[Failed candidate and verified restoration](../css-registered-selected-color-candidate-runtime-2/ROOT-SUMMARY.md).
