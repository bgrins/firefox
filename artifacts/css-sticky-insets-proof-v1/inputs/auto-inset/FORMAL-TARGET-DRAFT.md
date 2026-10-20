# Sticky auto-inset reduction: proposed formal contract

This is a proposed scope, not an implemented or accepted proof. The separate
logical-end-selection and nested-invalidation hypotheses remain open.

## Reference semantics

Represent each specified inset as an optional signed length. With neither
inset present, the axis has no sticky displacement. Otherwise construct a view
interval using zero for absent insets, reduce the logical end inset enough to
fit the border box, and apply movement constraints only on specified sides.
Apply containing-block constraints separately. Logical-to-physical end selection
is an explicit input, with the CSS containing-block writing-mode mapping
distinguished from the native legacy mapping.

Prove normalization fits the border box, preserves the start inset, and changes
only an insufficient end inset. Prove absent sides never introduce movement
constraints, both-absent identity, containment when feasible, idempotence and
translation covariance. Include negative insets, exact thresholds, reversed
axes, oversized boxes and empty/reversed containment intervals. Do not prove
the old and corrected formulas equivalent on the retained counterexamples.

## Native correspondence

Extract complete ComputeStickyLimits and DoComputePosition definitions, their
offset resolution and continuation consumers, and the shared scroll-range/view
timeline callers. Relate actual optional-inset sentinels, nsMargin construction,
rectangle edge operations and ordered clamps to the independent reference.
Cover finite nscoord bounds and overflow conditions explicitly; establish which
premises follow from native length/geometry providers rather than declaring all
arithmetic mathematical integers. Missing computed offsets and stored normal
positions require explicit return-path semantics.

Retain original and candidate executions, semantic mutations and fresh isolated
replay. Models of rectangle providers must identify the actual native boundary,
including frame unions, parent offsets, padding, margins and scrollport sizes.
Do not claim arbitrary layout, transformed/fragmented frames, scheduler delivery
or compositor correctness from a one-axis arithmetic theorem. Their unsolved
connections remain visible obligations in any broader sticky verification plan.

The separate end-selection issue requires all writing modes and a correct
containing-block provider. If its repair is integrated later, retain original,
auto-only, end-selection-only and combined variants so each fix is independently
reviewable. Nested-inset invalidation requires its own delivered-state theorem;
it must not be hidden in this arithmetic repair.

## Browser evidence and independent review

The corrected WPT covers 216 combinations of vertical/horizontal LTR/RTL axes,
sizes 60/80/200, absent/present/negative insets and four scroll offsets. It checks
normal geometry and actual scroll offsets before asserting the independent
constraint result. V1's two negative-zero expectation mistakes are retained;
v2 is the unchanged-test baseline/candidate pair (18 failures become passes).

Independent review must rederive the oracle, check supported reachability and
the source patch, and authenticate paired tests and packaging. Existing sticky
and shared view-timeline regressions are separate recorded gates. Browser
results from the combined worktree do not prove an isolated-base build or a
release-browser defect. Formal acceptance and a commit remain pending.
