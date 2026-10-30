# CSS and Stylo verification — V103

The selected-color clean original built successfully and ran 42 callbacks across three pages: 29 PASS, 13 FAIL, three OK page endings. Independent replay verified the complete results and source/application restoration. Eight failures concern identifier/color union dependencies or cyclic defaults; five concern registered images. These are failing cases, not thirteen independently established bugs. HEAD remains ecfe313d582a and the accepted native-fix count remains 149.

The selected-color proposal retains the selected AST and preserves invalid/default dependency handling. Two actual native trials have now failed before any browser execution. V3 failed E0502 at the extracted helper's mutable context boundary. V4 moved substitution inside that boundary, but its new enum omitted the real AttributeTracker lifetime and failed E0106. The isolated V4 tracker analogue missed that type detail. V5 is being prepared with separate input-borrow and tracker-context lifetimes; root read the minimal delta and verified the actual dom.rs definition against HEAD. No candidate42 browser result is claimed.

Latest owner 50372/cbc269/d0eb31 exited 1 (build exit2). Independent reviewer 46693/056f06/973d76/0 verified source/application, semantic index/staging, process cleanup and retained backup. Root rechecked source/application and inventory, removed 1,008,605,176 backup bytes and refreshed only raw-index bookkeeping. Runtime3 is frozen at 3465663e63e7afe617519fa9ca463581e6faa6b6936d33a409b78841fb739bad. Current epoch is 2c2281cf5a107db3dadf4904e17865dc24b9fc7cde4669b1815b633f234cc792. The previous failed trial is also retained; no native fix was accepted.

The clean-original42 evidence remains unchanged: owner 57577/eb6f51/d1cec3/0, independent reviewer 18962/2e16ba/4cb7ca/0, frozen runtime f061027414e062cb620a6c9bf33addcc15468871d19dc396180d66d4a95e350d. The restored application has build ID 20261029165244 and is distinct from temporary tested builds.

## Evidence and limits

- The selected-color Lean model has 15 theorem audits and seven semantic false controls. A separate default-selection model has ten audits and four false controls. They prove statements in their stated abstract models, not equivalence to Rust or full CSS coverage.
- An exhaustive three-node graph experiment covered 98,304 graph/default/root/neighbor-order combinations against an independent closure oracle. It checks the proposed cyclic-default edge placement in a bounded model, not native scheduling or arbitrary graphs.
- The 42-case matrix includes contextual registered initials as conditional preservation checks. A separate spec trace supports a tentative JavaScript registration-independence test; newer stylesheet descriptor wording remains a separate question. Neither those conditional checks nor browser agreement determines the normative answer.
- Three prepared absolute-color image unit cases remove system-color dependencies that could conceal a font-unit scheduling bug. They have not run. The separate three-case initial-independence page has now run in installed Firefox 158 and portable Chrome 156. Both accept red, CanvasText and light-dark(red, blue) without exceptions: one PASS, two tentative assertion FAILs, harness OK. Calibration, transport and owned cleanup succeeded. Independent raw/report/resource and reporter replay passed (affbe6b9). These shared outcomes do not establish a Firefox-specific interoperability bug or settle the normative discrepancy.

## Next actions

1. Finish the explicit tracker-lifetime correction, compile a fresh candidate and run the exact42 comparison. Inspect every changed failure and every previously passing case. Independently verify source, application, index, processes and backup restoration before another native experiment.
2. Run the absolute-color image unit controls against appropriate original and candidate builds. Separate false union edges from missing image dependencies using actual intermediate-patch evidence. The provisional A/B split makes B depend on A; that does not yet satisfy the requested independently cherry-pickable bug commits. An image-only alternative is under review.
3. Follow up the shared registration-initial behavior against current spec discussions before proposing a native change. Keep registration validity, conditional default preservation and later computed/used palette behavior separate. The completed installed-browser observations and independent replay are preserved.
4. Continue contextual attr work on the remaining consuming-property-context failure: selected dependency closure, request identity, SCC invalidation and session applicability. The clean animation-taint candidate previously changed 19 failures to passes (124 PASS, one FAIL, 18 OK); its lifetime/ownership semantics still need resolution before acceptance.
5. Resume signed publication when available. The last checkpoint failed with the 1Password buffer error. Validated min/max-relative-infinity and explicit-base-log changes still await preceding research and separate native+WPT commits. No unsigned fallback, push or Try run.

Bloom milestones 1–6 retain their recorded bounded completion; the standalone CSS Lean library remains partial. The latest untracked audit (V16) found exactly 563 expected paths: 53 WPT and 15 native/support files match committed recovery copies; 495 unrelated entries retain their metadata. Nothing was staged. Recovery snapshots are not finished native patches.

[Previous roadmap](../css-continuation-roadmap-20261030-v102/PLAN.md) · [Original42 evidence](../css-registered-selected-color-original-runtime-1/ROOT-SUMMARY.md) · [Corrected proposal](../css-registered-selected-color-dependency-proposal-v3/README.md) · [Branch table](../css-branch-work-readout-20261030-v4/README.md) · [Untracked audit](../css-untracked-user-recheck-20261030-v16.json).

[Failed candidate and verified restoration](../css-registered-selected-color-candidate-runtime-2/ROOT-SUMMARY.md).

[Installed registration results and independent replay](../css-registered-color-initial-independence-independent-review-v1/README.md) · [V4 borrow correction](../css-registered-selected-color-dependency-proposal-v4/README.md).

An isolated Lean extension is in progress for conditional-default closure on arbitrary finite graphs. Intended obligations are nonempty-path/cycle monotonicity, an inflationary monotone edge-enabling round, least-fixed-point containment and finite stabilization. The finite exhaustive vertex-list assumptions must remain explicit. This does not yet constitute a completed theorem set, and it does not prove equivalence to Stylo Tarjan traversal or publication of computed defaults.

[Latest failed compile and verified restoration](../css-registered-selected-color-candidate-runtime-3/ROOT-SUMMARY.md).
