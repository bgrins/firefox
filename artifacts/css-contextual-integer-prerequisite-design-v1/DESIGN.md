# Contextual integer prerequisites

These are designs for known bugs 2037744 and 2037743, not new defects or accepted patches. The concrete first implementation should be NameRepeat. Steps needs additional caller work before its parser restriction can safely be removed. Both can be tested without changing Round or installing held120; neither should preserve the current incorrect Round fold as a workaround.

Evidence is explicit HEAD90 source plus the sealed installed123/124 reference bodies carrying fixes118/119/121/122. These are historical source roles, not newly verified live guards. No current native source, binary, index or runtime state was read. Searchfox identifier/text discovery confirmed the relevant gates and callers; whole-file fetching failed network access, so the exact retained git objects supply bodies. The nonexistent computed/grid.rs lookup was abandoned; grid representation and derived conversions are in generics/grid.rs. webspec-index is unavailable; primary specifications were checked through web retrieval on 2026-10-24.

## Shared representation

Integer::parse_positive calls parse_integer_with_clamping_mode(AtLeastOne). A literal becomes inline; a typed math expression remains a boxed CalcNumeric with its range policy. Integer::resolve is deliberately context-free and may return None. Integer::to_computed_value(Context) already evaluates the retained tree using context, normalizes the numeric result and rounds to i32. CalcNumeric::resolve applies its stored range policy. Installed121 corrects that policy in the separate context-free resolve path; installed118 corrects rounding precision. Neither makes relative inputs context-free.

Use the existing Integer computation rather than resolving a unit coefficient or substituting a default font. A computed i32 can continue to feed both consumers. Keep the original specified Integer for serialization; do not replace it during parsing with a guessed count. Dependency tracking must flow through the real Context and normal style invalidation.

## NameRepeat: move the cache across the computation boundary

Current chain: GridTemplateComponent::parse_without_none -> LineNameList::parse -> NameRepeat::parse -> RepeatCount::parse -> Integer::parse_positive. NameRepeat rejects unresolved Number counts. LineNameListValue::line_names_length then calls resolve().unwrap(), and LineNameList::parse accumulates expanded_line_names_length. The generic ToComputedValue derive converts counts but copies the cached usize. Removing only the rejection would expose the unwrap; replacing failure with zero would make the cache disagree with later computed counts.

Minimal design, two Rust source files plus WPT:

1. In specified/grid.rs, retain count type/admission and the auto-fit/duplicate-auto-fill checks. Remove the contextual rejection only together with removal of parse-time count resolution/cache arithmetic.
2. In generics/grid.rs, replace LineNameList's derived computed conversion with an explicit conversion that first computes every retained line-name entry using the supplied Context, then calculates expanded_line_names_length from those computed counts. Keep the existing native struct layout. If the specified cache field is retained for ABI/template simplicity, make it a documented unused placeholder; it must never be treated as a resolved cache. Audit every constructor and inverse conversion.
3. The computed cache fold contributes one for an explicit name group, zero for auto-fill, and pattern_length.saturating_mul(computed_positive_count) for an integer repeat; combine with saturating_add. Preserve fix122's usize saturation and its native full-width consumer guard. Recompute after conversion, not by adding to a stale parsed cache. Empty name groups contribute one group; an empty repeated pattern remains inadmissible.
4. Add the appropriate computed field bound to the Subgrid variant if the manual implementation is restricted to the specified Integer/computed i32 pair; TrackList's existing field-bound pattern is the local precedent. This Rust derive/type boundary needs compilation, not a presumed two-line parser fix.
5. from_computed_value must rebuild a consistent specified value (and any explicitly unused cache policy), while resolved/animated conversion must not reintroduce a stale count cache. Subgrid animation currently errors; no interpolation feature is proposed.

The consumer shape need not change, and no C++ patch is indicated by this design. A standalone HEAD90 alternative must include equivalent saturated cache arithmetic at the new computation location; an installed-stack patch must preserve122 rather than copy the old wrapping multiplication. No patch is produced or compiled here.

## Steps: context conversion and publication safety

Current parse_steps stores Integer but rejects resolve()==None. TimingFunction::to_computed_value ignores its Context and calls to_computed_value_without_context, whose Steps branch unwraps resolve(). Thus a parser-only change is unsafe even for an ordinary CSS declaration.

The repair should let typed contextual counts survive parsing and use steps.to_computed_value(context) in the CSS computed conversion. Preserve the other timing variants initially; cubic-bezier and linear have additional bug2037743 gates and are outside this integer-only prerequisite. Keep literal invalid counts rejected. For jump-none, reject an inline literal1, but retain math expressions and clamp their computed integer to at least2; all other positions require at least1. This preserves the denominator invariant in calculate_step_output. calc(0), calc(1), negative calc and contextual results0/1 must be tested explicitly. Do not call get() as a substitute for resolving boxed values during computation, or drop the stored121 range policy.

Publication paths that must be addressed in the same safe change:

| Caller | Available basis | Required treatment |
|---|---|---|
| CSS longhand ToComputedValue | Actual Context | Compute Integer directly, retaining normal dependencies. |
| Servo_StyleSet_GetKeyframesForName | element, computed style, per-document data | Reuse create_context_for_animation/Context::new_for_animation with the existing style and element context; compute the keyframe timing function, never call context-free unwrap. Ensure font/tree dependency changes rebuild the timing data. |
| Servo IntermediateComputedKeyframe::update_from_step | SharedStyleContext and base_style | Use its existing animation computation context path; carry any required element/provider context explicitly. Do not silently select a default count. |
| Servo_ParseEasing | String and computed output only | No element/style input exists. Make the context-free conversion fallible immediately so newly admitted expressions cannot panic. Returning failure preserves the old unsupported API behavior but is not full contextual Web Animations support. Full support needs a separately specified computation context or retained specified easing through the API boundary; do not invent a target font or claim this is solved by CSS longhand work. |

The last row is a real design boundary. A fallible context-free helper plus updated callers is a safe staged implementation, but cannot be called complete bug2037743 support. CSS keyframe conversion must not take that fallback merely because it is convenient: it has a supplied style. Expected core source scope is specified/easing.rs, geckolib/glue.rs and servo/animation.rs; supporting context plumbing may add paths. Computed timing storage can remain i32 for the CSS routes. A complete targetless Web Animations solution could require broader storage/API changes and must be designed before claiming universal admission.

## Independent bounded regression scope

Use calc(2 + sign(1em - 16px)) at fonts16/32/8/16, giving counts2/3/1/2 without Round. Calibrate literal count references, actual retained declarations, font and an independent em box before checking results. Add sibling-index() with at most three siblings to exercise a distinct context source. These tests prove the prerequisites without relying on held120 or a corrected Round shortcut.

NameRepeat: test columns and rows; a five-line subgrid with `[pre] repeat(COUNT,[x]) repeat(auto-fill,[fill]) [tail]` has literal reference groups respectively `[pre] [x] [x] [fill] [tail]`, `[pre] [x] [x] [x] [tail]`, and `[pre] [x] [fill] [fill] [tail]`. Separate computed/resolved-name checks from geometry; use literal twin grids to avoid deriving the oracle from the implementation cache. Cover no-auto-fill, [] groups, dynamic recomputation, inherit's computed count, positive clamp of calc(0)/negative, literal0 rejection, auto-fit rejection and duplicate auto-fill rejection. Retain existing saturation boundary tests from122.

Steps: cover animation-timing-function and transition-timing-function computed serialization, start/end and jump-none; use calc(3 + sign(1em - 16px)) for always-valid jump-none counts3/4/2/3, plus explicit computed0/1 clamp controls. Include @keyframes timing declarations and a paused CSS-animation literal twin sampled away from a discontinuity to test actual output, not just serialization. Retain existing complete timing-functions-syntax-valid/invalid/computed and step-timing-functions-syntax files without broad metadata changes. Their existing contextual and jump-none calc cases already exercise part of the desired behavior. Add no-panic/behavior tests for the context-free Web Animations API and the Servo caller according to the selected API policy; these must not be mislabeled full contextual support.

The held120/new Round guard may subsequently be tested as an ordered dependent change using the bounded integer wrappers. These prerequisite tests should land independently of either Round guard. Their positive finite expressions avoid the disputed folding route; standalone operation on historical base still requires honest handling of the inherited range/cache differences, not silent inclusion of unrelated accepted patches.

## Specification mapping and limits

[CSS Values4 numeric functions](https://drafts.csswg.org/css-values-4/#numeric-functions) permits contextual computation and clamps function results rather than rejecting out-of-range numeric functions. Its [computed-value rules](https://drafts.csswg.org/css-values-4/#calc-computed-value) use available style information. [Grid2 name-repeat](https://drafts.csswg.org/css-grid-2/#typedef-name-repeat) accepts positive integer counts and constrains auto-fill placement. [CSS Easing1 steps](https://drafts.csswg.org/css-easing-1/#funcdef-steps) requires a positive count, greater than1 for jump-none. These support context computation and the lower-bound tests; they do not supply a missing element to the context-free FFI.

[Web Animations timing updates](https://drafts.csswg.org/web-animations-1/#updating-the-timing-properties-of-an-animation-effect) parses an easing string; the inspected algorithm does not resolve the targetless font/provider choice. Do not infer a default-context policy from its syntax requirement. Known bug IDs come from existing source TODOs, not a new bug-status investigation. Root's24PASS/14FAIL diagnostic is reported context, not independently reverified here. This capsule supplies source mapping and patch design only; no new bug count, observed crash, compilation, runtime fix or acceptance is claimed.
