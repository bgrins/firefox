# Exact source-to-model boundaries

Complete native files and hashes appear in SOURCE-CAPTURE.json. These are reviewed local snapshots, not translations certified by the Rust compiler. Searchfox discovery output and indexed snapshots are retained separately. Local/index differences include the accepted source-provenance shorthand cache change, custom-property work, scope-dependent nth sharing work, and rule-type parsing work. No equivalence to a newer indexed implementation is implied.

| Native symbol | Model operation | Source facts and boundary |
|---|---|---|
| dom.rs AttributeTracker::new/query/finalize | empty references / recordQuery / publication | query pushes namespace then calls context.get_attr; finalization returns the tracker map; allocation and duplicate vector sizes are not modeled |
| sharing/checks.rs have_same_referenced_attrs | haveSameReferencedAttributes | Optional absence is empty support; nested all is universal equality over recorded pairs; outer primary/pseudo traversal requires the relation for each style |
| properties/cascade.rs apply_declarations | one history from a fresh cache/tracker | Both are created within this function; custom/prioritary/late stages receive them; finalize publishes after late stage |
| properties/properties.mako.rs StyleBuilder/build and properties/gecko.mako.rs ComputedValues::new | transfer of reference metadata | The recorded map is passed into built style metadata, without a deduplication step in the retained publication chain |
| properties/cascade.rs substitute_variables_if_needed | recordRuleObservers flags | WithVariables on a non-inherited id marks uncacheable; Display/Content additionally sets DISPLAY_OR_CONTENT_DEPEND_ON_INHERITED_STYLE; ordinary declarations bypass this method's work |
| rule_cache.rs RuleCacheConditions::set_uncacheable | Boolean OR true | Idempotent setter; cache lookup consequences are not a performance neutrality claim |
| properties/mod.rs VariableDeclaration::substitute_variables | queryOnly / fill / hit | Invalid-property early return, source Arc cache hit, substitution and CSS-wide keyword early return, then successful shorthand parse and insertion are distinct branches; no single pure action premise is substituted for these branches |
| properties/mod.rs ShorthandsWithPropertyReferencesCache | eraseCache | Native key is (ShorthandId,LonghandId); value retains Arc source and declaration. Ghost dependencies are not stored natively. Tokens model these identities injectively as an admission obligation |
| properties/mod.rs shorthand insert loop | installParsedDeclarations | Each logical entry can install its physical alias before its own id; all share one preceding query history; overwrites preserve the ghost-certificate invariant |
| custom_properties.rs substitute/do_substitute_chunk/substitute_internal | unresolved evaluator yielding query history | Returns CSS/taint or failure; recursively consults custom/env/attr providers. Exact output, query support and transitive provider effects remain open |

A cache hit's observer safety says only that replaying that entry's previously recorded queries would not change the sharing predicate. It does not say re-evaluating the shorthand now returns the same value, nor that every future provider remains stable. ObserverContinuation deliberately states a common continuation; proving that the native evaluator chooses it is a separate obligation.

The optional tracker map and nested vectors retain order and multiplicity. Our abstraction preserves their relevant sharing consumer, not all possible future memory, logging, timing, serialization, allocation or equality observations. Native AttributeReferences is not changed into a set by this research.

The namespace-collision boundary is pinned separately in attr-namespace-probe-v1/SOURCE-TRACE.md. Its own integrity manifest and unexecuted status are preserved without modification by this enclosing package.
