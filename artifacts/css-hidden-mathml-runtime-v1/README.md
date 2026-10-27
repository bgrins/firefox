# Standalone MathML query comparison

Disabled draft: `ready_for_preparation=false`. No preparation, installation, lint, build, or browser execution has occurred. Root review, explicit enablement, and a new draft seal are required before preparation.

Baseline normalizes the previous 24 sources plus `nsMathMLContainerFrame.cpp` to saved HEAD `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`. All three accepted unsigned overlays and older prototypes are absent in both comparison phases. Candidate differs only by `MarkSubtreeDirty()` inside the existing hidden-in-flow-parent early return in `nsMathMLContainerFrame::Reflow`. The candidate body is `ddb46992d11db88da3e9ff116625f928b3f679bdaec82b3c823cc5c1efd44b67`; the float repair is absent.

The controller preserves and restores all 25 original writable bodies, including the working block/column/Grid overlays and older prototypes. Thirty-four primary sources are guarded. Nine additional constructor/API support files remain untouched and are authenticated through the resource inventory. Preparation compares the complete original source/native-diff/HEAD/index snapshot with the actually restored MathML trace-v3 snapshot, and projects its earlier 29 guards back to the restored standalone float comparison. Both prior campaigns must be terminal with successful restoration builds and no recovery errors. Initial binaries must equal trace-v3's recorded restored binary pins.

## Four exact cases

Only final `hidden-mathml-owner-queries.html` from `css-hidden-mathml-repair-proposal-v2` is installed and run. Its hash is `f25ee38628e0f9da1eb76d00de6fde979916020bf607f6bc28d956bfe938cc6d`. The four cases query the internal mrow or its mspace first, with visible and hidden owners. Assertions, repeated queries, visible peers, and shown/restored calibrations retain their prior semantics.

Baseline predicts two PASS and two exact known mutate-stage query failures; candidate predicts four PASS. These remain untested predictions on the normalized HEAD roles. The ordinary runner saves every raw row and message, verifies exact case order and harness completion, and stops on calibration failure. The controller records differences before rejecting unexpected outcomes. It does not weaken expectations or accept a repair automatically.

The original four root-block cases remain research/integration controls. Their hidden path can depend on the separate skipped-block repair, so this comparison does not require them to pass with that repair absent. The nine existing landing WPTs also remain read-only guards, not executed tests. A later interaction run can cover them with the accepted repairs present.

## Ownership and restoration

One temporary MathML WPT uses exclusive creation and owned removal. Both float temporary WPTs and all prior temporary paths must remain absent. The 30 historical MathML diagnostic resource/metadata pins are retained with exactly one final HTML replacement. Nine unchanged support-source pins bring the inventory to 39. Missing metadata remains explicitly absent; no preferences or expectation files change. Normal WPT lint must succeed, with no trace-console exception.

The WPT runner has one changed inventory line to include those nine supports and the two historical float-metadata absence guards. Its test execution and validation behavior are unchanged. The full exception/restoration tail is byte-identical to the standalone float controller. Four `.diff` files expose all adaptations. There is no cost phase, tracing, or new execution framework.

The exact 925 staged research paths, complete index entries, cached diff, and every staged payload remain bound to the existing boundary evidence. The controller never stages, commits, or rewrites Git state. Keep source, index, signing, build, and browser writers stopped during the comparison.

After any normalization attempt, cleanup independently restores every original, removes only the owned temporary WPT, and rebuilds originals. Final success requires source/native-diff/HEAD/index identity, all resources and support files unchanged, temporary-file absence, a zero restoration-build exit, and no recovery errors. Each actual test run records both binaries before and after testing; the restoration build restores their source role without assuming byte-identical rebuilt binaries.

After root enablement and resealing:

```
python3 -I -S -B artifacts/css-hidden-mathml-runtime-v1/prepare.py --draft-sha REVIEWED_ENABLED_DRAFT --expected-head 90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e
python3 -I -S -B artifacts/css-hidden-mathml-runtime-v1/experiment.py --inputs-sha PREPARED_INPUTS
```
