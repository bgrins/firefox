# Contextual steps: keyframe caller groundwork

Inactive five-source proposal on authenticated checkout bodies. It includes the sealed two-source predecessor and adds actual CSS keyframe computation contexts, Servo parent/context transport, and ordinary-restyle reconstruction metadata. The unresolved-count parser guard is unchanged. This is not a completed prerequisite, independently landable atan2 repair, native typecheck, or accepted bug.

## Implemented

Gecko's Servo_StyleSet_GetKeyframesForName now constructs its animation Context from the supplied computed style, real element, actual inherited parent (or originating element for a pseudo), per-document stylist, container query and tree caches. Explicit timing functions compute before grouping by offset/easing/composition. No FFI signature or computed timing representation changes.

Servo's ComputedKeyframe builder similarly constructs an actual animation Context and passes it into the intermediate-keyframe collection. The owning matching caller threads parent_style through update_animations_for_new_style and maybe_start_animations. Ordinary elements use with_default_parent_styles; pseudo-elements explicitly receive the newly resolved primary style, avoiding a stale originating-element style borrow. Existing keyframe declaration resolution is unchanged.

KeyframesAnimation records whether any explicit declared easing cannot compute without context, including range-name steps. needs_animations_update asks for keyframe reconstruction on ordinary traversals when an active name selects such a rule. This intentionally does not equate equality of the last integer result with absence of a contextual dependency. Current parser guards keep this new unresolved-count path inactive. Existing effect identity/JS-override handling is not bypassed, but its lifecycle has not been executed.

## Required before activation

A normal-restyle reconstruction hook does not cause the initial invalidation. Both new temporary Contexts currently discard builder dependency flags and rule-cache conditions after computing easing. Viewport invalidation's captured implementation consults the owning computed style's viewport flags; merely evaluating a temporary Context cannot set that style's flags. Root font, container selection/size and tree-counting dependencies need equivalent publication and invalidation integration. This proposal deliberately does not assert completeness for them.

The animation-only exclusion prevents a naive rebuild loop but also leaves animated dependency changes unresolved. Correct ordering when an easing itself depends on animated font/style must be decided and tested; a blanket normal-only gate is not a complete solution. Var()/attr()-bearing timing declarations and shorthand substitution remain on existing paths and are not made complete by scanning get_animation_timing_function alone.

WAAPI still has no proved target-live versus elementless computation policy for contextual easing. The current primary trace in SPEC-TRACE.md records the exact boundary. Servo_ParseEasing remains fallible and does not invent a count; retaining that rejection while removing the general parser guard would not be a complete compatibility fix.

Next native work is a dependency-bearing keyframe easing representation/hand-off to the owning computed style and effect invalidation, followed by exhaustive API publication handling. Do not activate generic Atan2 deferral until steps admission, keyframe/WAAPI lifecycle and existing integer consumers all work. Current subgrid support remains accepted fix127 with prerequisite122, not a second implementation task.

## Verification and checkpoint

Exact five-path forward/reverse/reapply transport passed without offsets or fuzz; Rust parsing passed for every candidate (2de1c2/0). Owned scratch was removed. Rustfmt formatted the candidate; two pre-existing cfg-block formatting differences were restored to avoid unrelated churn. No compiler, browser, canonical WPT, live source/index/epoch or build mutation occurred.

The intended six-case lifecycle fixture write was interrupted before dispatch by the signing request. No fixture or executed test is claimed. Required controls: same animation/effect identity with explicit keyframe steps under font, root-font, container, viewport and pseudo-element mutations; literal easing calibration; getKeyframes easing and sampled opacity; setKeyframes override preservation. General WAAPI target/null/retargeting cases need an explicit context policy before assigning new oracles.
