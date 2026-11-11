# Direct missing-pseudo driver source review

No remaining source blocker found for the isolated cumulative build and runtime experiment using driver v2 patch 24f2b2902305a3488a0f0e2b7270a5ec6e4aa16c2907d2d0faf9834a19c6bedd, over query-input patch 29390ea55c62ceefb36395a0a0657c26600a859991d937caa97f437a754b3757. This is independent source review of the sibling-authored driver. It is not native compilation, successful fixture calibration, a public CSSOM repair, or a waiver of the final missing-pseudo debug gate.

The 43 inputs in source manifest 085449bf8dbcb1036497f6693b7854703f94cbace53c37e8283737117959dc87 authenticate. The author checker was independently replayed into this review capsule: 11 basis files, deterministic copied generation/formatting, exact forward/reverse patch, XPIDL syntax, manifest parsing, inert JS, assertion inventory, scoped ESLint and prettier all pass. XPIDL type resolution and C++ compilation remain unrun. Full unmodified ESLint must run after reversible fixture installation; the source-only check disables import-globals because its target path is absent.

## Resolved source finding

The original v1 State aggregate attempted to initialize OwningAnimationTarget directly from GetAnimationTarget(), which returns NonOwningAnimationTarget. The types provide no such implicit conversion; their equality operators likewise do not support the attempted mixed comparison. Pinned AnimationTarget.h confirms the issue. V2 explicitly constructs the owning value from element and pseudo request, then compares those fields. V2-DRIVER-DELTA.diff records only this correction in driver.cpp. Strong element ownership now spans the query as intended. The source-only checks had passed v1, illustrating why those checks cannot substitute for C++ compilation.

## Call and ownership boundaries

The driver validates the composed element/document, longhand property and flush mode. It completes an explicitly requested flush before capturing state, rechecks document/pres-shell identity, holds strong effects/animations/targets/timelines, and completes raw lazy style resolution before entering the new compositor helper. No EffectSet iterator or lazy resolver borrow spans conversion. Exact membership and effect-to-animation identity are checked before and after the helper calls; selected raw timing fields, ranges, rates, target/request and cascade levels are compared afterward.

Aliased-output and already-owned-output rejection checks precede the real empty/distinct-map request. Their checks include pointer preservation. The two final maps remain request-local, are serialized separately and destroyed; nothing inserts rules into the style engine or cache. Captured-state equality is boundary equality for the named fields, not a full renderer-state hash, proof of no intermediate mutation, or guarantee against arbitrary reentrancy. If the pre-call membership check fails, the diagnostic still calls the helper and ultimately reports stateUnchanged false; its runtime gate must reject that result, not interpret subsequent map values as coherent evidence.

Raw style is deliberately used for both base and endpoint inputs only under the stable-provider fixture assumptions. This cannot establish correctness when the queried pseudo's custom properties/font/providers are themselves animated. RefPtr ownership does not prove same-sample dependency coherence. No public getter hook, transient recascade, cache/visited integration or important-rule precedence is covered by this driver.

## Reachability and interpretation

Thirteen tasks contain 208 required assertions: 150 diagnostics, 20 setup, 36 result, two preservation. Simple held arithmetic covers explicit and implicit endpoints, changed base, relative inherited context, additive order, retarget/cancel/property replacement and invalid/generated admission. The genuine CSSAnimation case requires native identity, exercising CSS completion rather than a nominal WAAPI substitute.

Pending pause is established on an ordinary target before retargeting; native counters require the null-hold/non-null-start wallclock branch. Constant endpoints make its result independent of elapsed wallclock noise, so this verifies branch execution and preservation rather than timestamp accuracy. Held pending play and zero-rate/null-timeline cases remain distinct. Unresolved timeline exclusion requires the actual unresolved/native registration setup; a failed setup is not evidence of a helper defect.

Finite and named-range cases require measured geometry and computed progress; two animation frames are opportunities, not readiness proofs. The named-range case exercises the new owned refresh path, but live offsets may already have been updated. Passing it would not prove that refresh is necessary or distinguish a no-refresh mutant. Both scroll-driven and typed-OM prefs are explicit.

The transition case creates actual CSS transitions, retargets their effects, and asserts native levels. It checks transition-only output and overlapping animation-union suppression, including transition underlying plus additive animation. This is map split/composition evidence, not final cascade insertion. Level or ownership drift must fail setup/preservation rather than be silently accepted.

All assertions and exact messages/expected classes should be retained at runtime. Setup exceptions, missing assertions, crashes and failed diagnostics reject the experiment. Keep the independent 130-record ordinary preservation suite separate from the 208-assertion driver gate. No browser fixture was calibrated during this review.

## Manifest amendment

The runtime capsule adds manifest-order.patch SHA 502672d2d45085c13d1a853a9ec8289936c9309ad0da78e3c11d5306fb32d9b7. Scratch application confirms it only moves the exact unchanged test section before test_mozMatchesSelector; parsed TOML content and all remaining bytes are identical. This review covers that amendment's source meaning, not the runtime orchestration, execution HEAD, restoration or build result.
