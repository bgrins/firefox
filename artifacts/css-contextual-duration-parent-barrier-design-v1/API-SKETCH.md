# Explicit implementation seams (not a native patch)

Names marked NEW are proposed APIs, not existing call sites. This is deliberately not `native.patch`: publication/task separation is larger than an applyable loop at `StyleDocument`.

| Boundary | Existing code to reuse | Required change |
| --- | --- | --- |
| Resolve without publication | `compute_style`, `StyleResolverForElement`, `ResolvedElementStyles` | NEW prepare batch returns owned provisional styles/cascade inputs and original before-change style. Extract `finish_restyle`; exclude provisional styles from caches. |
| Retain and release task work | `SequentialTask`, `SequentialTaskList::drop`, `ScopedTLS`, `traverse_dom` | NEW explicit extraction/ownership. End worker scope and release all TLS/ElementData borrows before tasks execute. Empty transferred lists before their automatic Drop; preserve old path. |
| Supply main-thread input | `GeckoElement::update_animations`, `Gecko_UpdateAnimations`, `nsAnimationManager::UpdateAnimations`, EffectProperties | NEW explicit-input variant accepts provisional composed style and original transition before-change style. Select timing base separately. Do not read old primary style in this path. |
| Prepare only this frontier | `PreTraverseInSubtree`, cascade result updates, animation hints, `WillComposeStyle` | NEW exact-target selector retains eligibility/two-level handling. Collect owning keys before mutation, leave unselected entries untouched. |
| Actually compose and cascade | `replace_rules_internal`, `get_animation_rule`, `GetServoAnimationRule`, `ComposeSortedEffects`, resolver | NEW composition-only batch rebuilds rules from updated effect data with the same settled parent/root snapshots. Do not repeat all CSS tasks just because this phase recascades. |
| Publish and expose descendants | `finish_restyle`, `data.set_styles`, device root publication, `note_children` | Split publication/diff from task discovery. Commit original-to-final damage/root metrics before children. Preserve outer frame/post-traversal semantics. |

An owned C++ batch can retain `RefPtr<Element>`/pseudo identity and `RefPtr<const ComputedStyle>` original/provisional/final inputs. Rust must not export references tied to document-data guards, rule locks, AtomicRefCells or StyleContext. Owned Arcs/cascade inputs require an explicit ABI lifetime. A retained non-owning target array alone is insufficient.

```text
frontier := affected inheritance roots whose predecessors are current
while frontier is not empty:
    prepared := Servo_PrepareStyleBatch_NEW(frontier, transaction_inputs)
    [all worker/TLS/ElementData borrows end]
    Gecko_ApplyPreparedAnimationTasks_NEW(prepared)
    EffectCompositor_PrepareExactTargets_NEW(prepared.targets)
    completed := Servo_ComposeAndPublishBatch_NEW(prepared)
    require completed.final_styles_have_been_published
    frontier := completed.affected_children
```

The variant is remaining reachable inheritance nodes, not Pending count, numerical changes or a pass counter. Each node is released only after parent publication. Incremental pruning requires complete invalidation; a correctness-first path can traverse the affected subtree fully. Newly created pseudos/frame-related children require defined generation accounting rather than silently expanding the fixed universe.

For the explicit-px endpoint chain, the per-node operations are concrete: timing from final inherited input, sample stepped effect rule, cascade, commit. For general local dependencies, `ComposeAndPublishBatch` needs the selected property-stage/deferred-endpoint algorithm or must decline that experimental path before partial publication. This missing general implementation is explicit, not hidden in a claimed completion helper. Needs-resampling cannot become CSS invalidity or a successful stale return.

Keep one transition before-change snapshot and apply transition bookkeeping once per actual change. Composition must not start transitions from intermediate outputs. Check timeline/effect identity, script-owned timing, root metric and stylesheet/snapshot generations. Main-thread tasks remain within the outer script blocker and owning shell/document scope; no recursive PresShell flush occurs.

No performance claim follows. Serial execution is a correctness-first experiment; unrelated siblings can later batch in parallel. Cache reuse must account for settled parent/input generations. Parallel children never start before the parent barrier.

For opt-in fixed-endpoint admission, inspect original `Keyframe::mPropertyValues`/`PropertyValuePair::mServoDeclarationBlock` through a new Rust classifier. Validate full effect stacks and complete-replace/iteration modes; computed segment values alone cannot certify independence. This is a concrete source-level predicate to implement, not a test-name whitelist or a claim that current APIs already return dependency certificates.
