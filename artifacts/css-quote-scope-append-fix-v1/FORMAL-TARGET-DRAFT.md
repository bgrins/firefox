# Quote-depth invalidation target (draft)

Prove that after delivered quote recalculation, every retained quote node has
the same depth and generated string as a declarative traversal of the current
flattened tree with style-containment boundaries. Contained subtrees inherit
entry depth but do not export their internal depth changes. The reference must
not consume the implementation's cached depth or dirty decision.

Required layers: actual lazy containment-scope creation/parent-child ownership;
flat-tree quote ordering and preceding-node lookup (including empty ancestors);
all four quote operations and clamped closing at zero; first/subsequent node
calculation; initial text publication; dirty notification and delivery through
frame construction; parent-first recalculation and changed-text publication;
removal, scope destruction/reconstruction and repeated edit/flush sequences.

The append preservation theorem must distinguish a leaf list from a list with
child dependencies. Prove that a last parent-list insertion can change a child
scope's entry value, and that the candidate requests delivery in all such
cases. The conservative child-presence predicate may admit unnecessary work;
it may not exclude a reachable dependency. Keep dirty accumulation separate
from actual delivery; no current-state invariant may assume fresh cached values.

A second result should show unchanged leaf append behavior and that mutation
of a later unrelated quote does not change earlier results. Include genuine
nested containment, empty scope lists, entry-depth decrease and zero clamps,
multiple dirty edits before a flush, removal/restore and flat-tree distribution.
Strings may be parameterized by an explicit deterministic quotation provider,
but the native bridge must retain the actual Text dispatch and distinguish
explicit-pair and automatic-language branches. Locale selection correctness is
a separately identified provider contract, not a claim to fix the known language
mutation behavior or the separate display:contents language hypothesis.

Retain complete native callers/providers and independently generated reference
observations; compile actual relevant bodies, not a reimplementation of Calc.
Mutants should include the original append shortcut, ignoring grandchildren,
using stale parent depths, omitting dirty delivery, wrong preceding-node order,
forgetting zero clamps, skipping changed generated-text publication and failing
scope cleanup. Arbitrary finite model traces and bounded native/browser checks
must remain distinct. State ownership, compiler, scheduler, layout/font and
stack/resource limits explicitly. No proof or approved scope is claimed yet.
