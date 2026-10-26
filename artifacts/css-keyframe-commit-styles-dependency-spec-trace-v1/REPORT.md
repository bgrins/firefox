# commitStyles: partial consumer stack, current provider context

**Verdict: REACHED for the scoped acyclic case.** Committing the consumer restricts its effect stack; it does not restrict the separately animated provider's computed context. This resolves the semantic question for the proposed numeric repair. It does not establish an implementation or a new observed defect.

Scenario: a rendered ordinary element; distinct registered `<number>` properties `--provider` and `--consumer`; separate paused WAAPI effects with explicit replace endpoints, interior progress and no cycles. The consumer alone is committed. No registration change, transition, additive composition, implicit endpoint or multi-property commit is involved.

## Current specification trace

Manually checked on 2026-10-24: Web Animations draft dated 8 October 2026, Properties and Values draft dated 6 August 2026, Cascade draft dated 13 April 2026. `webspec-index` was unavailable; this is a direct algorithm trace, not an exhaustive indexed route search. SPEC-ANCHORS records HTML-ID checks and fetched-page hashes. The unused `animation-behavior` anchor was absent; no claim relies on that URL.

1. [commitStyles](https://drafts.csswg.org/web-animations-1/#dom-animation-commitstyles) invokes [commit computed styles](https://drafts.csswg.org/web-animations-1/#commit-computed-styles). After the style-attribute/rendering guards, step 2.5.1 copies the stack for the selected property. Step 2.5.3 removes later effects from that copy.
2. Step 2.5.4 evaluates the copy using the target's computed style; step 2.5.5 writes its result. Endpoint-inclusive sampling does not alter our interior-progress example.
3. [Computed keyframes](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes) invoke [property computation](https://drafts.csswg.org/web-animations-1/#computing-property-values), which uses target computed dependencies and requires their computation first. Its note is explicit: “The computed values on element are not affected by this algorithm.”
4. [Registered substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) supplies the provider's computed value. [Cascade precedence](https://drafts.csswg.org/css-cascade-5/#cascade-sort) places important author declarations above animation declarations.

The returned partial-stack result is a snapshot, not a live variable reference. A later provider change must not alter the committed inline number after effects are cancelled.

The distinction follows the identities of the algorithm's operands: `partialEffectStack` belongs to `--consumer`; the dependency lookup belongs to the target's computed `--provider`. A later provider is not an entry in that consumer stack. A later consumer is. Thus higher provider order remains relevant to dependency resolution while higher consumer order remains excluded from the committed output. Important provider declarations participate in the provider's own cascade; the repair must not manufacture an animation-only provider context.

| Rejected interpretation | Reason |
| --- | --- |
| Resolve providers from a global prefix ending at the committed animation | Applies a per-property truncation to a different property's dependency context. |
| Copy the target's final computed consumer | Includes a later consumer effect which the partial-stack operation excludes. |
| Serialize the retained `var()` recipe into the inline declaration | Preserves a live dependency instead of the computed snapshot. |

This verdict does not decide cyclic dependencies, multiple committed properties that depend on one another, missing/additive endpoints, unsupported recipe types, or all public serialization routes. They remain separate design obligations. No claim of interop consensus is made.

## Exact archived source correspondence

SOURCE-BINDINGS authenticates the feasibility audit's eight Rust bodies under graph17ac, the archived EffectCompositor body, and the retained clean-base Animation body. The latter is historical source evidence, not a newly measured installed-source pin. Searchfox path discovery confirms the current identifier; its definition-context fetch failed with an upstream GitHub 404, which is not treated as source evidence.

`Animation::CommitStyles` holds its effect alive, flushes frames, checks rendering, requests `ComposeServoAnimationRuleForEffect`, then loops the committed effect's property set. It retrieves each map value and calls `Servo_DeclarationBlock_SetPropertyToAnimationValue` before updating the inline declaration.

`ComposeServoAnimationRuleForEffect` updates cascade results and obtains a strong `ComputedStyle` with `GetComputedStyleNoFlush`, relying on that prior flush. It updates the effect's base style, composes the sorted prefix through the committed effect, and returns the value map. The local style is not passed to `ComposeSortedEffects`. A provider after the committed effect is consequently absent from this temporary map even though it can be present in the full computed style. That is harmless for already-resolved values; it becomes critical if map entries retain recipes.

The archived Rust `Servo_AnimationValueMap_GetValue` clones a map value without context. `Servo_DeclarationBlock_SetPropertyToAnimationValue` calls context-free `uncompute()` and writes a normal author declaration. Neither boundary can currently resolve a pending dependency. Sharing the latter API with SMIL makes silently changing its contract particularly inappropriate.

## Minimal resolution seam

For the admitted numeric replace/interpolate case, add a dedicated internal map-resolution boundary in `ComposeServoAnimationRuleForEffect`, after partial composition and before returning values to `Animation::CommitStyles`. It can receive the already-held full computed style and resolve pending sampled operations against that style's custom-property map. This leaves the consumer prefix intact and avoids passing a target or recursively flushing through public serialization.

The proposed Rust-side contract is: ordinary computed entries are unchanged; pending admitted numeric entries are evaluated using immutable current provider values; the returned map contains only concrete animation values. Pending/invalid/unsupported states must remain distinct. It must not read a provider from the partial map, mutate the computed style, substitute the final consumer, or fall back to a stale cached endpoint. Resolve all relevant entries before any author declaration mutation. A missing style or unsupported operation needs an explicit error policy rather than stale success.

This is missing FFI context/plumbing, not an unresolved choice of provider context for the stated scenario. The remaining implementation premise is substantial: the normal cascade repair must first make the captured full style's providers current, including higher-order and important winners. Calling the resolver against today's stale provider map would not satisfy that premise. Recipe composition also must preserve partial-stack semantics before resolution; this proposal does not establish correctness for additive/accumulative operation trees.

Using a separate internal conversion preserves the existing public `uncompute`/declaration writer contract. It does not settle getKeyframes serialization, transitions, SMIL, taint, registration changes or SCC cycle handling. Those routes must be audited before a general pending-value representation can ship.

## Proposed bounded test oracles

TEST-CASES contains seven proposed cases and calibrated observation rules; no HTML was installed and no browser ran. With provider `200→300` at 0.75 and consumer `100→var(--provider)` at 0.25, the proposed inline result is `143.75` whether the provider is created before or after the consumer. A higher provider giving `450` yields `187.5`; provider `600 !important` yields `225`. A higher literal consumer giving `999` must not change the lower consumer's committed `143.75`. Literal and two-var-endpoint cases provide direct controls.

Save the inline commit result before a computed-style getter. Independently verify provider, ordinary var reference, timing, relative composite order and literal behavior; an incorrect animated consumer is the observation, not a prerequisite that aborts collection. Cancel all effects and change the provider afterward to verify the saved result remains a numeric snapshot. These values are derived from linear interpolation, not measured browser outcomes.

No native/source/index/reference/build/browser mutation, canonical model addition or acceptance occurred.
