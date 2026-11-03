# Pending animation application after the last style traversal

The confirmed late trace moves the failure downstream of endpoint conversion: root reports pass2, child64px `changed=1`, a new unposted request, `skip=0`, actual deferred posting with pretraverse=false, then document exit/no-root. A later traversal selects that child and rebuilds the same64px endpoints with changed=false. This note uses root's reported sequence; the independently sealed trace analysis remains the authority for raw/JS joins. It does not claim initial-load or deeper-chain closure.

**Recommendation:** make animation application a completion obligation of style resolution, with an explicit convergence policy. Do not ship a third pass or replace the second-pass `if` with an unqualified `while`. The source supports a concrete drain design, but not yet a generally sound small native patch. The immediate next discriminator is the already prepared depth2/depth4 probe, followed by a root-relative feedback control before executing any repeated-drain candidate.

## Exact repair seams

At pinned e86, `ServoStyleSet::StyleDocument` runs compositor PreTraverse before pass1 and once before optional pass2. `EffectCompositor::RequestRestyle` marks the map entry true before PostRestyleForAnimation. The latter's Servo/pre-traverse branch does not schedule PresShell work. `KeyframeEffect::UpdateProperties` replaces changed properties and requests a Layer restyle, which can therefore arrive during pass2 after the last drain. The return value only expresses post-traversal work, not queue exhaustion. RestyleManager clears the restyle root during post-traversal; a subsequent StyleDocument returns before PreTraverse when no root remains. Merely relying on the existing outer loop does not close this trace.

A candidate drain must use **PreTraverse's selected-work result**, not HasPendingStyleUpdates as its loop condition: the latter includes throttled, outside-subtree or otherwise ineligible entries that do not require this style operation. Keep actual root re-reading after each selected drain because PreTraverse can change it. Preserve snapshot ownership, postTraversalRequired accumulation, traversal guards and post-traversal tasks. Do not call PresShell::RestyleForAnimation inside a style refresh or while Servo holds element borrows; moving the deferred post alone crosses existing assertions and still does not guarantee synchronous installation.

For an already-styled document the candidate operation is:

1. Run the existing first traversal.
2. Drain eligible queued animation targets with existing PreTraverse.
3. If it selected work, run the corresponding animation application **and normal dependency propagation** using the existing traversal entry, then repeat completion checking under a defined convergence policy.
4. Return only after eligible work for this style operation is settled, or after an explicit cycle policy has been applied without silently dropping pending entries.

This is a design, not executable pseudocode with a hidden assumed termination theorem. It identifies the minimal C++ scheduling seam; determining the convergence policy is a remaining correctness requirement. An extra animation-only final pass alone can install this one child's64px, but can change another provider and leave deeper em endpoints stale. Suppressing EFFECT_PROPERTIES generation merely to make the queue empty would conceal that obligation.

## Conditional termination argument and its limits

For the depth fixture's restricted domain—fixed DOM, paused constant keyframes, root absolute32px, only ancestor-to-descendant rem/em font dependencies, stable ordinary declarations and animation membership—the provider graph is finite and acyclic. Once providers at level n settle, processing a dependent at level n+1 can settle it. Each full application/rebuild wave advances the settled frontier. The required waves depend on dependency depth, not a universal two/three-pass constant. This is a conditional argument; current Gecko queues do not encode that graph or enforce this restricted domain, and it is not a native termination proof.

General traversal also processes transitions, custom-property-driven animation definitions, container-dependent values and effect membership changes. Their convergence is not established by this font-only argument. Equality in UpdateProperties avoids redundant requests only after inputs stabilize; it supplies no bound on a sequence of distinct changed values. A queue-length check is not a progress measure. Repeated-state detection does not bound an ever-changing numeric sequence. A fixed iteration budget terminates execution but requires a specified fallback and cannot be advertised as correct synchronous resolution for arbitrarily deep acyclic chains.

The present selective/trace parent also retains the separately validated, uncommitted root-identity animation-context defect. Its derived animation context does not yet carry the root/pseudo distinction supplied by the independent glue repair. Thus a root-relative animated font is a concrete source-level feedback risk for repeated normal rebuilds, not a hypothetical reason to ignore cycles. A repeated-drain experiment must not silently incorporate that repair or relabel changed root-self results as cancellation success. Validate the existing root-self signatures separately, and compare a deliberate composition only with exact source roles.

A generally landable implementation needs either a provably ordered dependency evaluation (larger than this scheduling edit), or a reviewed finite cycle policy compatible with style/animation semantics. This note does not invent that policy. Pending actual depth evidence, the safest experimental path is an explicitly diagnostic bounded drain that reports saturation and preserves pending requests; it is not a proposed production fix and no patch is included here. Root can choose that experiment after reviewing its bound/guard rather than running an unbounded loop.

## StyleNewSubtree is a separate caller contract

`StyleNewSubtree` performs initial styling, then `PreTraverseInSubtree` and `AnimationOnly | FinalAnimationTraversal`. It asserts no post-traversal work. In the pinned Rust path, `finish_restyle` returns RECASCADE_SELF before ordinary old/new dependency checks under FinalAnimationTraversal, while `clear_state_after_traversing` clears restyle flags/damage and animation-dirty descendants. Animation-only processing of existing styles also skips process_animations. Consequently, an empty compositor queue after that pass does not establish fresh descendant keyframes: missing work can have been suppressed before enqueueing. Repeating the same final pass is not a sound substitute for normal dependency propagation.

A unified repair would perform dependency-settling passes while preserving required hints, then use forgetful final cleanup only after settlement. That changes the initial-style/frame-construction contract and needs review of StyleNewSubtree callers, frame/restyle damage and display:none/NAC behavior; do not reuse the late-document loop unchanged or remove FinalAnimationTraversal in passing. Keep initial-load tests and late pre-styled tests independently observed.

## Smallest validation decision

Run the existing prepared animated/literal root ×depth2/4 cases, retaining first and ordered settled arrays. A literal-root failure proves that descendant animated-provider chains alone exceed the current completion behavior; it does not require root publication to reproduce. Then, before any experimental drain build, specify the saturation behavior and include root-self font-relative/absolute controls, unchanged cancellation8/depth4, and initial/late startup lanes. The diagnostic should retain queue/pass records to show actual applications at each level, not infer pass count from JavaScript depth.

No implementation, model, runner, native build, browser execution or checkpoint modification was made. The completed cancellation/font publications and the pending V127 commit must proceed independently of this open scheduling design.

Source discovery used [PreTraverseInSubtree](https://searchfox.org/firefox-main/rev/7a315fc898bbd3e61ba7dd220a8fb1d0721a1eb7/dom/animation/EffectCompositor.cpp#794-938) and ServoStyleSet::StyleDocument/StyleNewSubtree in the same indexed revision. The exact e86/context and selective instrumented files in REFERENCES.json are the source authority here.
