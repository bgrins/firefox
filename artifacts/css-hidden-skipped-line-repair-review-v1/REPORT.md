# Independent review: dirty marking at skipped block lines

**GO for the bounded four-variant diagnostic; HOLD native acceptance until candidate runtime and boundary review.** No local source or iterator blocker found. The proposal is a narrow producer change, not proof of every hidden descendant's readiness.

Authenticated the producer FILES `7a4b9fd862582abb6593c08451f74c60ff354c2883492579f22b188b31338a8f` and every payload. Removing precisely the three added lines recovers the complete original `ReflowLine` byte-for-byte. Patch SHA is `a8e3d1eddf98b5bfbc825e431a71ab6cbbcec09b871ddcf42f59652e5046de7a`. This review performed no compiler/browser/build/Git operation and changed no shared source.

## Local control and data structure

`ReflowLine` asserts a nonempty line, clears its line flags, then returns early when the first child is hidden by its in-flow parent and the owning block does not have `NS_FRAME_OWNS_ANON_BOXES`. The patch marks every child subtree inside that existing return. The hidden predicate, anonymous-owner exception, ClearDirty ordering, return value and all actual block/inline reflow paths remain identical. The Boolean return still reports the same existing line result; marking does not turn the branch into an error/reflow-complete assertion.

`ChildFrames()` is explicitly intended for range iteration while the sibling chain stays unchanged. `begin()` takes `GetChildCount()` and `mFirstChild`; increment decrements the remaining count and follows the next sibling only while another child remains. This is a counted line slice, not traversal of all following block siblings. It remains valid under the preexisting well-formed nonempty line and stable frame/sibling lifetime invariant. MarkSubtreeDirty adds state bits and enumerates child lists; AddStateBits is a bitwise update, not a layout callback or sibling relink. The reviewed block child-list provider appends existing lists without modifying their membership. This supports the loop locally; it is not a universal proof of every virtual child-list provider.

Marking only the first frame would miss the later sibling roots of an inline line. Marking every block principal child instead would include unrelated lines. The proposed exact range is the appropriate extent for the branch that already decides to skip this entire line. A block line's single child is naturally covered without a separate special case.

## What the helper does and does not establish

A previously clean line child becomes directly dirty. Its owned descendant lists are traversed except at already-directly-dirty nodes and table-column groups. These barriers are real: an already-dirty root plus a clean leaf is not repaired merely by calling the helper. Full descendant closure requires source-produced coherence or explicit exceptions. Do not infer closure from the function name or quietly assume it in a later theorem.

All owned child lists of a traversed frame are considered, including block floats, overflow floats, pushed floats, overflow frames and ordinary container-owned lists. However, a line placeholder's out-of-flow pointer is a separate relationship, not an owned child list traversed by this helper. A float or absolute frame owned directly by the skipped parent can lie outside every marked line-child subtree. Conversely, one owned beneath a marked block child is within that child's enumeration, subject to the same dirty/group barriers. Thus neither “all OOF is covered” nor “all OOF is excluded” is accurate.

The existing OOF candidate remains a separate producer repair. This patch does not alter its call, timing, containing-block ownership or fallback sequence. Table column groups remain intentionally pruned; making their table/cell path dirty may complement the separate provider gate, but does not itself dirty each column. The pending four-phase matrix is necessary to distinguish these contributions.

## Scheduling and repeated work

MarkSubtreeDirty changes frame state; it does not independently enqueue another reflow, mark ancestor line boxes or immediately run layout. The current outer layout may finish and clear parent flags while a skipped child's dirty state remains as query-readiness evidence. The subsequent query still depends on the original ancestor-forcing/flush protocol. A forced pass that no longer satisfies the hidden-layout predicate reaches the existing actual child reflow path.

This source shape does not reveal an immediate recursive layout loop: no new synchronous reflow call was added. Repeated ordinary passes can revisit the line; already-dirty roots short-circuit the helper, while the all-root loop remains linear in line children. The first clean subtree traversal and later forced layout add work and need measurement if the candidate advances. Float recovery, line flag propagation, interrupted reflow and continuation scheduling are not proved by this source review.

## Applicability and evidence boundaries

The direct current failure is ordinary `.outer > .subject(hidden) > .item > table`, so this line seam can be reached without flex or OOF item layout. Retained TrialReflow/PrepareResizeReflow evidence distinguishes dirty line boxes from clean queried frame flags; the actual seven ordinary-block failures are compatible with that mechanism. A source-based mechanism is not a per-case runtime trace. The existing column-only trace does not log the parent line skip or table wrapper query and cannot establish that full chain.

The `NS_FRAME_OWNS_ANON_BOXES` exception is preserved; do not claim those parent categories were repaired. Current-line children are marked, not all continuation siblings in other fragments. A hidden size-contained subject is not automatically a valid fragmentation fixture. Any fragmentation control must visibly establish multiple fragments first and state what hidden containment changes before requiring an exact fragment list.

## Minimal additional discriminators

Keep the current eight independently calibrated ordinary-table cases and all 50 landing controls. The next useful additions are listed in TEST-DESIGN.md. Prioritize later-inline-sibling selection and a parent-owned float boundary. Do not silently expand the repair or suppress a failed control. Current four-phase execution can proceed with its immutable 66-case roster; these are separate follow-up diagnostics.

## Source roles

The complete retained before/candidate method and helper excerpt are producer evidence. Additional Searchfox discoveries retained here cover the counted iterator/range, AddStateBits, ChildLists, block-owned lists, hidden-parent predicate and the separate placeholder OOF accessor. They establish named source behavior, not equality of entire indexed files with the tested binary. No Lean compilation, universal provider theorem, native acceptance or new bug count is claimed.
