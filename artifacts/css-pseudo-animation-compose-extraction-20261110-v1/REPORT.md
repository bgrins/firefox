# Explicit prepared-property composition prerequisite

The two-file patch extracts `KeyframeEffect::ComposeProperties` and immediately routes ordinary `ComposeStyle` through it. It supplies the meaningful reusable seam required by the missing-pseudo design: selected-segment/value composition over an explicit property array, base-value table and timing, without effect/rendering bookkeeping. It is not a fix for bug 1615083 and does not add a CSSOM caller.

## Source and change

Basis: `7bc1ed9cde2a3f3f6e8c615125a7cf75c7964f16`. SOURCES.json records six exact Git objects; source/ contains them. candidate/ contains only the modified `dom/animation/KeyframeEffect.cpp` and `.h`. `prepare.py` deterministically derives both candidate files and extraction.patch. Searchfox receipts are navigational evidence, not the local branch basis. Searchfox CLI reported an available 0.20.6 update; installed 0.20.5 remained unchanged.

Before: private member `ComposeStyleRule` reads `mBaseValues` and `mEffectOptions.mIterationComposite`, then calls `Servo_AnimationCompose`. `ComposeStyle` obtains computed timing using the requested endpoint policy, returns when progress is null, selects a segment from each non-skipped `mProperties` entry, calls that helper, then updates overflow synchronization state where applicable.

After: static `ComposeProperties` receives all those value-composition inputs explicitly. It contains the unchanged segment-selection loop with renamed operands and the inlined FFI call. It asserts non-null progress. The existing `ComposeStyle` keeps its exact timing selection and null-progress guard, calls `ComposeProperties` with the existing members, and keeps its exact overflow block. The formerly protected BaseValuesHashmap alias moves to the public C++ section so internal callers can construct an owned scratch map; the member and its explanatory comment remain in place. No WebIDL surface changes.

The helper parameters are output map, const prepared properties, const base-value table, const computed timing, iteration composite mode, and skip set. Endpoint policy has already been applied by `GetComputedTiming(nullptr, aEndpointBehavior)` in the caller: accepting an independent second endpoint selector here would introduce two potentially inconsistent timing inputs. A future query caller must obtain correctly policy-adjusted computed timing before this helper.

## Preserved semantics and contracts

* `Animation::ComposeStyle` remains byte-identical. Unresolved-timeline admission, temporary pending hold-time adjustments and restoration are unaffected.
* `KeyframeEffect::ComposeStyle` still returns before overflow bookkeeping for null progress. With non-null progress it performs overflow bookkeeping even when all properties were skipped or the array was empty, as before.
* Property iteration order, skip membership, segment boundary selection (including coincident offsets), last-segment selection, timing argument and iteration-composite argument are preserved. The segment loop retains its existing assertions and valid-prepared-array precondition; this refactor does not reorder or harden those checks.
* `WillComposeStyle`, last-progress/iteration fields, compositor flags, target registration, property preparation, base-value refresh and restyle requests are untouched. `EffectCompositor` keeps its sorting and cascade masks unchanged.
* The FFI base-table pointer becomes const. The pinned Rust `Servo_AnimationCompose` accepts a shared reference to RawServoAnimationValueTable and reads base values; output-map composition remains mutable. There is no const_cast, allocation of a second base table, copied effect state, or new operation arena.
* The helper has no access to an effect instance. Inputs must remain alive and unmodified for its synchronous call. It does not solve ownership/reentrancy for the future code that will prepare those inputs.

This is output-map composition, not a claim that every operation downstream is mathematically pure: interpolation and existing native FFI behavior remain unchanged. The checked source property is absence of effect-instance reads/writes from the new helper and preservation of the ordinary call path.

## Hoisted-input review

The old helper takes the base-table address and reads iterationComposite for each selected property; the new helper receives them once before iterating. This relies on the existing synchronous, non-reentrant composition contract: the effect, prepared arrays, base table and iteration option stay stable throughout one ComposeStyle call. The base-table object's address itself is stable for the live effect; table contents remain shared read-only input. This is not the broader keyframe-preparation path whose reentrancy remains a final-repair concern.

Inspection of pinned `Servo_AnimationCompose` finds three direct Gecko callbacks: `Gecko_AnimationGetBaseStyle` reinterprets the const table and performs GetWeak; `Gecko_GetProgressFromComputedTiming` reads the supplied progress; `Gecko_GetPositionInSegment` computes a fraction and applies the supplied native timing function. Their implementations are now pinned in `layout/style/GeckoBindings.cpp`. None receives an effect/animation/DOM target or invokes a style flush/script callback in these bodies. The Rust function reads supplied segment/value operands, composes through `compose_animation_segment`, and inserts the resulting value into the supplied output map. Endpoint composition/interpolation consumes animation values, not an effect object. Logging, allocation and reference management remain existing operations.

This supports preserving the ordinary caller under its existing immutable-effect composition contract; it is not a whole-program proof of every interpolation implementation or allocator hook. The existing public header already describes avoiding effect-state mutation during potentially parallel traversal. Future callers must honor the same lifetime and no-reentrant-mutation contract. If such a mutation is discovered, it would invalidate both stable segment references in the existing loop and the extraction's once-per-call iteration argument; investigate it rather than relying on per-property rereads. The debug/native runtime gate remains required.

## Validation performed

`python3 check.py` passes source hashes/Git-object identity, deterministic generation, scratch forward/reverse patch application, exact ordinary timing/null-guard/overflow correspondence, exact segment-loop correspondence modulo explicit operands and the inlined FFI call, and absence of selected effect-state dependencies in the helper. CHECK.json records the result and patch hash. Scratch directories are removed automatically.

These checks are source-level evidence. No candidate compilation, browser execution, native differential test or sanitizer run occurred by this author. A subsequent copied-file clang-format pass split one new header parameter line; cpp was unchanged. See RUNNER.md for the frozen runtime wrapper and formatted patch identity. The source-only patch must pass the runtime gate in RUNTIME-GATE.md before acceptance. A generated-header const compatibility check and C++ access/type validation remain compiler responsibilities.

## How it fits the eventual repair

The future CSSOM request-local orchestration can pass newly prepared properties and fresh base values without publishing `mProperties`, `mBaseValues`, EffectSet masks or overflow state. The ordinary renderer uses exactly that same value-composition implementation now, so the extraction is exercised by existing consumers rather than waiting as unused scaffolding.

It does not make the existing renderer arrays fresh, repair the missing pseudo base-style early return, bypass stale CSSOM caches, construct fresh animation/transition masks, provide a transient pseudo recascade, or establish query-safe timing/preparation. All remain mandatory parts of the final design in `../css-pseudo-animation-design-20261110-v1/REPORT.md`. Provider-dependent endpoint computation, inherited/current contexts, pending/unresolved timeline behavior and no-flush/reentrancy constraints must be addressed in that final repair; they are not silently waived by this extraction. Missing-pseudo failures are expected to remain unchanged here.

No live source, preexisting untracked draft, WPT, build output, browser, Git index or history was changed. Prior deferred-operation/endpoint prototypes were neither adopted nor duplicated.
