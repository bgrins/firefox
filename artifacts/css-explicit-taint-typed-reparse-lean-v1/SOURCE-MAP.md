# Saved source correspondence

`SOURCE-EXCERPTS.json` contains exact text from the immutable root-created e86 source snapshot. `REFERENCES.json` pins those source files, snapshot identity, the transition probe's report and the three prior model packages. Native correspondence is a review relation, not a verified extraction of Rust into Lean.

| Lean boundary | Saved native source | Required external premise |
| --- | --- | --- |
| `Universal`, `uncompute` | `ComputedValue::to_declared_value` in properties_and_values/value.rs | Universal computed representation reaches uncompute; the represented reference-free inner value has no ATTR flag, so its existing taint is the explicit bit. Wrapper-dirty/inner-clean is the concrete witness. |
| `ReferenceFree` | Unparsed `VariableValue`, then `substitute_internal` | The same explicitly tainted object is recascaded under a typed current registration; it is not replaced by a freshly parsed authored string or recomputed endpoint. No references remain. |
| `legacyNoReferences` | `do_substitute_chunk`'s empty/no-reference return | Exact CSS bytes/token boundaries are transported, but the supplied substitution taint is default; `substitute_internal` does not forward the explicit field. Tokens, URL context and grammar are abstracted here. |
| `parseNative` | `Substitution::into_value`: construct full-value AttrTaint, call `compute_value`, then OR `v.attr_tainted` | Bool denotes the native full-value taint input, not a proof of range layout. Parser input/output provenance can affect success independently; no general parse equivalence is assumed. |
| `native_admitted_handoff_counterexample` | The same `into_value` path under typed registration | Both parser calls succeed with the same clean payload. This is an explicit conditional premise, intended for the prospective string case, not arbitrary URL/image syntax. |
| Payload-only subset and trace composition | Correctly completed `publish` output in the imported aggregate model | A taint-insensitive, provenance-neutral parser; it is a proved special case of the general parser interface. |
| `withInitial` | Invalid-at-computed-value handling after a failed typed computation | Caller has already selected the proper computed initial/default. Registration/inheritance choice and initial computation are external. |

The transition probe report supplies a concrete candidate caller chain: old computed-map endpoint → AnimationValue uncompute → transition keyframe construction → current-style keyframe map rebuild → typed reparse. That report also identifies remaining transition creation, endpoint retention, cancellation, and sampling prerequisites. This model assumes the handoff rather than proving browser reachability. It does not reinstate the excluded direct keyframe parser route: actual keyframe processing can bypass that route by reading a rebuilt computed custom-property map, whose construction is the path being examined.
