# Guarded duration task and sampling boundaries

The guarded V2 task can change effect timing and cause a second traversal within the same style flush. It is not intrinsically a next-frame operation. The inspected mechanisms prevent recursive flush entry and coalesce pending requests; they do not establish convergence of self-dependent duration. This is a static trace while root-owned candidate session 63783 is active, with no candidate result read or inferred.

The local candidate is `matching.rs` SHA256 c3b2ddf2a3fb0ab2a8f5e74acaad0502e9e61f83e0427a300e106207ea1e7e64, from sealed proposal-v2. Unchanged implementation was searched through Searchfox; primary upstream raw views supplied bodies when CLI context expansion failed. Those views have different crawl dates and are not a complete local-branch refinement audit. Function names and source links are recorded in SOURCES.json rather than invented revision permalinks.

## Dispatch and same-flush consumption

1. `process_animations` compares old/new primary computed animation lists, requires specified or existing CSS animations, and queues CSS_ANIMATIONS | EFFECT_PROPERTIES. `finish_restyle` subsequently stores the new primary style. The task contains the element and flags, not a frozen new-style snapshot.
2. Traversal-local task-list destruction runs the sequential task on the parent thread. `GeckoElement::update_animations` borrows the element's current primary computed style and calls `Gecko_UpdateAnimations`. Driver context destruction occurs before traversal returns, not on a later refresh tick.
3. Gecko dispatches CSS animation updates before effect-property updates. The CSS animation manager reuses matching CSSAnimation objects and updates CSS-owned timing. `AnimationEffect::SetSpecifiedTiming` has a complete-timing equality early return; otherwise it updates normalized timing, notifies the animation and requests a Layer restyle.
4. `EffectCompositor::RequestRestyle` records a pending element/pseudo/cascade-level entry and coalesces duplicate postings. Inside Servo traversal or compositor pre-traversal, `PostRestyleForAnimation` deliberately does not mutate ElementData or post a new PresShell request. The pending entry remains for `PreTraverse`.
5. `ServoStyleSet::StyleDocument` explicitly invokes compositor `PreTraverse` after its first traversal and, if needed, traverses again. Thus timing changed by a drained task can affect another composition in the same invocation. `Servo_TraverseSubtree` itself performs eligible animation-only work before ordinary traversal; these are separate boundaries from a refresh frame.

## What bounds, and what does not

`RestyleManager::DoProcessPendingRestyles` rejects recursive entry and installs AutoAssertNoFlush. Its outer StyleDocument loop handles further invalidations; it is not an animation fixed-point solver. StyleDocument contains one explicit second traversal per invocation. A task queued during that second traversal can again leave a compositor-table entry, because the same traversal-time deferral applies. The inspected code does not prove when every such residual entry will be consumed, nor that it alone forces the outer loop to continue.

Pending compositor work is queried by `UpdateOnlyAnimationStyles` and computed-style flush logic. The computed-style fast path also checks pending restyle ancestors; a nonempty compositor table alone is not proof that every property read will traverse. Therefore one model step must not be identified with one requestAnimationFrame callback, one getter, or exactly one whole flush. Repeated reads in one recorded sample can potentially cross different processing boundaries; native instrumentation would be required to count task/traversal steps reliably.

There is another concrete boundary: `StyleNewSubtree` uses AnimationOnly | FinalAnimationTraversal for a forgetful animation pass. In the exact V2 source, `process_animations` runs before `finish_restyle` checks FinalAnimationTraversal. That flag suppresses damage accumulation and clears restyle state; it does not suppress the new task. Initial acquisition is therefore not automatically outside the new update path. This is a review obligation, not an observed loop, regression, or proposal for an arbitrary iteration cap.

## Base style and ownership

The CSS-animation update receives current primary computed style, including contextual dependencies affected by animated inherited or same-element font. The separate `GetBaseContextForElement` path removes animation rules to obtain underlying values where effect composition needs them. `EnsureBaseStyle` is conditional on additive/base-value needs (and relevant timeline cases); it does not replace CSS animation timing input with an animation-free primary style. Fully replacing font keyframes do not gain a duration feedback barrier merely from that base-value cache.

Script timing ownership remains per field: CSS animation updates do not overwrite duration after a successful updateTiming duration override, while CSS-owned fields can still update. Script-owned keyframes likewise remain protected by their override flag. However EFFECT_PROPERTIES visits the target's EffectSet, including unrelated script effects, and can rebuild property/base values or request a restyle. The V2 existing-or-specified guard avoids dispatch on targets with no CSS animation but does not make this work CSS-effect-only. It does not schedule CSS_TRANSITIONS or timeline-update task flags.

## Connection to the bounded models

The scheduling model abstracts a computed-style commit plus conditional applied-duration update. It omits compositor queues, traversal multiplicity, initial acquisition, base-value caches and frame/style-read boundaries. Its fixed-exogenous-input idempotence theorem cannot prove native flush convergence.

The feedback companion's two-cycle requires synchronized entries (1000,1000) or (1500,1500) and the specified feedback input at each abstract step. The completed original record instead projects to (computed1500, applied1000); the separate boundary proof shows that state is fixed under the existing equality-guarded abstract step and is not a synchronized cycle entry. Neither the pending candidate nor an initial seed can be inferred from that original observation. Candidate records can test observable stability and mismatches, but cannot on their own identify which internal traversal produced each sample.

No source, application, index, canonical state or sealed input was changed. No browser, build, full live guard, model replay, acceptance increment or new bug claim is part of this trace.
