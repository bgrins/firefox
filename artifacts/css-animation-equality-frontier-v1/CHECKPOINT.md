# Equality frontier checkpoint

Static research only; no browser execution, native changes or confirmed new defect.

## Ranked leads

1. **Transition endpoint retention.** `Servo_ComputedValues_ShouldTransition` preserves an existing transition when its old endpoint equals the new value. `Servo_ComputedValues_TransitionValueMatches` also uses payload equality. `Value<Component>::PartialEq` deliberately ignores attribute taint and URL data. Concrete proposed sequence: registered `<string>` property transitions from distinct A to B; pause beyond the discrete midpoint; change underlying B from literal to `attr()` with the same text. Observe image-set(var(--value)), endpoint payload, transition identity, and forced resampling. Reverse taint direction, different-text updates, and a nontransitioned control distinguish old endpoint retention. **Oracle unresolved:** CSS Transitions defines equality of end/computed values but reviewed text does not explicitly settle provenance-only equality. Do not assert restart/cancellation requirements solely from hidden-bit inequality. Primary sources: https://drafts.csswg.org/css-transitions-1/#starting and https://drafts.csswg.org/css-values-5/#attr-security, read 2026-10-19.

2. **Interpolation metadata transport (provider lead).** `Value<Component>::animate` combines both payloads but copies URL data and attr taint only from `self`. A potential numeric observer is `--bundle: url(...) var(--n); border-image: var(--bundle)`: substitution into the whole custom value can make its URL tainted even though --n is numeric. Proposed clean/tainted endpoint directions, progress 0/.25/.75/1, literal controls and discrete string controls. **Not yet a spec-adjudicated bug:** precise attribute-taint transport through interpolation versus selected discrete endpoint needs verification. No fixture has been executed or final oracle asserted.

3. **Unchanged raw keyframes / external inputs.** `PropertyValuePair` declaration equality and `SetKeyframes` early return deserve a future URL-data investigation, but same-effect dependency behavior is already an explicit PLAN-OF-RECORD caveat. Neither overwriting skipped CSS-wide defaults nor globally changing equality is justified. Fixes 78 and 79 cover separate endpoint/base notification paths.

## Negative findings

- Indexed Searchfox `KeyframesEqualIgnoringComputedOffsets` omits composite, but the exact local helper includes it. Existing ledger `animation-composite` already repairs this. No duplicate bug or fixture proposed.
- Indexed SMILCSSProperty takes NonCustomCSSPropertyId, so direct registered-custom-value metadata cannot enter this interface. This does not establish all SMIL URL equality correctness.
- The global Value equality omission is intentional; each observer requires its own admission and soundness argument.

## Evidence and state

`discovery/` retains Searchfox output, including incomplete/failed queries. Complete `KeyframeEffect.cpp`, `KeyframeUtils.cpp`, `Keyframe.h`, `value.rs`, and `SMILCSSProperty.h` are indexed snapshots. `source/` retains exact locally changed source files separately; indexed/current bytes are not silently equated. No extracted execution, browser receipt, proof or novelty claim. Task paused for whole-CSS architecture research at root request.
