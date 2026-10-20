# Hidden geometry measurement trace: independent driver review

## Decision

GO for the reversible diagnostic experiment pinned in REVIEW.json. Native acceptance remains HOLD. No browser, compiler, build, Git mutation, or production edit was performed by this review.

## Source variants

All three unified patches independently reconstruct their retained candidate snapshots exactly. Baseline adds only read-only key/measurement logging. Key-omitted removes only the containing-block key field and initializer, retaining the padding key and measurement logs. Repair retains the full key and marks the item dirty on a hidden-parent measurement miss. Its before-log now precedes AddStateBits. Getter argument types and existing FLEX_ITEM_LOG pointer conventions are consistent with the retained source; compilation remains the root experiment's gate. Logging equality is read-only. Cached/current writing-mode coherence is a source premise, not established by this horizontal fixture.

Key removal is an isolation diagnostic, not an acceptable repair of the genuine caption containing-block dependency. Dirty-on-miss has a separate limitation: a valid cached measurement followed by hidden ReflowChildren skipping placement can retain a clean item's stale position. Marking only the flex item also does not by itself admit forced layout for every clean descendant queried directly. The new shrink fixture probes descendant sizes; it does not establish arbitrary position correctness or continuation/lifetime closure.

## Driver and closure

Authenticated all 28 payload hashes, exact 25-path/source-pin roster equality, original flex snapshot binding, and byte-identical per-phase probes/runners. Both runner directory calculations resolve to the repository and common INPUTS. Each fresh-profile loopback run records executable/XUL/test/runner/INPUTS and all native sources before/after. The driver checks variant installation after build, all other native sources, runner stability and both exact configuration rosters. It requires visible-reference calibration but records observed differences without demanding a predetermined diagnostic result.

All mutation occurs inside the try/finally recovery region, with changed set before the write. Failure retains diagnostics and attempts original source restoration plus rebuild; recovery logging failure does not suppress the rebuild. Final state compares HEAD, complete index entries, cached diff and all source hashes. No Git mutation is issued. Process termination has a bounded terminate/kill sequence; browser launch failures can leave an owned profile but still propagate to native recovery. Abrupt process termination/power loss cannot be made transactional by Python finally; ordinary exceptions are covered.

The currently active separate root isolation intentionally makes live flex differ from this experiment's original. This review did not bypass the live preflight: it must pass after isolation restores the tree. Input hashes also bind the intended historical HEAD/index; a later signing change requires refreshed preflight and review pins.

## Independent validator checks

Executed only extracted validation functions, not either driver's top-level code. The retained original release result passes the 32-row/160-stage closed roster. The retained shrink release result passes the 48-row/240-stage roster and independently returns 12 differences with zero visible calibration failures. Missing row, duplicated configuration, incorrect expected geometry and nonfinite numeric payload each reject. Review.json retains these receipts and source hashes.

The release fixture's preexisting failures mean the original project/release 32-case difference alone does not establish a new upstream regression. Actual key/dirty/size traces and the key-omitted comparison are needed to distinguish strengthened-key exposure from the older hidden-layout protocol defect. Successful diagnostic execution or disappearance of one symptom does not close this causal or lifecycle question.
