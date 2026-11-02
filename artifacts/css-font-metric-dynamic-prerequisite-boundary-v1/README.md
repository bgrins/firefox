# Dynamic prerequisite boundary after the native diagnostic

The actual diagnostic identifies registered `len` in Publish, with no metric action. Appearance was ensured and dynamic but uncertified; FontFamily, XTextScale and FontSize consequently remained uncertified. This confirms the blanket dynamic-chain certification guard blocks progress. It does not establish that those already-applied properties have correct final values. Removing the guard or certifying all ensured properties is unsafe.

## Why existing application cannot simply be blessed

The first fixture uses `--len:1em`, literal `font-size`, and `appearance:attr(data-length type(<length>), auto)` with attribute text `var(--len)`. `maybe_note_non_custom_dependency` calls `update_attributes_map` before its property-specific routing. `get_attr_value_for_cycle_resolution` parses the attribute into a universal token value; it does not finish its references. Custom roots run before the final attribute-root loop.

The ordinary generated dependency path can therefore reach Appearance while this cache still holds unresolved tokens. `substitute_variables_if_needed` immediately calls the declaration's substitution routine. The typed-attr branch reads the cached CSS and invokes `parse_typed_value`; it does not first run the retained selected-reference walk or demand a final node-publication certificate. Failed typed parsing takes the attr fallback. Consequently premature fallback/application is a concrete source possibility, not something an ensured bit excludes. The native diagnostic did not log cache contents, substituted CSS, or resulting Appearance, so this report does not claim it observed `auto` or prove the exact branch taken there.

Literal typed-attr inputs and missing attributes are different: their selected primary/fallback can be independent of `len`. The separate saved witness even starts with a prepared literal cache and still reproduces the blanket certification block. These cases justify supporting proven-final dynamic declarations; they do not justify treating every WithVariables declaration as final.

## Actual reads and ordering effects

| Operation | Source-established requirements/effects |
| --- | --- |
| Absolute FontSize | Converts the selected length with effective zoom and applicable `maybe_zoom_text`, which reads final XTextScale; keyword info starts at none. |
| Other FontSize forms | Percent/em/smaller/larger can preserve inherited keyword derivation; keywords/system/math/calc have distinct input paths. A px case cannot authorize all forms. |
| XTextScale application | `unzoom_fonts_if_needed` compares parent/current scale and can modify inherited font values. It is a real effect, not merely a scheduling flag. |
| FontFamily application | Prioritizes user fonts and can recompute keyword-derived size; recomputation exits for keyword-info None. Later family work must not overwrite an already-consumed value incorrectly. |
| Appearance application | Can add APPEARANCE_BASE eligibility/context flags. A stale application may change later declaration selection; finality cannot be inferred from completion of an unrelated literal size. |

Exact local excerpts are authoritative. Searchfox discovery confirmed the unchanged [application bookkeeping](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/properties/cascade.rs) and [font-size conversion](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/values/specified/font.rs). Local conversion interfaces differ from indexed source; no indexed implementation is transplanted.

## Before and proposed boundary

Current path: custom len → semantic FontSize → ordinary XTextScale → FontFamily → Appearance → eager attr substitution/application → dynamic certification rejected → len Publish Pending with no action. The source establishes the call path; the native diagnostic establishes its ensured/completion states, not the intermediate substituted values.

Proposed boundary: reached dynamic prerequisite → owned selection and final-reference checks → Pending without application, or retained substituted declaration → final input checks → one application and certificate. This changes when completion is earned, rather than accepting an earlier uncertified effect.

## Next specific change and test

Add an owned selected-prerequisite preparation path for supported dynamic Appearance/FontFamily declarations **before** ordinary ensured insertion or application. Retain eligibility/local rollback, exact longhand/raw Arc, reference cursor and context flags. Resolve the selected primary and only a genuinely selected fallback through the existing retained walk; require final custom/attr publication state, not cache membership. Substitute once, retain the resulting declaration, apply once and certify only after its actual prerequisites and bookkeeping are final. Do not retrospectively certify the builder produced by the old eager path, re-evaluate a losing declaration, or reuse an already-seen shortcut as proof. The ownership successor supplies containment but not this producer or progress.

The smallest useful test has two branches with the real ordinary caller and generated dependencies: (1) final literal typed-attr/missing-attr primary or fallback resumes a retained declaration, applies once and certifies the chain; (2) cached raw `var(--len)` remains Pending before Appearance is marked ensured/applied, without choosing auto, changing eligibility flags, or evaluating the declaration twice. Include rollback to a second dynamic declaration and verify its new Arc/cursor owns the reply. This is a proposed test, not an executed result in this package.

That change alone need not finish the first fixture. Its scheduling wait returns from Appearance to `len`, which needs computed FontSize. Completing that acyclic CSS value path also requires separating actual selected size/text-scale inputs from conservative family/appearance ordering, preserving zoom, inherited keyword bookkeeping and later fixups. Do not turn this scheduling return into a CSS SCC or waive XTextScale. A general value-sensitive computed-size boundary is the next progress obligation after safe dynamic preparation; it is not solved by a test-specific literal constant escape.

The earlier producer test support replaced Context ordinary application with unconditional completion and precompleted Appearance; that could not reveal this chain. The separate actual-method/generated-mask witness closes that control-flow gap, but still doubles CSS application and does not establish the browser's attr cache contents. A narrow later diagnostic could report cache presence, universal/reference-bearing state and selected-node finality before ordinary substitution, without dumping CSS or attribute values or performing another substitution.

No implementation, model, tests, browser run or native build was added here. This report authenticates source paths and separates the observed certification failure from unlogged earlier values. Existing true metric-cycle policy and broader nested scheduling remain unresolved.
