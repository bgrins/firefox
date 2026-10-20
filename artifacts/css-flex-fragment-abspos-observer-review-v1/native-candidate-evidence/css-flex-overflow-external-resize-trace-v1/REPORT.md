# External resize and column dirty propagation

The fixture changes only a sibling's width in an outer flex row. This produces actual multicol block extents160→240→160→240px with fixed inline extent200px; tall descendants stay160px. Both row and column inner-flex modes calibrate their independent absolute references. All eight baseline stages have displaced descendants; all eight instrumented candidate stages match the references.

The candidate adds the standalone final-size overflow-container retiming patch plus temporary read-only logging in the overflow helper and column reflow. Twenty-four eligible overflow helper visits all reflow; none skips. Every visit has parentDIRTY/childdirty/reflow-all true, inline-resize false, block-resize true, and relative-block-size flag false. Each logged flex parent is the exact column child just passed to MarkSubtreeDirty. Eighteen of those column children were clean before marking. The prior column's recorded NextInFlowNeedsReflow is true. This establishes an executed dirty-propagation route for this fixture instead of merely inferring it from source.

This eliminates the proposed external-sizing route as a discriminator for a clean skipped child. It does not prove all flex fragmentation entry routes mark descendants dirty, nor does it prove every skipped child retains final parent width. Source review must cover pagination, nested fragmentation and overflow-only continuation/status paths or produce another source-directed discriminator.

The instrumented helper evaluates the overflow-exceeds guard for logging only when the original short-circuit would reach it; this did not occur here. Column logs read existing branch variables and state. Logged frame identities are diagnostic process addresses, not stable identifiers. No production trace is retained in the source.

See STATE.json for build/run/restoration results. No new repair acceptance or bug count follows from this branch diagnostic. The wide cumulative arithmetic project and its full formal obligations remain separate.
