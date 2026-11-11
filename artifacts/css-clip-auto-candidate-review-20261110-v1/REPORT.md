# Independent clip-auto candidate review

Verdict: **no blocking source finding; proceed to the real binding/build and baseline-matched runtime gate.** Reviewed native patch SHA-256: `5e85b5ad7ab7279cf2d7a1594cd5bf0aa32fbce495c28d7d65e466837c5040f5`. This is not runtime acceptance or an added bugfix count.

All 19 pinned source files were independently authenticated against Git revision `d68b16b121b4fdcc8c783f8a14fc41a6218f8e46`. The candidate checker was inspected and replayed with Git validation: three-file forward/reverse patch checks, C++ name-only correspondence, arithmetic-only helper calls and the author's finite model passed. `REVIEWED.json` binds the exact reviewed source/candidate/report inputs; `native-check.log` retains the source check. The Python finite model is not used as a Lean proof.

## Native behavior and callers

`ClipRect::animate` retains component order and underlying component operations. The only removed operation is the old non-interpolation guard that rejected a successfully animated auto component. Shared CSS Add/Accumulate can therefore preserve matching auto components while composing lengths. The early mismatch failures still come from the derived LengthOrAuto operation. Interpolation is unaffected in the shared rectangle operation because the old closure already bypassed its guard for Interpolate.

The private SMIL helper first runs the same AnimationValue arithmetic and returns null on failure. It then rejects only `Clip(Rect(...))` containing auto before allocating the Arc. All-numeric clip, successful non-clip results and outer `Clip(Auto)` survive unchanged. Outer auto versus a rectangle still fails through the existing variant mismatch. It is incorrect to use SMIL from-by auto/auto's no-effect rendering as evidence that the low-level outer-auto arithmetic failed.

The helper has exactly two callers, passing Add and Accumulate. Its Rust parameter can express Interpolate, but the relocation's compatibility claim excludes such a future call. Applying this final guard to interpolation would reject values that the old shared implementation accepted. Retain the arithmetic-only caller restriction when changing this helper later.

Independent global Searchfox discovery finds the two Rust definitions, two generated declarations and one C++ call for each export, both in `SMILCSSValueType::AddOrAccumulate`. This agrees with the author's pinned local consumer audit. The native branch uses CSS composite/iteration helpers that call AnimationValue.animate directly; they do not pass through the plural SMIL exports. Renaming those exports makes the compatibility policy explicit at their existing callers.

cbindgen exports functions and its pinned configuration contains no old-name manual declaration or exclusion requiring a parallel edit. The payload generator uses `base_type()` for animated types rather than the boxed specified-property storage type. Together with CSSPixelLength's self animated type, this is consistent with the candidate ClipRectOrAuto match. Actual generated bindings, concrete Rust pattern types, C++ declarations and link references remain a real build gate; no mock compiler result is claimed here.

## Short-circuit and arithmetic premise

Relocation changes evaluation after an early auto: later components can now be computed before the final guard rejects. Result equivalence requires these component computations to be pure and total. For the concrete chain, the pinned types reduce to GenericLengthPercentageOrAuto<CSSPixelLength>. The derived Animate implementation rejects unequal discriminants, preserves equal fieldless Auto and otherwise calls the scalar operation. CSSPixelLength contains CSSFloat/f32. Its animation delegates to f64 weighting and clamp/cast; the inspected code has no author callbacks, mutable external state, allocation, integral division or explicit panic.

This source analysis supports the concrete pure/total premise. It is not a formal proof of floating-point instructions, trapping modes, compiler behavior or arbitrary future Animate implementations. The extra work is at most the remaining rectangle components. Result equality does not assert identical timing, evaluation count, traces or performance.

SMIL count zero has no bypass in SMILValue::Add. The candidate keeps count propagation and arithmetic admission, so a rectangle with matching auto components remains rejected even at count zero. The current SVG repeat path's first iteration may bypass the low-level call; that browser observation cannot replace direct count-zero coverage.

`FinalizeServoAnimationValues`, both-null refusal, zero conversion, property exclusions and destination-wrapper setup retain their exact order. The C++ file is token-identical after reversing the two export names. In particular, finalization can update/create a wrapper before subsequent arithmetic fails; the guard was not moved ahead of that mutation. Multi-value/shorthand partial updates and null-result handling remain in the original loop. No new rollback guarantee is claimed.

## Universal Lean result

`Guard.lean` is a standalone model using only Std. Its component functions are arbitrary total pure `Unit → Option (Component α)` computations with uninterpreted length payloads. `rectangle_guard_relocation` proves equality between the old per-component guard and a final rectangle guard for all four computations. This is universal over payloads and failures; it is not enumeration of sample numbers.

`arithmetic_compatibility` lifts that result to an explicitly arithmetic-only interface with Add and Accumulate. Counts are arbitrary naturals, including zero; the count merely indexes the supplied component computations, so the theorem covers every native u64 count without asserting a numeric formula. Separate constructors and theorems preserve outer auto, arbitrary non-clip success/failure and top-level mismatches.

`preparation_order_preserved` composes the equality with the same abstract preparation/state-update function. `prepared_state_preserved` and `failed_preparation_preserved` retain the already-prepared state and failure. This captures why moving the native guard before finalization would be a different change. It does not implement or prove the native hashtable, zero conversion, wrapper allocation or full SMIL loop.

Fresh source-only validation passed **14 theorem axiom audits and four exact false-claim rejection controls**. Only standard `propext`, `Quot.sound` and `Classical.choice` are permitted. The controls reject omitting the SMIL guard, rejecting outer auto, introducing a count-zero shortcut and rejecting numeric clip rectangles. They are kernel-rejected false claims about modeled alternatives, not native implementation mutants. `proof1/REPORT.json` pins all sources, toolchain fingerprints and logs. Temporary compiled output was removed.

The model does not include Interpolate in its operation type. Native-to-Lean correspondence, purity/totality of actual compiled component operations, IEEE arithmetic, allocation and FFI behavior remain explicit assumptions. The theorem closes the abstract guard-relocation argument; it does not convert source inspection into a whole-program proof.

Reproduce with a new output path:

```sh
python3 -B artifacts/css-clip-auto-candidate-review-20261110-v1/check.py --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean --out /tmp/clip-guard-review-new
```

`SOURCE-ONLY.json` lists the three proof/checker/toolchain-manifest files. Each run copies Guard.lean into fresh temporary storage and compiles it without prebuilt project modules. Toolchain fingerprints cover the Lean binary and Std umbrella source/object, not a hermetic audit of the complete installation.

## Contract and acceptance limits

The earlier CSS trace supports changing matching-auto CSS component arithmetic; its separate SVG/SMIL trace leaves the mixed keyword/numeric host-integration question inconclusive. This review preserves that distinction and does not reinterpret established SMIL behavior as a settled new SVG normative rule. CONTRACT-INPUTS.json authenticates the reviewed traces; no new latest-spec scan was performed here.

The candidate still needs regenerated binding/type validation and browser baseline comparison for CSS addition/accumulation, existing iteration composition, SMIL from-by/from-to, repeat, sandwich and zero-finalization cases. Debug/assertion coverage remains necessary. The direct count-zero FFI branch has source/model coverage here, not a native API test result. No browser, native build, live source, WPT, Git index or commit was changed by this review.
