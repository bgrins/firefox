# Provider and lifecycle boundaries

## Bound source interfaces

The before/candidate position/flag statements, full FinishReflowChild, both ApplyRelativePositioning overloads, GetNormalPosition and GetLogicalNormalPosition, both logical/physical point conversions, final LogicalRect::GetPhysicalRect and relative RestyleManager cache/update statements are extracted from pinned snapshots. EXTRACTIONS.json records exact slice hashes. Actual IEnd/BEnd are additions before container subtraction; they are not replaced by algebraic cancellation. The before selection/finish slices are independently extracted from the genuine baseline source. All six actual helper callers use Default. The frame-aware relative predicate excludes SVG text and implies the downstream relative-or-sticky predicate and relative style.

The arbitrary actual returned physical size is installed before normal-coordinate conversion. Current offset and previous offset are independent: the model accepts the current ReflowInput's physical margin output, not an invented previous=current identity. The predecessor's normal property is optional; absent property explicitly reads used position. The proof does not silently turn that fallback into a correct unshifted origin.

## Explicit provider contracts

- The native calibration facade supplies a current ReflowInput physical margin vector. Real ComputeRelativeOffsets resolves auto/percentage/inset constraints in the containing-block writing mode, stores ComputedOffsetProperty and sets current logical offsets. LogicalMargin conversion returns physical margins. This complete numeric style-resolution algorithm is retained as source but not formally reimplemented; no arbitrary-percentage conformance theorem is claimed.
- ReflowChild is the producer of actual ReflowOutput size and can modify frame state. Selection of the local normal inline coordinate occurs before that call. The model takes the frozen local coordinate and arbitrary actual returned size; the extraction facade skips the actual child callback and supplies that output. It does not assert callback purity or previous/current size equality.
- Frame identity, valid nonnull previous-in-flow, normalized lists, live objects and unchanged style/applicability during the synchronous selected call are engine invariants. Allocation, reparenting, style mutation and lifetime are not proven by integer theorems.
- FinishReflowChild's post-commit DidReflow callback is a recording no-op in native calibration. Retained base DidReflow clears state and invalidates observers; its percent-size callback requires no previous-in-flow and is therefore excluded on the true-OC path. The indexed overrides schedule scroll or XUL work. Source review found no direct position/normal-property setter in these bodies, but arbitrary external observer effects and deferred lifecycle are not modeled.
- Native SetRect additionally manages retained overflow storage and display-item invalidation. The calibration exercises its exact logical-rect geometry conversion, but replaces those object/observer side effects. Actual local child overflow rectangles and later ancestor unions are upstream/downstream state, not fabricated as zero to claim complete observer closure.

## Numeric domain

ExecutedDomain explicitly requires each executed subtraction, addition, logical inversion and final rect end sum to fit signed32. The kernel additionally derives all these requirements from a sufficient domain: each container/previous/returned size component in [0,1000000] app units and normal/offset components in [-1000000,1000000]. Those bounds are sufficient hypotheses, not a universal CSS or callback range guarantee. All ordinary extracted calibration rows satisfy them. They do not cover all possible native inputs.

A retained before/candidate UBSan witness uses a representable logical start2147483647 plus size1. Final mathematical position is−1, but IEnd overflows before container subtraction. It refutes safety from final-result fit alone and is a preexisting source limitation, not a new observed browser regression or independent bug count.

## Skip and cache lifecycle

The model proves every executed repaired continuation step initializes its own normal property, arbitrary finite repeated steps keep a property, and later eligible relative updates preserve it. It does not prove every actual continuation necessarily executes that step after every reparenting/style/dirty transition. Skipped or eligibility-rejected children preserve existing native behavior. A missing predecessor property remains a real prerequisite boundary: if used position is shifted, fallback may carry that shift. Initial ordinary-fragment positioning establishes normal properties through other layout paths; their complete caller/lifecycle proof remains open. No blanket provider admission turns these cases into accepted full-scope verification.

These boundaries permit a bounded source-correspondence theorem and native recommendation, while full lifecycle/all-caller closure remains HOLD. FORMAL-SCOPE.md preserves every original obligation without replacing them with audit counts.

## Tool installation boundary

Replay pins the Lean and clang executable hashes and uses their installed standard libraries/SDK. It is a closed source capsule with explicit external tool installations, not a vendored hermetic operating-system/toolchain image. Allowed-axiom checks reject added assumptions and sorryAx; native UBSan is executable evidence, not a proof of compiler correctness.
