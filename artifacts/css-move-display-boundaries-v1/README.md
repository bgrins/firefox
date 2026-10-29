# Move invalidation and shadow-state observations

The connected Firefox browser reports version 158 in its user agent. These are browser observations with unchanged local native sources, not a candidate build, a factory-default release claim, or a full mach WPT run. Privileged browser metadata access was unavailable.

## Display and selector matrix

`probe.js` exercised 1,296 combinations across ordinary parents, parents within a shadow root, and slotted children; block/none/contents on both parents and the moved element; eight selectors; and ordinary versus state-preserving moves. All 23,328 snapshots completed without exceptions and all fixtures were removed. The 594 computed-style/matches disagreements occur only after moveBefore or restoration. Initial and ordinary-move samples agree. Each topology has 198 disagreements. This broadens the existing old-parent invalidation evidence, not the accepted bug count. Computed values are captured before the fresh matches oracle.

## Shadow state loss

The calibrated animation controls isolate a different implementation boundary. CSSAnimations on the moved root and its light-DOM children retain identity, time375 and computed margin3.75px after self-reference, original-gap and cross-parent moves. An animation inside the moving host's shadow root is replaced: the original becomes idle with null time, and the new animation starts at zero. No-move controls preserve all three shapes, and ordinary appendChild cancels all three. Initial samples have pending=false. Replacing the internal style element with an adopted stylesheet produces the same result. Separate imperative-animation controls retain identity/time625.

Custom-element controls corroborate the boundary. Root/light descendants receive connectedMoveCallback, while shadow and nested-shadow descendants receive disconnectedCallback then connectedCallback on self-reference and cross-parent moves. An existing upstream WPT already covers the single-shadow cross-parent callback failure and marks it expected FAIL. This is known callback coverage, not a claim of a newly discovered callback defect; the animation witness exposes another consequence of the same context-loss family.

Element forwards the move context to light children but invokes ShadowRoot Bind/Unbind without it. Each shadow helper creates a fresh context whose move flag defaults false. A three-DOM-file proposal in [css-shadow-move-context-repair-v1](../css-shadow-move-context-repair-v1/) forwards only that flag, retaining the shadow-specific root/context semantics. It has not been compiled, installed or executed.

## Focused WPT execution

The exact proposed HTML test scripts ran with the repository's genuine testharness.js and testharnessreport.js over a temporary loopback server. The server adds only result/completion observers after the harness scripts. The animation page completed9PASS/3FAIL; the callback page completed2PASS/3FAIL; both harness status0. Every failure is a shadow-descendant target. Raw completed callbacks are `wpt-animation-completed.json` and `wpt-reactions-completed.json`. This is system-browser harness execution, not mach/WPTrunner or candidate validation. Inputs are fingerprinted in SUMMARY.json.

The first snapshots had all subtest rows but preceded the completion callback; they are preserved as incomplete evidence, not successful harness endings. The subsequent runs explicitly awaited completion. An earlier state probe waited on animation.ready and timed out; its tab was closed before a synchronous calibrated replacement ran. Direct absolute output saving and oversized inline harness injection were rejected by the browser tool before those requested evaluations; the loopback server avoided both limitations. The initial server start was denied by filesystem/network sandboxing; the explicitly authorized loopback start succeeded. Both owned server sessions are terminal and the owned tab is closed, leaving the original about:blank tab. No temporary build target or app backup was created.

## Next actions

1. Complete the pending233-file signed research checkpoint once 1Password is ready; preserve its exact existing index and message.
2. Finish native installation and final validation of the already paired old-parent invalidation repair, then commit its native/WPT payload separately from research.
3. Validate shadow-context propagation as its own experiment and commit: original/candidate runs of the new17callbacks, existing custom-element shadow expected failure, and animation/frame/focus/ordinary-removal controls. Only remove obsolete expectation metadata after actual candidate success. The two native proposals touch disjoint source files and neither is assumed to require the other.
4. Record the scoped arbitrary-gap Lean model and resume the remaining contextual-easing/provider roadmap after these concrete DOM/style boundaries. The new model establishes interval locality from erase/reinsert, not DOM callback or native refinement.

Accepted totals remain145native fixes,146tracked IDs with120held, and two test-only repairs. The frozen staged roadmap and all233 staged bodies remain unchanged. The signing recovery, newly completed models, these observations, and new proposals are not yet committed. This continuation note supplements the frozen roadmap until the next signing checkpoint.

The arbitrary-gap model also received independent bounded source/log review (dc0e16/cf35b7), without a kernel rerun. The shadow-context native proposal received independent source/context review (d94658/044d9e/712e0f); compilation and actual candidate execution remain open.
