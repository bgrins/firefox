# Interpolation provenance repair proposal

The one-line proposal combines attribute taint with Boolean OR after successful payload animation. Exact local candidate: `source/value.candidate.rs`. Standalone alternative: `upstream-native.patch` against the retained root-supplied base snapshot; root owns exact patch application/reversal and isolated runtime testing.

## Procedure boundary

The complete `Value<Component>::animate` calls the payload provider with `?` before constructing its output. Thus unsuccessful arithmetic remains unsuccessful with no metadata output. Successful outputs retain exactly the same payload and first-operand URL data. Only attribute provenance changes. `CustomAnimatedValue::animate` still rejects different names, and the optional-value wrapper still rejects mismatched Some/None, accepts None/None, and delegates Some/Some.

The retained `Procedure::weights` specifies interpolation (1-p,p), addition (1,1), and accumulation (count,1). Addition and positive-count accumulation involve both operands, so preserving either operand's attribute provenance is consistent with the same normative rule as interior interpolation. At interpolation progress0/1 or accumulation count0, OR conservatively keeps provenance from a zero-weight operand; the reviewed normative contract does not require clearing it. Extrapolation and arithmetic corner cases are not proved here.

Actual complete `composite_endpoint`, `accumulate_endpoint`, and `compose_animation_segment` were inspected in the retained glue source. Endpoint add/accumulate uses the underlying value as first operand; endpoint accumulate has count1. Iteration accumulation executes only for positive count. Their existing fallback selection does not change. Final interpolation failure selects an original/composited endpoint by the existing midpoint branch; zero-length intervals select by total-progress sign. Neither path calls the changed metadata construction after a failure. Universal/string/noninterpolable components and payload provider failure retain their existing discrete path.

This is a source review, not a compiled full effect-stack refinement. A source-shaped small proof will cover the wrapper and admitted observer, with numeric providers and scheduling explicitly external.

## Necessary WPT

`registered-number-interpolation-attr-taint.html`: 24 fixed-oracle tests (8 static calibrations,16 interior animated samples). Four endpoint combinations × .25/.75 × whole-bundle/direct URL observers. Actual effect, progress, numeric payload and URL are checked. No support skips or zero-weight ambiguity. Node registration verified syntax and unique test names without invoking browser callbacks.

The preceding40-case root diagnostic reported37PASS3FAIL: clean-to-tainted whole-bundle at .25,.75,1. All control/calibration assertions passed. The compact landing fixture intentionally drops endpoints; root owns its baseline/candidate pair.

## Standalone prerequisite assessment

Root supplied `value.upstream.rs` for base976279105b2e78b8666a959eb3f25c9176cefaf8 with SHAa86c48b68b7cf373aa1b0039af2be1ad926bd50b57e39adf4c4b622272ba0d0c. Comparing the complete file to the local original found only the public visibility/documentation change for `CustomAnimatedValue::from_computed` and added `is_attr_tainted` getter. The wrapper, interpolation and CSS-wide initial/inherit provider bodies are identical. The one-line repair requires neither addition.

The fixture uses CSS-wide initial/inherit, not raw attr()/var() keyframe endpoints, so it does not need the prior keyframe-provider conversion repair. It uses fresh targets and distinct initial12/inherited8/interior9-or11 payloads, avoiding equal-payload map publication and endpoint/base invalidation shortcuts. Both endpoints are explicit replacement values; no neutral endpoint or underlying-value composition is required. Static calibration verifies inherited taint and both observers. This is a source-based prerequisite argument, not an isolated upstream execution claim.

No global value equality, URL-data policy, map publication, cache invalidation, FFI or C++ changes are proposed. The minimal native/WPT package is two files.
