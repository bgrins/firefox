# Pending collection cannot yet enter the completing cascade

The requested pending source-item/winner-table patch cannot safely stop at the current production boundary. Four exact preimages are retained. No native patch or executable tests are supplied: an implementation that stores pending winners and then returns through the existing API would publish an unresolved style.

The concrete signatures are:

* `DeclarationIterator::Item = (&PropertyDeclaration, CascadePriority, DeclarationSource)`.
* `iter_declarations(..., custom: Option<(&mut Cascade, &mut computed::Context)>, ...) -> ()`.
* `Cascade::apply_custom_and_prioritary_properties(...) -> ()`.
* `apply_declarations(...) -> Arc<ComputedValues>`, also the return type of `cascade_rules` and `cascade`.

In the unvisited branch, `apply_declarations` initializes inherited/initial custom values, collects declarations, resolves ordinary custom/prioritary properties, tries cached reset properties, applies the remaining properties, finalizes attribute tracking and calls `context.builder.build()`. There is no unresolved-result owner at any of these handoffs. The visited branch deliberately reuses the unvisited substitution map and does not cascade custom values again.

`AnimationRuleSource` currently owns `FrozenAnimationRule<Infallible>` plus an eagerly materialized concrete PDB. Its type prevents recipes. Removing that restriction and adding a pending iterator variant would make the completion problem real even with the native producer disabled. Privacy of a constructor, a runtime feature switch, or a test-only constructor is not an exhaustive Rust handling of the pending variant. An assertion, silently ignoring it, synthesizing an invalid value, or returning the inherited map would not be a correct implementation.

The owner author independently confirmed that the earlier owner work contains no unresolved-cascade completion API. The shared gates can be extracted safely, but delivering only that refactor would not constitute pending-root transport and admission. I have therefore not packaged a disconnected helper as the requested implementation.

## Concrete integrated type boundary

Use one collector for both the existing normal route and the new pending route. Proposed names below describe interfaces, not compiled definitions.

1. `SourceItem<'a>` is either `Concrete(&'a PropertyDeclaration)` or `SampledCustom { name: &'a Name, owner: &'a AnimationRuleSource, root: owned property handle }`. It is produced by the real rule-tree `DeclarationIterator`, with the existing priority, importance and pseudo-restriction handling. The concrete PDB contains only concrete items. Pending-only properties are enumerated from the owner, once, without a companion Parsed value. Longhand records continue storing the original PDB pointer.
2. `CollectedDeclarations<'a>` owns the longhand declarations and a `CustomCollection<'a>`. The custom collection retains actual winner roots, ordinary seen/revert state, and dependency work. Context, trackers and read guards remain caller-owned, avoiding a self-referential structure. Retained roots own their arenas; borrowed names/ordinary declarations retain the existing guard lifetime.
3. Admission uses one implementation of the current custom gates: reverted-priority permission, included flags and seen entry, in their current order. Concrete values then follow the existing `value_may_affect_style`, reference detection and application path. Pending items enter the winner table before any value-equality optimization. An ordinary revert removes the seen entry and updates the existing revert state exactly as today; pending endpoint-level revert is not reinterpreted as a rule-level revert.
4. `resolve_collected_custom(...)` consumes or mutably borrows the incomplete custom collection and returns a `ResolvedCustom` capability only when ordinary and sampled dependencies are complete. The capability must not be publicly constructible or obtainable by clearing the pending table. Failure retains the incomplete collection and current resolution state; it does not return a ComputedStyle or CSS-invalid value. The scheduler-aware endpoint operation is a dependency of this function, not an optional callback supplied by a host test.
5. Cache reuse, non-prioritary application, visited-style derivation and final `builder.build()` require the resolved capability. The existing concrete-only normal route must use the same collector and the existing ordinary resolver to obtain it. The visited branch consumes its already-resolved unvisited context and remains separate from custom collection.

There are two honest ways to connect this to callers. Either implement the normal scheduler so the public cascade still always completes, or propagate an explicit incomplete result through the real style traversal until an owner resolves it. The latter is not implemented anywhere in the inspected owner code and is a substantially wider change. Returning a `Result` internally and unwrapping it at the old Arc-returning boundary does not solve the problem. The recommended repair is the former: keep normal pending production disabled until collection and the scheduler/completion operation are wired together.

## Bounded patch dependencies

| Patch component | Exact dependency before normal admission |
| --- | --- |
| `animation_rule_sample.rs` / `declaration_block.rs` | Owned recipe roots with current-sample semantics; split concrete PDB materialization from pending property enumeration. No public pending AnimationValue. |
| `rule_tree/source.rs` / `properties/cascade.rs::DeclarationIterator` | Source-item iteration through the real rule tree; preserve compact source representation, identity and longhand storage. Compatibility PDB accessors cannot be treated as exhaustive pending-property enumeration. |
| `properties/cascade.rs::iter_declarations` and `cascade_custom_property` | Shared collection and actual winner gates; incomplete collection returned explicitly; concrete ordering and revert handling unchanged. |
| `properties/cascade.rs::apply_custom_and_prioritary_properties` / `substitute_all` | Pending-first provider lookup, current prioritary dependencies, shared substitution guards and a genuine resolution/completion capability. No typed-map or absent-map shortcut for a pending winner. |
| `keyframe_endpoint.rs` / existing substitution extraction | Scheduler-aware no-publication endpoint resolution, complete admission/defaulting distinction and transfer of tracker/cache/style effects. The currently exposed complete-style FFI is insufficient here. |
| `geckolib/glue.rs::Servo_AnimationRuleSample_Compose` | Final activation only after the preceding components are complete; retain descriptors rather than cached operands, preserve explicit/implicit classification and native operation ordering. |

Animated cycle policy, all computed-keyframe scope, registration changes, endpoint-level revert and unsupported-result handling remain the semantic dependencies recorded in the prior boundary report. They are not solved by the collection types. An acyclic research experiment may expose an explicit incomplete outcome, but it must not claim a shipped full repair or manufacture a numeric result for unresolved cases.

## Tests at the real collection boundary

The test entry should construct genuine rule nodes and call the same `DeclarationIterator` and collector used by `apply_declarations`, stopping with `CollectedDeclarations`. It must not call a reimplemented Boolean winner predicate or finish a style with unresolved roots. Once the production collector is extracted, test these cases:

* A source with an empty concrete PDB and one retained custom root yields that exact property/root identity and an incomplete winner collection; no custom value is inserted into the ready map.
* A higher important ordinary declaration wins before the animation level; the lower sampled root is absent from the winner table and its resolver is never invoked.
* Real ordinary revert/revert-layer entries update the same `RevertState`, and a disallowed lower sampled source is not admitted. Preserve existing revert-rule behavior rather than inventing a new custom-rule identity policy.
* A higher accepted custom declaration marks the real seen table; a later sampled declaration of the same name is not admitted.
* Excluded `RuleCascadeFlags` reject an item before changing seen or pending state; an eligible lower declaration remains selectable.
* Mixed concrete longhands and pending custom items retain the original longhand order/source pointer, with no change to the 32-byte collector representation.
* A second attempted sampled winner cannot overwrite the first or make an incomplete collection appear resolved. A compile-fail boundary test should reject passing `CollectedDeclarations` directly to the completion API.

These are test requirements, not executed or authored tests. The first end-to-end repair gate remains the unchanged ten-case browser diagnostic through ordinary animation scheduling, including the four red-phase histories and both creation orders. Snapshot-resolver tests and collection tests cannot replace that gate.

No build, browser, compiler, live index, canonical source or ledger operation was performed for this artifact. The exact blocker is the missing typed completion owner, not a missing permission or test harness.
