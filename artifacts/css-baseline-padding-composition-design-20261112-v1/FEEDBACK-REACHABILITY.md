# Padding feedback: separate hypothesis, not a defect verdict

The local PresShell source has the same non-root `DoReflow` Init call as the indexed source; INPUTS.json pins that whole local file and local-pres-shell-excerpt.txt retains the relevant context. The copied containing-block candidate's `InitOffsets` is the other end of the proposed cycle. Its exact original signed32 source excerpts and proof remain frozen in the baseline capsule.

Pinned upstream references:

- [PresShell reuses used padding](https://searchfox.org/firefox-main/rev/a9a644f66adb0cbb132f042bb7df24032f56346a/layout/base/PresShell.cpp#10851).
- [Baseline application](https://searchfox.org/firefox-main/rev/a9a644f66adb0cbb132f042bb7df24032f56346a/layout/generic/ReflowInput.cpp#2444), with independently guarded [block](https://searchfox.org/firefox-main/rev/a9a644f66adb0cbb132f042bb7df24032f56346a/layout/generic/ReflowInput.cpp#2467) and [inline](https://searchfox.org/firefox-main/rev/a9a644f66adb0cbb132f042bb7df24032f56346a/layout/generic/ReflowInput.cpp#2470) calls.
- [Grid property producer](https://searchfox.org/firefox-main/rev/a9a644f66adb0cbb132f042bb7df24032f56346a/layout/generic/nsGridContainerFrame.cpp#8112).

A native/browser witness needs all of the following, none established by this source design:

1. A grid item obtains a nonzero content-baseline padding property and completes a parent-driven reflow that caches the adjustment.
2. The same frame is eligible and actually selected as a non-root reflow root, without a continuation. `CanBeDynamicReflowRoot` excludes line/ruby/inner-table/table cases; its containment branch accepts layout plus both-axis size containment. Eligibility alone does not prove selection, and containment may alter baseline participation.
3. A descendant/content change triggers reflow at that frame without a parent grid reflow first changing/removing the property or forcing propagation past it.
4. Used-padding lookup returns the adjusted cache rather than early first-reflow/SVG zero or theme padding, and the overriding Init path reaches the same-axis application with its suppression flag absent.
5. The resulting padding affects an observable or cached state and is not reset by a later producer before observation.

The strongest first diagnostic would record the property, cached padding, override padding, flags and resulting padding for parent-driven then selected-root reflows on the same frame. Merely comparing two style declarations or assuming `contain` guarantees baseline alignment is insufficient. Repeated positive increments are a mathematical counterexample to reusing the single-invocation bound for arbitrary already-adjusted overrides, not evidence this loop is natively reachable.

No new semantic initialization mode or property precedence change is authorized by this note. Root owns any reachability probe; no browser or native run was performed here.
