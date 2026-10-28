# Contextual easing handoff review

The six-source handoff is suitable for a configured compile experiment with its parser guards closed. It is not ready to activate contextual easing. Five candidate bodies reuse the earlier dependency handoff; the easing body adds the reviewed Resolved/Contextual representation and removes the temporary infallible conversion wrapper. No new proof, browser test, native equivalence or coverage claim accompanies this review.

The selected-rule scope is a concrete missing input. `Context::new_for_animation` supplies same-tree author scope. The late cascade dependency pass instead inherits the last declaration's scope. `Stylist::lookup_keyframes` returns only an animation, dropping both origin and the non-document visitor's containing host. `Context::resolve_tree_counting_result` checks the current shadow order: a positive containing-tree order produces the default index/count of one; same-tree and descendant scopes use the target's tree-counting cache. Therefore the two conversions can produce different numeric values for the same selected easing. Both may still conservatively set dependency flags; this is not evidence that all such flags are missing.

A decisive future test uses a target carrying a part name, with preceding siblings inside a shadow root, and a selected keyframes rule in the outer document. An easing such as `steps(calc(1 + sibling-index()), end)` distinguishes the containing-tree default from the target's actual index. Vary an unrelated final declaration's scope and insert a preceding sibling. Once contextual syntax is activated, both computation and dependency recording must consistently use the selected rule's scope. The present closed guards prevent this from being a runnable activation test or a newly demonstrated shipped bug.

## Proposed scope transport

Return a scoped selection, conceptually `(&KeyframesAnimation, CascadeLevel)`, from a new `lookup_keyframes_with_scope`. Preserve the existing lookup order and keep the old lookup as a projection for unaffected callers. Do not store an element-relative cascade level permanently in the shared `KeyframesAnimation`: the same rule can be selected for different elements at different relative depths.

Carry scope at the existing non-document visitor rather than reconstructing it from the number of successful callbacks:

| Selected data | CascadeLevel construction |
|---|---|
| Target's containing shadow tree, using the collector's SVG-use normalization | `author_normal(for_same_tree())` |
| Immediate assigned slot's tree, then further assigned slots | Start `for_outermost_shadow_tree()` and `dec()` for each further slot |
| Target's own shadow root (`:host` path) | Start at -1 and decrement once for each assigned-slot hop, as `collect_host_and_slotted_rules` does |
| Successive containing `::part` trees | Start `for_innermost_containing_tree()` and advance with `inc()` for each containing edge |
| Document author fallback reached through containing part trees | Retain the document's positive containing distance; ordinary document selection uses same-tree order |
| User / UA fallback | Preserve `CascadeLevel::new(CascadeOrigin::User/UA)` rather than relabeling it author |

An internal scoped visitor can return the document-applicability result together with its author level, while the existing visitor drops the extra scope for old callers. It must preserve the current `doc_rules_apply`, slotted/part eligibility, SVG-use treatment, selection order and finite shadow-order saturation. In particular, skipped trees without matching rule data must not collapse the actual selected tree's distance. The current part collector increments inside its available-part-rules branch; this proposal does not certify that preexisting behavior or propose changing it incidentally. Test the new transport against `CascadeLevel::get_shadow_root_for_scoped`, including missing intermediate data, nested slots and exported parts.

Use the selected level at all three conversion sites: real unvisited-cascade dependency recording, Gecko keyframe extraction and Servo intermediate-keyframe generation. Save and restore an existing caller context's scope and `for_non_inherited_property`; fresh temporary contexts can receive the selected level before conversion and then be dropped. Where separate declaration guards are used, select them with the level's origin. Gecko currently reads through its global shared lock; do not invent a separate lock contract there.

## Other reviewed behavior and remaining boundaries

The dependency pass executes before owning-style build and tree-counting selector-flag publication, sets rule caching uncacheable, and restores the non-inherited-property flag. It records conversions for all declared steps, including overwritten ones: this is conservative work, not a proof of selected-winner or exact effect dependency behavior. Style sharing, overridden keyframes, animation-only updates and animated font/self-dependency remain explicit activation obligations. Recomputing in a temporary animation Context alone would not publish those effects to the owning style.

Gecko supplies base/parent styles, the element, container query and tree-counting cache. Servo threads parent style, including the new primary style for pseudo-elements. The inspected callsites no longer use the removed infallible easing wrapper; remaining same-name Searchfox results belong to unrelated filter/range helpers. A configured Gecko check will not compile all Servo-only paths.

Resolved Linear functions retain the old piecewise builder, canonical equality, serialization and Arc storage. `Percentage::to_percentage` delegates to `resolve`, matching the new known-value route. Contextual stops own all Number/Percentage expressions without a computed cache. Steps jump-none handling and Bezier x clamping are retained; API conversion fails before writing output. Known parsing adds temporary storage allocations, so no performance-neutral claim is made. API context policy and complete invalidation are not solved by this representation.

The compact checker was separately read at `092907`, with saved binding authentication `6b6759`: six buffered sources, accepted easing claim alias, thirteen other fixed accepted claims, owned-group absence before reverse restoration, unchanged canonical control bytes, and explicitly recorded root raw-index drift. No checker main, source overlay, compiler, browser, index operation or canonical publication was run by this reviewer.
