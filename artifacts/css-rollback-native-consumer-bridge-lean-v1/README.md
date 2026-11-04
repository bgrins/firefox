# Guarded rollback consumer bridge

This extends the existing represented-cutoff proof to the A+B+D candidate in `../css-rollback-cutoff-e86-rebase-v1`. It discharges a missing bridge: the actual longhand fast-bit/map gate and custom map gate, followed by guarded updates, implement the previously proved intersection control. It does not extract or verify Rust, prove the declaration providers correct, or add a browser bug.

Run `python3 artifacts/css-rollback-native-consumer-bridge-lean-v1/replay.py` from the repository root. `IMPORTS.json` pins the existing Lean dependency closure; compilation happens in a temporary directory that is removed. `RESULT.json` records compiler/source hashes and every module's exit code; `lean.log` retains commands and theorem axiom reports.

## What is proved

| Bridge | Lean result |
| --- | --- |
| Rust's `is_none_or(strictly_less)` replacement matches the existing representative operation; equal keys retain the old full priority, including its flags | `rust_keep_matches`, `rust_keep_tie_preserves`, `rust_add_matches` |
| A missing map entry projects to three empty representatives; adding Origin/Layer creates the map entry and sets the fast bit; Rule preserves the whole previous state | `packed_add_projects`, `packed_add_well_formed`, `rule_preserves_all_storage` |
| Longhand's conjunctive fast-bit/map rejection and custom's map rejection agree with represented admission | `longhand_allows_projects`, `custom_allows_projects` |
| Checking inclusion before or after cutoff admission has the same pure control result | `gates_agree` |
| Rejected declarations do not contribute rollback bounds or terminal results | `rejected_declaration_is_inert` |
| For any finite event order, either guarded consumer selects exactly the same terminal event as successive deletion of the regions excluded by accepted rollback declarations | `native_control_bridge`, `guarded_consumer_region_deletion`, `fresh_consumers_region_deletion` |

The final theorem reuses `representative_step_intersection` and `arbitrary_region_deletion`; it does not repeat their proofs or assume the desired whole-stream conclusion. No sortedness assumption is needed for this control equivalence. That is not a proof that an arbitrary provider order implements CSS cascade order.

`Packed.fast = Packed.slot.isSome` is an explicit reachable-state invariant. The candidate creates both entries together for non-Rule rollback, and initializes both empty. The model proves preservation. `stale_fast_bit_changes_admission` demonstrates why this condition matters: an existing rejecting cutoff with a false fast bit would be bypassed by the longhand gate. This state is not claimed reachable in the candidate.

## Native correspondence and remaining assumptions

The two candidate Rust files and consulted old proof files are pinned in `SOURCE-MAPPING.json`. Names below refer to those snapshots, not changing checkout line numbers.

1. `CascadePriority::allows_when_reverted`, `CascadePriority::unimportant`, and `CascadePriority::cmp` must correspond to the imported `Priority` mapping: collapsed origin comparison is `coreKey`, unimportant priority comparison is `normalKey`, tree/author levels map to `origin == 3`, and the style-attribute layer is 65535. Native flags are ignored by `cmp` and retained in priorities. The imported numeric ordering proofs apply only within their admitted coordinate ranges. This package does not prove extraction from native enums or that every provider supplies admitted coordinates.
2. `RevertState::add` is mirrored by `rustAdd`; `RevertState::allows` is the existing conjunction `representativeAllows`. The special and ordinary layer slots stay disjoint under the proved validity invariant. The stored priority, not just its scalar key, is retained on ties.
3. Each event stream is for one **physical longhand key** after logical-property mapping, or one custom-property `Name`, during one coherent cascade-state lifetime. Provider order, repetitions, property identity, and ownership are inputs. Other property streams must not mutate this key's cutoff or seen state. For a rollback event, `action` must supply the event's actual priority and resolved keyword kind. No claim about selector matching, rule-tree iteration, alias mapping, or provider provenance is made.
4. `included` must equal the event's native cascade-flag test at its visit. `action` represents the classification reached after native substitution and color handling. The theorem compares fixed event observations; it does not prove those computations pure, fixed in advance, or insensitive to earlier side effects. It only removes rejected events from cutoff/terminal control, not from all browser-visible bookkeeping.
5. The stream starts unseen for this key. `apply_one_longhand` leaves it unseen on rollback and marks it seen for every non-rollback terminal outcome, including `can_skip_apply`. `cascade_custom_property` temporarily inserts a seen entry and removes it for rollback; the literal rollback keywords cannot take the `value_may_affect_style == false` branch. A false result from that helper inserts a seen entry and is therefore **terminal**, even if no value is written. The model stops at the first terminal event, representing rejection of later visits by seen state. `RegionAction.skip` is available for explicitly inert events; it must not represent these terminal no-write paths. An already-seen native invocation has no remaining eligible stream. Registration, cycle handling, side effects, substitution results, and seen-map transaction execution are source-mapping obligations, not Lean-verified Rust operations.

## Rule identity boundary

`RepresentedControl.lean` supports both `.priority p .rule` and a distinct `.rule identity` exclusion. Only the first is represented by this candidate. The latter stores excluded rule identities and belongs to the held provenance work, not A+B+D.

`rule_is_not_identity_deletion` proves the distinction on a two-event stream: a neutral Rule cutoff permits a later terminal event, whereas excluding its shared rule identity removes it. The candidate therefore needs its provider's “next same-property declaration effectively comes from another rule” assumption to implement `revert-rule` region semantics. This proof does not discharge that assumption, silently import the held C repair, or count that known boundary as a new bug. The useful completed result is narrower: Rule cannot erase previously accumulated Origin/Layer constraints, and guard-rejected Rule or other declarations cannot alter them.
