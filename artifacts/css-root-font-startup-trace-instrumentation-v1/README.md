# Simultaneous root/child CSS-animation startup trace

Diagnostic instrumentation on exact selective handoff8c89, including its font-unit admission prerequisite. INSTRUMENTATION.patch applies to that parent; native.patch is cumulative from e86b64866cdc5e2260ba9be08c45756fd96e21bb. Eight source roles are pinned, including unchanged parent data.rs. No live native source/index/application/canonical record or browser was modified. No native compilation or execution is claimed.

Set MOZ_ROOT_FONT_STARTUP_TRACE=1 in the browser process environment to enable RFST stderr lines. Presence enables the flag, including an empty value; leave it absent to suppress every new output. The disabled path still checks the environment, so this is not a performance-neutrality claim. There is no new style flush, DOM attribute enumeration, animation membership query or metric load. The original single token decision, atomic load and root-size calculation are saved in locals and consumed once. Existing mutation/queue/return order is retained. Runtime environment changes are unsupported diagnostic use.

Retain cancellation8 smoke, then execute the exact sealed target-restyle3 diagnostic. Logging must reproduce late46/46/46→64 before interpretation. Browser identity comparisons prove CSSAnimation identity only; native effect pointers supply a separate cohort-local observation. Initial results vary across launches and do not establish FinalAnimationTraversal.

## Trace boundaries

- entry/restyle/returned/finish: full flags, existing decision/kind and hints. finish precedes final-pass early returns; returned is the actual returned hint. admitted_animation is the existing short-circuited operand, not an unconditional membership observation.
- root-published: newly stored unzoomed device px, device pointer and existing old style computed font px. old_computed_px is zoomed style data, not a fresh read of the previous device value.
- signal/joined/seed/normal-dirty: existing selective atomic and post-join operations. These do not prove subsequent traversal/delivery.
- tasks/skip-existing-animation/delivery/effect-properties: existing task masks, early return and normalized Gecko delivery. Mask4 is EffectProperties. Rust input nodes may differ from normalized C++ target nodes for pseudos; pseudo type is recorded separately.
- build-properties/rem-basis/converted-font/built-properties: existing KeyframeEffect entry/pointer, already-loaded zoomed Rem basis/factor, already-computed FontSize keyframe values before append, then changed/base-changed flags before the early return. No final segment assignment or sampled-rule installation is logged.

Rust rows carry node addresses where available and thread identity. Rem rows carry the existing device pointer; interpret them within the synchronous conversion call on that thread. Construction can precede CSSAnimation attachment. C++ node pointers are explicitly converted through nsINode to match Rust OpaqueNode's base pointer. Addresses can be reused after destruction; no cross-document/process lifetime identity follows. Device/thread adjacency alone is not durable target identity. Worker stderr interleaving is not a total causal clock. Logging may perturb scheduling. No IDs, getters, flushes or sequence counter were added.

No post-publication update suggests route/task delivery; only early conversions suggest a missing later rebuild; a later old basis suggests provider/context timing. If64 is computed yet46 remains sampled, additional installation logging may be justified. This package does not instrument downstream composition queues preemptively.

## Bounded type review

Exact e86 type-source files establish the generated FontSize payload: longhands.toml selects FontSize with default normal animation; data.py maps it to ToAnimatedValue::AnimatedValue; computed FontSize defines AnimatedValue=Length, whose computed implementation exposes px(). The AnimationValue generator uses this animated type. It is not the computed FontSize wrapper's computed_size field. The borrowed match reads a Copy length without moving the enclosing value.

OpaqueNode is public with a public usize field. matching.rs imports TNode on Gecko; other touched callers already import it. UpdateAnimationsTasks uses bits(), never Debug. OwningAnimationTarget holds RefPtr<dom::Element> and PseudoStyleRequest; get() supplies the pointer for nsINode base conversion, including null. Task/pseudo enums become unsigned for %u, pointers const void* for %p, count size_t for %zu. C++ files include cstdio/cstdlib. No new FFI interface is added.

Source review/formatter parsing do not establish generated-bindings typechecking, platform include completeness or native behavior. A source-bound build remains required. AnimationOnly and FinalAnimationTraversal remain distinct flags; neither is inferred from browser output. No new bug count or repair acceptance.

## Saved checks

check.py authenticates eight roles and ten e86 type-source objects, reverses20 replacements to the exact selective parent, applies/reverses both patches with zero fuzz/offset, and checks formatter parser acceptance for six Rust/two C++ files. It does not format or compile repository files. RESULT pins tested inputs and removed owned scratch.

Preparation initially stopped at exact include/normalization anchor assertions9e0fc2 and99b3b8; ad996f completed with precise anchors. First check969225 stopped at the depot_tools clang-format wrapper requiring Chromium; source/log preserved. Check6dd5c8 passed using Mozilla's existing clang-format before multiline formatting/old-px addition; its log/result remain named initial. Final checkb06930 exit0 covers final source. No failed run is relabeled as final.

Root reviewed the final patch in0ba327 and authorized sealing. Final1d5820 reauthenticated all tested inputs/five references and scratch absence. Independent publisher reviewer was busy; no additional peer review is claimed. Native build is the next actual typecheck.
