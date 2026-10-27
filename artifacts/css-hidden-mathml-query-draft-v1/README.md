# Hidden MathML owner query diagnostic

Artifact-only draft: **not installed, linted or browser-executed**. No native repair or clean-child history is claimed. The sealed adjacent-provider scan remains unchanged.

## Local source binding

Six relevant committed files are copied under source/ and hashed in SOURCE-FILES.json, from explicit Git blobs at HEAD `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`. These roles do not depend on live files during the concurrent float campaign. Initial live snapshots are retained as historical metadata and happen to match all six committed blobs exactly; the final binding is to committed blobs.

Two whole files (MathML container header and frame classes) equal their indexed counterparts. The other four whole files differ; no whole-file indexed transfer is claimed. Twelve exact relevant function bodies nevertheless match the indexed bodies: MathML Reflow, ReflowChild, SaveReflowAndBoundingMetricsFor, PositionRowChildFrames, length-width sizing/RTL adjustment; style applicability/effective visibility; generic physical child reflow; frame hidden predicates and DidReflow. FUNCTION-BINDINGS.json identifies each exact excerpt.

The local size gate still does not generally exclude internal MathML containers, which lack the non-replaced-line-participant classification. The outer block/inline math roots have different frame classes. Applicability remains plausible, not runtime-proven. In particular, computed visibility would not establish the used-value or early-return branch by itself.

## Eight-case roster

CASES.json is embedded verbatim in hidden-mathml-owner-queries.html:

- internal mrow owner versus outer block-math owner;
- nested mrow-first versus mspace-leaf-first;
- visible versus hidden target owner.

There are four visible cases, two root-block hidden interaction controls and two internal-mrow hidden hypotheses. Root-block cases help identify interaction with the accepted block-line marking repair; a root-only failure is not independently localized MathML evidence.

The owner has constant RTL direction and an explicit CSS length width of 100px, changed to 60px. Its nested target contains only a fixed mspace of 40px by 16px. The source-defined RTL adjustment should move visible child placement by 40px while preserving its width. No MathML percentage-width behavior is assumed: the local adjustment explicitly has a percentage-resolution TODO.

Only the owner's non-inherited width changes; no child attribute, width or direction changes. This avoids directly changing the selected child's style, but does not prove clean native dirty bits. Parent invalidation, ReflowInput or an earlier accepted marking pass may still dirty it. Those remain decisive falsification gates.

## Measurement and failure order

Each test owns independent target and visible-peer fixtures. The sequence is warm, hide, mutate, show, restore. Show keeps the changed width so visible restoration is checked before undoing the mutation. An outside HTML wrapper query precedes each first selected query; repeated selected queries are copied immediately afterward. Only then are the visible peer and its owner measured. All rectangles are copied into arrays and retained before assertions in window.hiddenMathMLQueryResults.

All five stages' visible-peer size, explicit owner dimensions, RTL placement and outside-wrapper calibration run before any hidden-query assertion. The visible peer must show the full 40px horizontal movement. Warm/shown/restored target measurements are also calibrated first. Then hide/mutate first and repeat queries compare against the independent visible peer. Assertion messages name the exact stage and whether failure is calibration or selected-query first/repeat.

A raw WPT failure reports only the first failing assertion. The in-page copied rows do not automatically appear in a standard WPT log; do not claim later assertion outcomes or native dirty-state observations from a single failure message.

Any calibration failure stops interpretation and must be diagnosed before calling this a native bug. A differently aligned root-block control must not be silently counted as a hidden-content failure. If internal hidden cases pass, no bug has been shown by this history. If they fail while controls pass, bind the selected native frame/hidden predicate/dirty state before attributing the result to the hypothesized producer.

## Checks and execution gate

Node syntax parsing passed; it did not execute test registration or callbacks. The eight unique static case names, JavaScript extraction identity, twelve source-function identities and committed source hashes were checked. WPT lint and browser execution are deferred to root after the float campaign. No browser, native compiler/build, production source or Git mutation occurred. No disposable build target or profile was created.
