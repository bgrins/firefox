# Retained work does not schedule normal entry

The isolated child pair exposes a missing prerequisite of the existing Route worklist theorem: the normal traversal must first admit its root. Retaining descendant ancestor-font hints is not equivalent to scheduling that traversal. The proof below connects that admission boundary to the existing route induction; it does not validate a proposed native repair.

## Actual observations

The root-owned isolated runtime is sealed as `b2943303a0969e13f546765e1651ea1a7cfd86191a36f9a3dc99c9ce5fd73c9d`. `OBSERVATIONS.json` authenticates both trace-prefix boundaries and complete stderr hashes. The two cohort extracts start at the unique 32px root write in each test interval, selected by its device identity. Pointers are used only within each captured interval, not across processes, document lifetimes, or pseudo identities.

| Child scenario | First / settled | Root provider history | Following normal root entry |
| --- | --- | --- | --- |
| No intervening read | 64 / 64px | 16 → 23 normal, 32 → 23 AnimationOnly | Declined; empty local hint, normal dirty false, animation dirty true |
| Root read before target animation | 46 / 46px | Same sequence | Also declined with the same state |

Both reports have all calibration controls true, no errors, and completed cleanup. Neither device cohort contains an `animation-task` record. This absence is bounded to the instrumented existing-style path and captured interval, not a claim that no other engine mechanism ran. Native execution is root-owned; this package only analyzes its saved records.

The root-read result is not a successful normal-delivery witness. The exact executed JavaScript performs `calibration.cancel()`, then the optional `getComputedStyle(root)` read, then constructs the target animation. A restored provider can therefore supply a fresh target conversion without rebuilding a previously computed target. The numeric pair and ordering support that explanation, but do not independently log every internal conversion or prove that a particular stored keyframe number caused the result.

## Exact source boundary

All changed source references are the actually built `css-root-font-cancellation-trace-instrumentation-v3` candidate, based on the known font-unit admission fix. `SOURCE.json` records the read-only e86 object for `restyle_hints.rs`; Searchfox discovery confirmed the same named operation before the immutable object was read.

1. `RestyleHint::propagate` in AnimationOnly removes animation and recascade hints, returns an empty propagated hint, and retains the ancestor-font flag. This does not itself forward retained work. `recalc_style_at` separately ORs the freshly computed child hint into the propagated hint.
2. `note_children` inserts that propagated hint into child data and uses the current traversal's predicate. For non-initial children in AnimationOnly it marks the parent with `set_animation_only_dirty_descendants`, not `set_dirty_descendants`.
3. Gecko's normal `element_needs_traversal` accepts missing styles, normal dirty descendants, or a nonempty local hint. Animation-only dirty descendants are consulted only in the AnimationOnly branch; Servo's damage branch does not apply here.
4. `pre_traverse` calls this predicate after root invalidation. The recorded root has styles, no normal dirty bit, and an empty local hint, so its token contains no root. Descendant hints are not scanned by this gate.
5. Existing-style `process_animations` returns early for AnimationOnly. Normal recascade and effect-task generation consequently require a separately reachable normal traversal; retained hints alone do not establish it.

The trace directly records this combination, including child hints and dirty-channel choices. It does not authenticate a JS DOM ID for each opaque node, establish all pseudo/host routes, or prove that clearing a particular native bit is the unique cause. Source repair and subsequent reproduction remain separate.

## Minimal refinement

`Entry.lean` imports the existing Route library without changing it. `Gate` models the Gecko normal-entry inputs after root invalidation. `enter` now creates `load route []` only when that gate admits traversal; denied entry retains the route as an unscheduled suffix. The existing arbitrary-budget `no_scheduled_work_no_visitation` theorem proves that more dispatch steps cannot repair denied entry. This is the concrete gap in applying `scheduled_route_visits_in_order` directly to the trace.

The minimal root-omission invariant is: if retained normal work is owed below the chosen root, that root must be normal-eligible at normal pre-traverse. `reserveNormal` is a specification-side realization that reserves normal dirty ancestry for such work and leaves a no-work state unchanged. It is not extracted native code or a recommendation to mark only the document root. The resulting admitted route composes with the existing arbitrary-length forwarding theorem.

Native obligations remain explicit: establish that the retained work is normal work; preserve appropriate dirty ancestry at every necessary intermediate node and through hint retirement; choose the correct traversal root; dispatch before observation; and perform normal recascade/task delivery/rebuild for the actual target or pseudo. The imported `forwardAll` policy stipulates successful downstream forwarding. The new theorem prevents root omission under its scheduling invariant; it does not prove that native code establishes that invariant, that root admission alone fixes intermediate pruning, or that provider freshness follows from visitation.

## Checked evidence

Actual run2 `1a5e11 / session40313 / e6cc86 / exit0` checked seven theorem audits and five genuine decide-false controls. The controls reject treating animation dirtiness as normal eligibility, starting from retained but unscheduled work, repairing absence by extra dispatches, setting the wrong dirty channel, and denying correctly reserved work. `run2/Audit.log` reports only the Lean axioms listed there; no `sorry`, custom axiom declaration, or native decision shortcut is used. Seven exact imported modules were rebuilt with the pinned Lean executable in owned scratch, then the scratch was removed.

Run1 `150252 / session60159 / 293edb / exit1` is preserved. Its 100-step false control produced a kernel application-type error rather than the required decide-false diagnostic. The control was reduced to five steps; the actual arbitrary-budget denial theorem and all production model definitions were unchanged. No native code, browser, index, canonical state, or historical proof package was modified.
