# Experimental registered active-value producer

This is a minimal successor to frozen corrected proposal V2. The only V2-to-V3 source change removes the unregistered-singleton predicate in Cascade::cascade_custom_property. Winning Animations-origin values now acquire source provenance regardless of registration. Three other native postimages are byte-identical, including the held-provider and clean-provider candidates. Existing priority/seen/revert handling, ordinary-property guard, alias context, attr-security metadata, and metadata-aware map equality are unchanged. No current native owner or source was edited.

The observed valid registered inputs justify this bounded experiment; they do not establish all registered taint semantics. Installed Firefox158 runtime2 returned vertical-rl on all eight readings in each unregistered/universal/typed mode; Chrome156 returned vertical-lr on all eight. Both retained registration calibration, literal control and fixed lifecycle, with harness0. REGISTERED-OBSERVATIONS.json is a saved-schema replay (60b2b6/0), not a native candidate result. The earlier incomplete V1 remains separate. The current 106-case native trial is untouched and is not presented as validation of V3.

## Why the valid paths support the producer change

| Registered path | Existing V2 mechanism retained by V3 |
| --- | --- |
| Universal `*`, reference-free value | The producer marks VariableValue before the early substitute/apply return; ComputedRegisteredValue::universal copies that flag. |
| Typed unparsed value with successful computation | substitute_internal retains explicit provenance; Substitution::into_value ORs it after successful compute_value. |
| Already Parsed typed value | to_computed_value preserves metadata; the producer marks the selected map value after insertion. |
| Computed animation declaration round-trip | to_declared_value preserves universal wrapper taint, or uses from_computed_value for Parsed values. Re-cascading the winning Animations-origin value marks it independently. |
| Typed serialization for outer var | to_variable_value transfers the wrapper bit to the resulting token value, so the unchanged outer Var guard can reject it. |
| Successful interpolation | Value::animate ORs endpoint metadata; discrete/custom-ident failure fallback and actual integration still require native tests. |
| Same-token changes and map reuse | Existing value_may_affect_style checks effective animation metadata for universal values; Parsed values recompute, and map dedup/equality compares metadata explicitly. |
| Direct valid CSS-wide selected replacement | Producer marks only surviving selected map values after priority/revert selection; the substituted CSS-wide branch also preserves its successful substitution bit. |

REGISTERED-PATHS.json binds exact frozen bodies for this audit. Public Searchfox discovery of Parsed-value construction is saved (ba8596/0); initial restricted-network DNS failure is retained. This is source reasoning, not proof every runtime entry takes one of these paths. The producer still includes script-generated Animations-origin effects; the proposed next suite uses CSS keyframes and does not certify WAAPI behavior.

## Unresolved registered obligations

One additional successful-computation entry is not metadata-transparent: `CustomAnimatedValue::from_declaration` sends the CSS string of an Unparsed typed value to `SpecifiedValue::compute` without reattaching that input's explicit animation bit in the inspected body. A later winning Animations recascade can re-mark the value for the observed valid fixture, but that is an explicit producer-boundary argument, not proof that every successful registered conversion preserves provenance. Exercise this entry independently, especially values transported without that later origin boundary.

The error paths deserve separate policy and tests, not an implicit preservation claim. In substitute_references_if_needed_and_apply, substitution failure or typed parse failure calls handle_invalid_at_computed_value_time and returns without OR-ing the rejected substitution's animation bit onto the selected initial/inherited replacement. In the held recursive custom path, registered_default can replace a tainted invalid or CSS-wide result with a selected default and reconstruct from that value's own metadata. The clean provider has a different defaulting implementation. This proposal changes neither branch.

A winning valid animation result and an invalid referenced declaration default are not the same input. The current value-level experiment does not resolve whether rejected-input/name-level taint must attach to such defaults. Do not certify all registered aliases/defaults from the constant valid keywords. Existing inherit/initial/unset fast paths use seeded maps; cross-element taint inheritance and later ordinary replacement need explicit controls. Attribute-derived alias provenance and direct typed-attr consumer context remain separate known gaps; removing this registration gate does not repair them.

Proposed discriminators before broader claims:

- Include all four exact hidden-diagnostic registered-scope V2 WPT callbacks in the next suite, alongside the unchanged106. Require effective registration calibration and inspect both first/later readings.
- For registered universal and typed names, exercise animation introduction/cancellation and same-token ordinary replacement, with retained animation/source observations. Distinguish active-value scope from unresolved name-global policy rather than inventing a before-animation oracle.
- Use a typed registered alias referencing a tainted `one two` value, with noninitial initial/inherited replacements and distinct outer var fallback. Compare ready versus deferred substitution and inherits true/false. Treat the taint-on-default expectation as a separate spec question; do not silently choose it here.
- Exercise successful CSS-wide inheritance/initial replacement separately from invalid typed keyframes that may be filtered before producing an animation value. Retain source/effect membership so a discarded keyframe is not mistaken for a successfully marked producer.
- Preserve ordinary important winners, valid registered aliases, typed animation interpolation and attr-security behavior. Existing94 preservation callbacks help regressions but do not cover all these taint-triggered paths.

## Applicability and checks

SOURCE-ROLES retains the same four original preimages. Native.patch applies over held provider2675; native-clean-provider.patch uses committed provider8a4 with identical other three files. Provider postimages are exactly V2; source applicability does not establish clean-provider execution or independent landability. Actual static906900/0 reconstructs the one replacement and applies/reverses both full patches in owned scratch; scratch removed. No build, browser, canonical coverage, native acceptance, registered-policy completeness or native refinement is claimed.

The package is a proposal only, with no execution gate or runner. Root must bind a new controlled owner after restoration and independent review. Do not mutate the existing106 owner or reinterpret its result as a run of these bytes.
