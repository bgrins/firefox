# Retain the computation inputs that selected-root sampling loses

This is an uncompiled four-file production transport proposal, not a provider repair. It preserves the ordered segment endpoint inputs of each successfully composed custom property in the actual normal animation-rule owner. Public `Servo_AnimationCompose` and commitStyles remain unchanged. Pending recipes remain disabled (`FrozenAnimationRule<Infallible>`); no resolver error is converted into a cached value, initial value, or dropped winner.

## Concrete counterexample to the current input boundary

`KeyframeEffect::ComposeStyleRule` currently sends only the selected segment and the last segment to `Servo_AnimationRuleSample_Compose`. With keyframes at 0, .25, .5, .75 and 1, sampling at .125 selects the first segment. Changing only the .5 declaration from a literal to `var(--provider)` leaves both transmitted segments identical. Changing it to `var(--x)` likewise leaves the transmitted inputs identical. `WITNESSES.json` records these two pairs without assigning a cyclic numeric oracle.

The cached arithmetic roots therefore cannot reconstruct the full materialized keyframe computation inputs. An endpoint descriptor owns one keyframe context, not the whole effect's other keyframes. Its keyframe index is local to that computation; it is not a global identity from which the missing context can be recovered. This is an information-loss counterexample, not evidence that an unselected cycle must invalidate the selected result. The exact cycle/defaulting owner remains INCONCLUSIVE in the pinned cycle review. It also does not prove that every retained endpoint must be recomputed on every sample.

## Implemented handoff

The normal C++ call additionally passes the property's complete materialized segment array. While that array is borrowed, Rust retains its endpoint inputs and offsets in order. A null value is `Underlying`; a non-null value without a descriptor is `Concrete`; a descriptor-backed value is `Authored`. This preserves the transition-start correction's distinction between a synthesized concrete value and an implicit endpoint. Authored entries retain the original descriptor, not a numeric substitute.

Native RefPtr payloads already originate from servo Arc allocations. `Arc::from_raw_addrefed` retains an owned reference before the C++ borrow ends. No C++ array pointer, effect pointer, raw lifetime, or newly tagged pointer escapes. Shared contexts stay shared through descriptor Arcs. Offsets and repeated endpoint occurrences remain ordered; there is no numeric-equality or provider-key deduplication.

The vector is appended only after the existing composition operation reports insertion. Later replacement of a property's arithmetic root does not delete earlier composition-call input groups. Groups identify property and call order; they do not yet identify individual arena nodes or establish a winning-effect computation scope. The owned vector survives normal `into_rule_source` publication alongside the existing concrete rule. The legacy concrete-only `into_declaration_block` still materializes concrete values and drops auxiliary inputs; it is not a permitted future pending publication route.

## Still required for the four observed provider failures

This change does not fix them. The current normal producer still uses cached endpoints. The existing endpoint resolver requires a complete current provider snapshot and cannot recursively request a pending winner. The real cascade still returns `Arc<ComputedValues>` and has no incomplete completion owner. Ordinary custom-property SCC invalidation cannot simply be reused as animated final-property invalidation without settling the endpoint/final-property boundary.

A complete next integration must connect real source iteration and priority/revert/seen admission to an owned pending winner table, distinguish a pending provider before typed/absent-map shortcuts, and finish dependency resolution before cache reuse or final style publication. Endpoint computation must use current registrations, prepared typed attributes and isolated current context, with tracker/cacheability effects accounted for. Inputs retained here must be associated with operation roots and the chosen computation scope; skipped/filtered declarations and effects that never enter this composition call are not recovered by this patch. No branch may publish inherited/initial values merely because a pending item was collected.

The observed unregistered literal provider switching from `20` to `red` provides a useful first vertical test: all four existing registered-consumer histories must compute the red-phase endpoint default of 10 rather than reuse 20. That witness cannot establish arbitrary animated cycles, unsupported declaration kinds, or full pending-provider semantics. Dynamic implicit-underlying freshness also remains INCONCLUSIVE; this proposal does not change it.

## Costs and validation limits

For each successful custom-property composition call this copies O(segment count) offsets and owned Arc references into an additional vector. Repeated endpoints and lower overwritten effects are retained. Ordinary longhands do not allocate this vector's entries. This is a deliberately visible experimental representation cost, not a performance or landability recommendation. Existing shared-owner memory-reporting gaps remain; no complete accounting or pruning is claimed.

`check.py` authenticates the four pre/postimages and prior evidence, proves the two finite input projections are identical while their full lists differ, verifies the unchanged public glue suffix, and applies/reverses the exact patch in disposable scratch. Those are source/transport checks, not native semantic tests. Formatting was restricted back to the changed code after an initial Rust 2021 invocation rejected existing let-chain syntax; the changed Rust was formatted using edition 2024. No compiler, browser, native test, live source edit, index operation, or canonical-library operation was run.

Before application, generated FFI signature compilation, actual host ownership tests and current preimage validation are required. This package is neither an accepted CSS bug nor a complete animated-provider implementation.
