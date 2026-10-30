# Typed attr consuming-context dependency plan

The frozen native walker does **not** use every syntactic fallback as a cycle edge. It first inventories attribute references, then resolves dependency primaries and follows only fallbacks classified as selected. The corrected animation-taint proposal adds a consuming-property rejection in substitution, but not in that dependency classifier. Re-evaluating typed attribute text under a non-animatable consumer can therefore select edges the earlier walk skipped. Copying provenance onto the cached final token string cannot recover those edges or the lost inner fallback.

This is an artifact-only analysis of proposal V2 `7ba8f26d`, including its held-provider and fallback-aware cascade changes. SOURCE-TRACE.json contains thirteen exact excerpts; REFERENCES.json authenticates their bodies and the prior design/spec note. Historical `dom.rs` and `properties/data.py` captures support the tracker/dependency explanation; no fresh whole-file branch equivalence is asserted for them. The public Searchfox `prioritary_property_dependencies` lookup independently showed the same line-height → writing-mode dependency, but is discovery evidence, not tested-branch provenance. No native patch, compile, browser run, Git operation or current-state read is part of this package.

## What the existing functions do

| Hook | Consequence for a context repair |
| --- | --- |
| `Cascade::update_attributes_map` | Walks reference fallback syntax eagerly, queries typed attributes through `AttributeTracker`, and inserts raw parsed attribute values. This inventory is distinct from SCC edges and does not recursively inventory every string fetched from an attribute. |
| `visit_value_references` inside `substitute_all` | Calls `visit_link` for a primary before classifying it. Missing/unresolved primary, failed typed parse, absent env, or invalid non-type attr selects its fallback. A resolved animation-tainted var is still classified as valid here. |
| `VarType` / `OrderIndexMap` | Attr nodes are keyed by name and namespace; custom nodes by name. No consuming property or suppression context is part of attr identity. |
| `traverse` | Uses a strong value clone while releasing map borrows, tracks stack/lowlink/self-reference, invalidates SCC members, then performs substitution. Both Attr and Custom nodes pass a custom-shaped property ID derived from the name. |
| `substitute_references_if_needed_and_apply` | Replaces the attr cache entry with a resolved universal value. The original raw expression and its alternative branches are no longer available from that entry. |
| `substitute_referenced_variable` | The typed-attr path queries the actual string but normally replaces it with cached `.css` before parsing. Its Var-only taint guard can reject in a non-animatable property. Recursive unresolved custom values suppress that guard internally, then face the outer Var guard. |

`substitute_all` starts custom roots and then remaining attr roots. That order does not prove a fully settled custom map at every property substitution. `apply_custom_and_prioritary_properties` deliberately interleaves custom resolution and prioritary property application. `ensure_prioritary_property` applies dependencies first; line-height depends on writing-mode. The recursive Var path explicitly handles partially resolved maps. A generic “wait until all custom values are settled, then evaluate attrs” repair cannot simply be inserted at the current consumer call site.

## Repair boundary

Root review rejected pursuing the restricted shortcut below: it could pass the current fixture while leaving the requested general repair incomplete. It is recorded to explain the boundary, not as the next implementation step. The next useful work is the contextual evaluation request integrated with the existing walk.

The smallest directly implementable experiment for the observed WPT is a restricted direct-consumer path: retain/use the already tracked raw attribute string, recognize a typed `<custom-ident>` expression whose primary var is a ready unregistered value and whose fallback is reference-free, and substitute under the actual consumer property/suppression context before typed parsing. Return owned substituted text; do not borrow a newly parsed local buffer. This introduces no new dependency edge for that admitted shape. Keep custom-property consumers, unresolved values, nested attr/env, registered/relative values and all other shapes on their existing route. Preserve attr-security marking on the resulting value and existing missing/parse-failure behavior.

That restriction is a possible prerequisite experiment, **not a complete repair or a proposed landable fast path**: it would leave the new-edge cases below unresolved and must be accompanied by explicit admission checks. Even this path needs an implementation review proving that “ready” comes from the actual value representation and that custom alias resolution cannot accidentally enter it. No implementation or compile evidence is supplied here.

A general repair needs a narrow integration with the existing resolver, rather than a second uncoordinated recursion loop:

1. Preserve immutable raw parsed attr input separately from its resolved result. Thread the consuming property from `maybe_note_non_custom_dependency` (which already has the longhand ID) and the keyframe preparation caller instead of discarding it at `update_attributes_map`. A result cache key must distinguish relevant consumer/suppression and typed-parse inputs; a boolean non-animatable bucket is not established sufficient for `parse_typed_value`.
2. Share primary acceptance logic between dependency traversal and substitution. Resolve the primary, apply the actual Var taint restriction in its consumer context, and only then select/traverse its fallback. Keep custom-reference recursion in custom context; reject the completed referenced value at the outer Var boundary. Do not reject all of Attr, and do not follow all fallback edges eagerly.
3. Preserve SCC participation of custom and non-custom dependencies, including priority application. Context-specific attr results must not overwrite the custom-context result. Conversely, splitting cache nodes by context must not defeat the attribute recursion guard: a re-entry into the same tracked attribute must still obey the attribute guard even if the consumer context differs. The precise interaction between contextual result nodes, existing SCC invalidation and cross-context recursion remains an implementation obligation; a cache-key change alone does not solve it.
4. Route every newly queried attribute, including missing ones and newly selected fallbacks, through `AttributeTracker::query`; retain namespace distinctions and final reference publication. Do not use an untracked DOM read. Retain strong ownership while map mutations occur and keep raw input alive independently of resolved-map replacement.

The central unresolved implementation seam is therefore **a contextual attr evaluation request that can participate in the existing in-progress custom/non-custom walk**. It cannot assume global completion, mutate an already-resolved context-free entry for another consumer, or discard the SCC/attribute guard state. No claim is made that existing APIs already implement this request.

## Required discriminators

| Case | What it must distinguish |
| --- | --- |
| Existing direct-attr WPT: active tainted `--v`, attribute `var(--v, vertical-lr)`, outer attr fallback `vertical-rl` | Select the inner fallback under the ordinary consumer; distinguish whole-Attr rejection and use of cached primary tokens. |
| Same raw attribute also consumed through a custom alias | Preserve custom-reference context independently of the direct consumer. Animation provenance propagation through typed attr remains a separate unresolved spec bridge. |
| `data-a="var(--v, attr(data-b type(<custom-ident>)))"`, `data-b="attr(data-a type(<custom-ident>))"` | The custom-context primary can succeed without selecting the recursive fallback; the ordinary consumer can reject that primary and select a new attribute cycle. This is a proposed structural discriminator, not an executed outcome or a settled CSS cycle oracle. |
| Replace `data-b` with an ordinary ready value, then mutate or remove it | A selected fallback must be queried/tracked and later invalidated; an unrelated cached result must not hide the read. |
| A fallback custom value depending on registered `lh`/font inputs while writing-mode is being applied | Exercise priority/SCC re-entry; reject the assumption that all custom values have completed at the consumer. Exact legal fixture and expected cycle behavior still need separate validation. |
| Valid primary with an unused cyclic fallback; missing primary with the same fallback | Preserve this held branch's selective-edge behavior. Eagerly linking every fallback is not an equivalent implementation. |
| Namespaced attrs, typed parse failure, attr-security URL restriction, inherited/registered values | Preserve adjacent behavior; animation provenance and attr-security metadata must not be conflated. |

The direct ordinary-property interpretation is conditional on the consuming context described in the sealed spec follow-up. This source analysis adds no new normative rule, alias-infection proof, browser verdict, theorem, or accepted native fix. The existing finite context model explains why one context-free final token cannot serve both consumers; it does not prove this native dependency integration.
