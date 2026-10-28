# Contextual steps conversion groundwork

This is an actual two-source prototype, not a completed steps feature or permission to activate generic Atan2 deferral. It preserves the current unresolved-count parser rejection. Current subgrid support is already supplied by accepted fix127, with fix122 as its documented prerequisite; rebuilding that work here would duplicate an accepted repair.

## Implemented native delta

`TimingFunction::try_to_computed_value_without_context` returns an Option, propagating unresolved count/control-point values before constructing a computed timing function. Existing context-free callers retain the invariant wrapper while the parser guard remains present. This replaces their distributed scalar unwrap assumptions with a single explicit boundary without inventing a count for unresolved input.

The normal `ToComputedValue` Steps branch now calls the existing `Integer::to_computed_value` with its supplied Context. It retains the current calc-versus-literal jump-none rule and raises a computed calculation's minimum to2 where required. Positive-count parsing, Integer rounding/clamping/saturation, serialized representation, generic timing-function layout and all non-Steps conversion behavior are retained. No alternate floating-point rounding implementation is introduced.

`Servo_ParseEasing` uses the fallible conversion and writes its output only after successful computation. Its signature and C++ ABI remain unchanged. A failure leaves the prior output untouched. This is preparation for an exhaustive transport design, not a new policy that unresolved valid syntax should permanently become TypeError.

The guard in parse_steps is byte-for-byte retained. Therefore this prototype does not admit a new unresolved tree to the remaining context-free keyframe/Servo wrappers and does not claim to fix the browser-observed atan2 count. No expected runtime behavior change is claimed for currently valid parsed counts.

## Remaining implementation, from current source

Three publication routes must be completed before removing the guard:

1. `Servo_StyleSet_GetKeyframesForName` computes explicit keyframe easing before grouping by offset/easing/composition. It has element, supplied computed style and per-document stylist, so a real animation Context is available through the existing create_context_for_animation helper. That helper also requires correct parent/pseudo style, container queries, ElementContext and tree caches. Compute the count before grouping; a fake context or context-free fallback changes grouping semantics.
2. Recomputing at initial publication is insufficient. The captured `needs_animations_update` checks UI animation data, rule changes, display, writing mode and scroll-self, but a font-only change can leave those unchanged. Retain actual contextual-keyframe-easing ownership/dependency information and schedule keyframe reconstruction on relevant normal restyles, preserving JS overrides and animation-only traversal exclusions. The dependency is about the retained expression, not whether its current integer result happened to change. Changing only animation property-value recomputation misses stored keyframe easing.
3. Servo's `IntermediateComputedKeyframe::update_from_step` has SharedStyleContext/base style, but its current call site lacks the complete element/context inputs needed for general relative/tree expressions. Thread the real element/context through its caller, or retain specified easing until its later element-aware resolution stage. Do not leave this backend's invariant unwrap newly reachable.

The API route is a separate concrete interface decision. `TimingParams::ParseEasing` currently accepts only a string and ErrorResult and stores a computed function; it cannot resolve an element/document-dependent count. The latest previously pinned Web Animations algorithm establishes grammar validation and atomic update, but does not settle target-live versus elementless document-snapshot computation, targetless effects, retargeting and getters. CSS Values provides outside-element font defaults; that does not itself choose whether this API is outside an element when a target exists. A snapshot policy needs a real owning-document/device input throughout constructors, updates and keyframe parsing. A target-live policy needs specified storage, recomputation/invalidation and compositor publication updates. Neither can be implemented honestly as a guessed16px font or by keeping the old folded coefficient.

These are the actual next caller changes, not hypothetical risks. The current native groundwork is useful without making that policy choice. A complete generic Atan2 repair remains held until previously admitted steps APIs and CSS lifecycle paths retain their intended behavior.

## Test obligations and evidence

Reuse the existing accepted integer rounding/range tests and CSS easing grammar/computation tests. Cover literal0/negative rejection, literal1/jump-none rejection versus calculated1 clamping, fractional ties, huge values and NaN. Add a font mutation with an unchanged animation effect and explicit keyframe timing; verify same effect identity, keyframe easing and sampled output against literal controls. Keep the Atan2 proposal's steps/subgrid/z-index em and px cases, including parse admission assertions. Null-target API, retargeting, clone/getters and atomic failed-update observations require the explicit API policy before assigning new normative expectations.

Searchfox located current callers; local bodies were captured and hashed before editing artifact copies. Exact two-file forward/reverse/reapply transport and Rust parsing passed5f8178/0, with owned temporary files removed. Easing rustfmt --check passed b0d1c8/0. No native typecheck/build, browser, canonical WPT, source/index/epoch mutation, memory-accounting proof, new coverage count or accepted fix is claimed. Other captured files are source evidence only. The prior API plan and current fix127 correction remain explicitly referenced.
