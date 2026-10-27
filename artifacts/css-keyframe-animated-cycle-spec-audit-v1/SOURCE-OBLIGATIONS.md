All source observations use the three exact authenticated graph17ac archived bodies in SOURCE-BINDINGS.json. No live source was read. Searchfox was used only to locate symbols; its current positions were not treated as the archived positions.

`Cascade::cascade_custom_property` applies reverted-priority, included-origin and seen-name checks before admitting a declaration. The selected value's references determine whether the cycle walk runs. The Parsed branch currently declares no references. A pending numeric recipe must preserve the winning declaration's identity and priority, rather than letting a lower declaration or a previously computed sample stand in for it.

`visit_value_references` traverses the primary reference using `visit_link`, then decides whether its fallback is actually used. Resolved typed values count as valid; unresolved references do not. Traversing every syntactic fallback would regress the existing short-circuit policy. Pending typed recipes need a representation that cannot be mistaken for an already resolved typed value.

`traverse` pops the whole SCC before the acyclic apply path; `Context::handle_loop` calls `handle_invalid_at_computed_value_time` for custom properties. That function installs the inherited value for an inherited registration where available, or computes the registered initial for non-inherited/root cases; otherwise it removes the map entry. Merely deleting a pending recipe is insufficient if an old value remains available to dependents or can be applied later.

`Servo_GetComputedKeyframeValues` / `AnimationValue::from_declaration` establish a separate endpoint-to-animation-value boundary. Bringing endpoint dependencies into the ordinary cascade walker needs an explicit correspondence between endpoint computations, effect-stack selection, the current sampled provider and property-node invalidation. Existing declaration SCC machinery alone does not establish that correspondence.

Integration obligations:

- Preserve origin/important/revert/seen winner gates; do not add a losing provider edge.
- Preserve short-circuit fallback and registration inheritance/defaulting.
- Distinguish ready numeric, pending dependency, CSS-invalid, and unsupported evaluator/recipe states. Unsupported work must fall back to the established full path or remain explicitly unsupported, not be converted to CSS-invalid to make the scheduler terminate.
- If an animated-cycle invalidation policy is selected, invalidate every participating selected property atomically before downstream reads; prevent a removed recipe from subsequently applying a stale cached value. Explain why this policy follows the spec or an explicit compatibility contract.
- Do not cancel an entire effect because one selected property's dependency fails. Do not use numeric equality with an old sample as independence evidence.

Recommendation: admit and test the three acyclic/ordinary controls first. Keep animated mutual-cycle producer admission held pending the missing bridge. This is a source/spec obligation audit, not a patch, a native extraction proof, a new bug, or an acceptance verdict.
