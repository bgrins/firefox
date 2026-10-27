# Transition endpoint descriptor regression proposal

This proposal tests an internal metadata invariant in the applied endpoint prototype. It does not establish a new observable browser defect or add accepted-fix credit. No live source was changed and the new test has not been compiled or executed.

`tests.patch` extends the real `KeyframePresentation` fixture and adds one test-only Rust observer. `native.patch` is separate and byte-identical to the previously reviewed one-line correction: clear `mFromEndpoint` after replacing the concrete start value. Apply the test patch alone for the red run; only then apply the correction for the green run. The selection requires both named tests to execute, not merely a successful process exit.

The existing `KeyframePresentation.LiteralOpacity` body is unchanged. Its actual calibration log records `TEST_START: KeyframePresentation.LiteralOpacity` and `TEST_END: PASS`; root subsequently completed preservation and committed that fixture as `73a62b1ecf58b5edc9c214f38b7701a0c16bfb4a`. This supports using the presentation setup, not the correctness or compilability of this new extension. References pin the log and postcommit epoch. Bind the experiment to a fresh execution receipt rather than treating this proposal as activation.

## Test observations

`TransitionConcreteEndpoint` creates two literal opacity keyframes, 0.2 and 0.8, through production parsing, `SetKeyframes`, and presentation-backed keyframe computation. It retains both actual descriptor Arcs and the to-value Arc externally. The Rust observer checks the retained declaration, selected longhand, keyframe index, declaration index, and identity within the owned context through public descriptor methods. Its assertions report through the existing GTest failure bridge; the observer does not construct replacement descriptors or evaluate a separate model.

The real `ReplaceTransitionStartValue` receives a genuine `Servo_AnimationValue_Opacity(0.4)` value. The test checks non-null concrete from value 0.4, a cleared from descriptor, the unchanged to descriptor and to-value pointer, and unchanged 0/1 offsets. The null-descriptor expectation is deliberately nonfatal, so the red run can continue through all numeric controls. Recomputing the effect's stored keyframe input verifies the synthetic declaration was updated to 0.4 while its other endpoint remains 0.8. This separate computation does not call `UpdateProperties` or repair the effect under test.

Production `Servo_ComposeAnimationSegment` must compose the explicit 0.4/0.8 segment to 0.6 at progress 0.5 even when supplied underlying 0.1. A second effect built from only an offset-one 0.8 keyframe must have a genuinely implicit null from value and null descriptor; the same native composition call must produce 0.45 using underlying 0.1. Thus a missing descriptor is not treated as implicit when the concrete value is present. Finally, after releasing the first effect, the externally held original descriptors must still describe 0.2 and 0.8.

## Source and ownership boundaries

The test-local subclass exposes only the protected input array as a const reference. Production headers and public APIs are unchanged by the test patch. `GetComputedKeyframeValuesFor` accepts that const array. `AnimationValue` owns a `RefPtr<StyleAnimationValue>`; `Servo_ComposeAnimationSegment` borrows its segment and values, and its returned strong reference is consumed into a `RefPtr`. The descriptor observer borrows the opaque pointer only during the C++ call while a strong C++ reference remains live. It uses `Opacity::from_computed_value` solely to check the already parsed literal declaration, not as a provider/defaulting oracle.

The original transition construction can already use declarations synthesized by uncomputing a concrete value. Clearing the obsolete descriptor does not reconstruct authored `var()` syntax or discard the replacement `AnimationValue`. The proposal tests literal opacity ownership and classification only: custom-property taint/URL metadata, actual compositor-driven transition replacement, future recipe admission, and current-provider resolution are outside this test. A future adapter must classify non-null value plus absent descriptor as explicit concrete, not as an implicit endpoint or a failed-recipe fallback.

## Validation and remaining gates

Both patches independently applied and reversed exactly in an owned temporary tree, which was removed. The native patch matches the prior proposal hash. New C++ and Rust sections were formatted; the existing calibration body and Rust host body remain byte-identical. Actual source/API pins and patch hashes are retained. No compiler, linker, browser, native test, live preservation checker, or index operation was run.

Required next evidence is the red run against uncleared production metadata, followed by the same selection with the one-line correction. The red result should isolate the nonfatal descriptor-null expectation while recording completion of the numeric and ownership controls. Unexpected setup, API, or assertion failures require diagnosis rather than being credited as this regression. The green run must execute both tests and report zero failures. Native compilation remains the decisive check of the new test-only subclass and Rust/C++ symbol linkage.
