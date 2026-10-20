# Sticky containing-block writing mode: proposed formal contract

This is a proposed scope, not a completed proof. Retain the complete caller and
provider obligations in the auto-inset companion's FORMAL-TARGET-DRAFT.md.

Define the physical block/inline start/end mapping from the CSS Writing Modes
table, independently of Gecko bitfields. Cover all five supported writing modes
and both directions. Prove opposite-side consistency and that the mapping uses
the containing block's writing mode, including orthogonal sticky children.

Compose that mapping with view-rectangle construction and end-inset reduction.
For an undersized sticky view rectangle, only the containing block's logical end
on the affected physical axis changes. The resulting view size accommodates the
border box; originally absent insets still introduce no displacement constraint.
Preserve exact-threshold and sufficient-size inputs. Cover negative insets,
oversized boxes, reversed axes, infeasible containing-block intervals and ordered
clamping. State finite nscoord intermediate bounds explicitly.

Retain and execute complete ComputeStickyLimits and DoComputePosition, their
computed-offset/normal-position entry paths, WritingMode and nsMargin side
operations, continuation/frame-union providers, and shared scroll-range/view
timeline callers. Trace GetContainingBlock and its writing-mode provider rather
than accepting the sticky element's mode as a substituted input. Provider
geometry, frame transformations, fragmentation, scheduling and compositor work
remain named boundaries unless actually proved.

Preserve four distinct native variants: original, auto-inset only, writing-mode
only and combined. The independent source patches reconstruct and reverse each
variant. The local four-build matrix has 186,168,18,0 failures respectively across
the two unchanged WPTs'1296 cases. Model counterexamples and genuine compiled
semantic mutants must preserve this attribution. These finite browser results
are not a universal algorithm proof or clean-base builds.

The new WPT uses two present physical insets to isolate writing-mode selection
from auto normalization. Its1080 cases vary containing-block modes/directions,
three child mode/direction combinations, axis, size, signed insets and scroll.
It calibrates ordinary geometry and actual scroll positions before measuring
sticky geometry. Existing sticky and view-timeline gates are separately paired.

Independent review must audit the specification table, source patch, provider
choice, oracle and four-way evidence. Nested-inset invalidation is a separate
state-delivery problem and remains outside these two arithmetic repairs.
