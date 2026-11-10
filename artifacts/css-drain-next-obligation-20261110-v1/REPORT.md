# Remaining drain obligation: lifetime closure

Recommendation: implement the scoped lifetime-to-phase refinement in NEXT-PROOF.md, while keeping #160 held for a scheduler architecture decision. This source audit does not identify a concrete recurring style-lifetime renewal inside the inner StyleDocument drain. Do not repeat the completed scroll-timeline readiness or initial-admission probes. The strongest bounded next bug surface is the existing missing-pseudo lazy animation-rule composition failure, bug 1615083, rather than another speculative drain cycle.

Basis: `b1f13d1516967034ca17255bcb1634e9f166b54a`. Searchfox caller discovery preceded exact local reads; SOURCES.json pins complete copies and EXCERPTS.json pins the two Document excerpts. The current roadmap and prior progress/lifetime/feedback reports are authenticated separately. This review makes no native edits, browser/build runs, Git mutations or new bug claim.

## What can actually replace a style lifetime

| Path | Source boundary and consequence |
| --- | --- |
| `recalc_style_at` → `clear_descendant_data` | Display:none clears strict traversal descendants, preserving the hiding target. `GeckoElement::clear_data` drops ElementData and flags, not the DOM node or the target's CSSAnimation collection. This is a genuine lifetime change for descendants, but not a self-renewal mechanism for the hiding ancestor. |
| `ensure_data` and initial `process_animations` | A later visit can create new ElementData and admit initial animation management. It requires a reachable/revealed subtree. One hide/reveal supplies finite new work; the source does not turn that one event into unlimited repetitions. |
| `Element::ClearServoData` / `RestyleManager::ClearServoDataFromSubtree` | Root-inclusive callers found here include DOM unbinding/removal, slot reassignment, shadow changes and prescontext reinitialization. Document's stale-data clear is called from DeletePresShell. They do not establish an inner-drain callback that repeatedly destroys and recreates the same target. |
| Input UA shadow construction | `CreateShadowTreeFromLayoutIfNeeded` can clear descendants before creating an absent UA shadow tree. It returns immediately if the shadow root already exists. This is a layout construction case, not an unguarded style-iteration injection. |
| Pseudo/frame reconstruction | The discovered frame-constructor StyleNewSubtree calls belong to frame/layout work. `ProcessPendingRestyles` invokes post-traversal and frame changes after StyleDocument returns. StyleDocument's own initially unstyled root branch is a separate finite initial admission, not evidence of repeated frame reconstruction within its inner drain. |
| Animation collection destruction | `nsAnimationManager::UpdateAnimations` can destroy animations for a missing style or display:none root with the display-animation preference disabled. `AnimationsWithDestroyedFrame` performs additional cleanup after frame processing. Neither operation itself erases the hiding target's ElementData and reinserts its DOM node. Animation lifetime and ElementData lifetime must be distinguished. |

`ProcessPendingRestyles` asserts script is blocked, rejects reentrant style refresh, and installs a no-reentrant-flush guard. The inspected animation mutation batch appends records and schedules observers; it does not synchronously call their script. The sequential tasks admitted by this traversal execute animation/timeline/effect management, not arbitrary author callbacks or DOM insertion. These are concrete exclusions for the proposed obvious renewal routes, not a verified whole-program no-reentrancy theorem.

The outer restyle loop may encounter genuine later lifetimes because frame construction and post-traversal can cause more invalidation. Its iterations are separate StyleDocument invocations. An argument scoped to the inner drain cannot silently treat all work in that outer style flush as one fixed lifetime, or conversely use an outer-loop recreation to claim inner-drain recurrence.

## Relevant specification contract

[CSS Animations' animation rules](https://drafts.csswg.org/css-animations-1/#animations) describe cancellation under display:none and starting applicable animations when revealed. That contract allows real cancellation/recreation across changes; it does not mandate infinitely repeating style updates or supply a termination measure. Current implementation display-animation exceptions must still be respected; this audit does not infer all cancellation behavior from the Level 1 paragraph alone.

[CSS Conditional's animated-container rule](https://drafts.csswg.org/css-conditional-5/#animated-containers) requires query evaluation changes from animation effects to participate in style-change events. Therefore dropping normal query work or postponing it merely to make a drain terminate would require a separate observable-semantics argument. Authenticated webspec-index snapshots are retained for both sections.

## Remaining premise, not a new native cycle

The finite-generation premise still needs a complete accounting of permitted causes across target, pseudo, cascade level and style lifetime. A fixed finite DOM and finite producer-function roster are insufficient on their own. Conversely, the abstract renewal witness is not a native reproducer.

The completed V2 timeline trace already provides the relevant finite execution: 54 readiness restorations occurred outside StyleDocument; none occurred inside. Fifty affected style calls made two timeline changes each and returned. It closes that running-animation route for the observed fixture. This review does not extend it to every paused/seeked animation or arbitrary timing mutation, but has found no supported new same-call renewal fixture worth executing now.

A finite styled→hidden→revealed test could add lifetime-delivery coverage, especially with font-dependent animations or pseudos, but it would not discharge the missing global closure premise. It should only be added when a specific dropped/coalesced obligation is identified, not as another generic convergence test.

## Can #160 be narrower?

The already completed producer-only comparison is decisive: both A and B retained 137 PASS / 27 FAIL; the combined repair passed 164. Producer-local delivery alone is not a complete substitute for #160's dependent first-read behavior.

A constant iteration cap or node-count cap is not justified by the present generation model. It can silently leave deep or renewed obligations unapplied. Replacing the loop with a bounded font-dependency phase is a plausible architecture, but needs explicit cause/provenance and generation treatment: the current EffectCompositor queue is keyed by target/pseudo and cascade level with an eligibility Boolean, not by the causal dependency that generated each request. It cannot simply select “font-only requests” from that representation.

A narrower design would have to isolate normal font-dependent rebuilding from its animation application, preserve all intervening coalesced work, and prove which requests belong to the finite descending phase graph. Upward timeline management and other requests need explicit scheduling semantics. Such a design should retain the 164-case first-read gate and add relevant order/retirement checks; it is not a small loop-bound edit. Until that choice is made, the combined repair remains a held engineering candidate rather than a formally closed native drain.

## Optional independent surface: lazy pseudo animation-rule composition

The existing KeyframeEffect target WPT expects animated computed values for both generated and non-generated pseudos; metadata marks six absent-pseudo target-switch cases FAIL for bug 1615083. This is existing issue context, not a new finding or fresh runtime result.

The PostRestyleForAnimation early-return FIXME alone is not a correct root-cause analysis. Root's fresh tracker review of [bug 1615083 comments 2–5](https://bugzilla.mozilla.org/show_bug.cgi?id=1615083#c2) reports that absent pseudos should not be restyled as generated elements. The identified problem concerns missing animation rules in lazy pseudo style resolution and stale EffectSet::PropertiesForAnimationsLevel when composing. Comment 8 links the earlier animation-rule patch. This audit has not independently replayed that patch or authenticated the fresh tracker response; root retains it.

Therefore do not demand generated-element hint delivery for a CSSOM-only pseudo. If the existing WPT still fails on the current browser, trace the lazy style resolver's animation-rule inclusion and effect property-set freshness. The correct distinction is logical pseudo-style resolution versus generated-element styling. NEXT-PROBE.md describes the optional existing-test gate; NEXT-PROOF.md gives the immediate native-track proof implementation step. Neither depends on claiming a new drain renewal cycle.
