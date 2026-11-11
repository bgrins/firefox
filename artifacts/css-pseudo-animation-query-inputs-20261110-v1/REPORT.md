# Request-local missing-pseudo animation inputs

The copied candidate implements the next concrete preparation and composition stage for bug 1615083. It captures query inputs, refreshes owned offsets, regenerates CSS endpoints, builds fresh properties/base values/masks and produces separate animation- and transition-origin maps. It does not install a CSSOM caller or recascade those maps, so it is not a bugfix acceptance or a claim that the missing-pseudo tests now pass.

## Patch basis

Source revision: `3f8f7324c20de730eddcf07b224dd93e9be6694d`. `SOURCES.json` authenticates 25 source files; `SEARCHFOX.json` contains discovery receipts. Searchfox 0.20.5 reports 0.20.6 available; tooling was not updated. Exact branch sources govern the audit.

`prerequisite/` applies the previously reviewed composition extraction and owned-generation patches in `PREREQUISITES.json`. Those proposals remain research, so `candidate.patch` cumulatively changes eight native files from the pinned production source. `query-inputs.patch` is the four-file incremental change over those prerequisites. Do not stack the cumulative patch on either prerequisite. `ROLES.json` pins all three versions. Existing accepted source comments and helper bodies are retained except the explicitly shared timing selection.

## API and preparation sequence

The only new public entry point is `EffectCompositor::ComposeServoAnimationRulesForMissingPseudo`. It takes an exact owning target, distinct unanimated-base and endpoint styles, and two empty `UniquePtr<StyleAnimationValueMap>` output references. It rejects nonempty or aliased output references and allocates both maps internally only after preparation completes. All false returns precede output allocation.

Admission requires the dynamic matching pres context, non-null styles and target, and one of `::before`, `::after` or `::marker`. Both supplied styles must have the requested pseudo type. A currently generated pseudo is rejected, preserving its ordinary rendering/query path. Before conversion the code checks each effect's target element and full pseudo request, its animation identity and its animation's effect pointer. Style objects do not encode their originating element identity; their association with this exact target remains a caller premise, not something inferred from a strong reference.

The helper first copies strong effect references out of the EffectSet and releases its iterator, then sorts by the existing composite-order comparator. It captures strong animation/timeline references, the range, specified keyframe inputs, CSS generation options, iteration-composite mode, cascade level and computed timing before entering any property-value conversion. Array order freezes composite order for the request. It calls the owned `RefreshComputedOffsets` during this capture phase. Later `BuildPropertiesFromInputs` therefore generates fresh endpoint arrays from those refreshed offsets, using the explicit endpoint style.

No completed endpoint array is cached in the input snapshot. No frame pointer or EffectSet iterator spans value preparation. Strong ownership protects lifetime; it does not freeze mutable declarations, animation state, parent style or provider state.

## Timing selection

The private `Animation::GetHoldTimeForComposition` helper retains the original pending guard, null-hold/non-null-start admission, wallclock-timeline test, null conversion handling and playback-rate conversion. Ordinary `Animation::ComposeStyle` still uses its AutoRestore scope, identical effect/unresolved admission, ordinary effect composition and pending-state postcondition. It assigns the helper's result to the temporary live hold value as before. With the default argument, `TimeStamp::Now()` is evaluated only in the same wallclock branch as before.

The query calls that same selector with one captured timestamp, then feeds the returned hold value to the existing read-only current-time calculation. It never assigns live hold/start/pending state and does not tick, trigger readiness, or update the timeline. Unresolved timelines retain null progress, including when a hold value exists. Endpoint behavior is Exclusive; commitStyles' Inclusive policy is not reused.

Query timing parameters are copied from specified timing and normalized against the current cached finite timeline/range duration. The resulting computed timing is stored before conversions. `AtTimelineBoundary` and current-time reads occur in this same capture phase. This supplies owned results for that observed context; it does not prove the cached provider snapshot is fresh. Document timeline getters read refresh/navigation timestamps. Scroll/view mapping reads cached timeline data. None of the inspected getter bodies advances the refresh driver or pending animation state.

The source checker establishes correspondence of the shared branch and restoration of the ordinary caller modulo its helper call. This is source-level evidence under the existing synchronous composition contract, not a machine proof of native floating-point behavior, thread safety, or arbitrary reentrant mutation.

## Fresh base values and cascade masks

Properties are rebuilt into request-owned arrays. The helper extracts one base value for each property in the combined prepared union from the supplied raw base style using `Servo_ComputedValues_ExtractAnimationValue`. This avoids the renderer's `EnsureBaseStyle` early return when no generated pseudo exists. It does not call `GetBaseContextForElement` or read the effect's stored base table.

The animation-level property union is derived from newly prepared arrays and captured cascade levels, not `EffectSet::PropertiesForAnimationsLevel`. The animation-origin map composes all sorted effects with the complement of that union skipped, retaining transition values as possible underlying inputs for animation composition. The transition-origin map includes transition-level effects only and skips the animation-level union. Null-progress effects contribute no sampled values. These are the existing composition-level skip rules applied to fresh query inputs; they do not directly overwrite computed style fields or bypass important rules. The future transient recascade must insert both maps at their proper origins.

The common explicit `ComposeProperties` helper performs segment selection and value composition. Query work does not call renderer `UpdateProperties`, cascade-result updates, `WillComposeStyle`, restyle requests or bookkeeping publication. Attribute-reference tracking from value conversion is local and discarded; the future CSSOM result must be request-local rather than persistently cached on that basis.

## Unresolved caller contracts

1. The base style must exclude this target's own animation and transition rules while preserving appropriate inherited state, including ancestor animation effects. The endpoint style must supply the correct current providers. Passing raw base style for both is not established for animated custom properties, fonts, relative/logical units or other same-sample dependencies.
2. The two styles, origin/parent style read by keyframe conversion, container/query context, attributes, timeline cached state and sampled effect inputs must describe one coherent request. Ownership alone does not establish that relationship. `Servo_GetComputedKeyframeValues` still reads current parent ElementData and container context during conversion.
3. Lazy-resolution Rust borrows must be released before this method, and preparation must not reenter mutation of captured target/animation/provider state. The inspected direct conversion chain uses local result arrays/contexts and scoped borrows; this is not a whole-program no-flush/no-script theorem. There is no retry loop or convergence assertion.
4. The final CSSOM admission, disconnected/flat-tree/printing handling, generation-cache bypass/cancellation clearing, visited handling, and pseudo-aware transient recascade remain unimplemented. This helper is not exposed to JavaScript and has no production query caller yet.

These are explicit gates for the future caller, not policy choices silently resolved by this candidate. In particular, this stage does not invent a fixed-point algorithm for provider-dependent endpoints.

## Validation and next gate

`python3 -B check.py` passes Git/source authentication, prerequisite reconstruction, deterministic clang-format generation, forward/reverse incremental and cumulative patch replay, ordinary pending-selector correspondence, phase ordering, identity/fresh-map checks and absence of selected renderer publication calls. These checks are structural; they do not replace compilation or exercising the query API. No live native/WPT source, app, build, canonical library or Git state was changed. No native build, browser run or formal native-refinement proof was performed.

`fixtures/` retains the exact original 20 CSSOM-lifetime and nine underlying-value controls from the signed owned-generation experiment, authenticated in `TESTS.json`. They are unchanged and no expected-failure metadata is introduced. The existing optimized 130-record preservation vector remains the ordinary-path baseline; this candidate has not run it. Its new hold-selector extraction additionally needs pending play/pause, held/zero-rate, unresolved timeline and finite-range boundary coverage.

Root's next gate is source review and real compilation of the cumulative candidate, including UniquePtr/binding compatibility, followed by ordinary-path preservation. That alone cannot accept the unused query path. A direct query driver or the subsequent explicitly reviewed CSSOM caller must exercise fixed/implicit/additive values, transition/animation overlap, retarget identity, range refresh and provider-style inputs. Preserve the missing-versus-generated split in the original controls. Final repair acceptance still requires the debug transform-hint traversal gate; this preparation stage does not waive it.
