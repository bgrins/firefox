# Registered length Zoom trace

The pre-A branch binary exhibits inconsistent registered-length storage/serialization under CSS zoom. This is a separate existing lead, not an A-introduced bug, an upstream/release-browser reproduction, or an accepted new fix. Original observation RESULT.json is complete/preserved and all16registrations succeeded. Full32snapshots and exact native roles are pinned in OBSERVED.json; candidate comparison was still pending when this report was sealed.

| Fixed-font case at zoom2 | Registered CSSOM | Width CSSOM | Physical width |
| --- | --- | --- | --- |
| Literal5px | 2.5px | 5px | 10 |
| Ready5px primary, unused1em fallback | 5px | 10px | 20 |
| Selected invalid em text, initial10px | 10px | 20px | 40 |
| Initial keyword, initial10px | 5px | 10px | 20 |
| Explicit inherit of parent20px | 10px | 20px | 40 |

These are measured values, not proposed expected values. The fixed-font cases avoid the disputed self-font numeric cycle question. Both snapshots and self-font cases remain in the raw evidence.

## Manual specification trace

Scenario: a registered non-inherited length property with valid initial10px, selected literal5px, fixed font20px, local zoom2, no ancestor zoom or transform, no border/padding; width consumes that custom property. Browser full-page zoom is not changed.

1. [Properties and Values API computed-value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) admits the length and converts a dimension to its canonical unit. Literal5px therefore remains5px.
2. [Registered var substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) uses serialized computed values, not an implementation's internally zoomed storage. The deciding text is: “substitute as their computed value”. The width token value should consequently be5px.
3. [Viewport zoom](https://drafts.csswg.org/css-viewport/#zoom-property) scales the used length. [DOM/CSSOM interaction](https://drafts.csswg.org/css-viewport/#zoom-om) says computed-style lengths “must be unscaled” and bounding APIs “must return rects with scaled lengths”. Thus custom CSSOM5px, width CSSOM5px and physical width10 are the joined expectation for this scenario.

**Verdict: REACHED** for the literal fixed-font expectation. The baseline literal's2.5px custom CSSOM contradicts it; the ready-primary path has the correct custom text but doubles the consumed width. This manual clause trace uses current captured official documents and validated element IDs. webspec-index was unavailable per root, so no machine-generated exhaustive route enumeration or NOT-REACHED assertion is claimed. Invalid/defaulting and inheritance followups need their additional defaulting rules traced before a comprehensive WPT oracle is finalized.

## Native correspondence

The exact captured cascade initializes/cascades simple registered values before the custom graph and remaining prioritary properties finish. StyleBuilder starts with inherited effective_zoom. The captured dependency table makes FontSize depend on Zoom. Consequently an em graph edge can force Zoom earlier even when its selected replacement becomes an absolute length. Direct reference-free values can compute using the earlier scale.

NoCalcLength::to_computed_value_for_math multiplies absolute pixels by builder.effective_zoom. The actual stored length therefore depends on which scale was active at computation. Value::to_variable_value uses to_css_string directly, so stored scaled lengths become var tokens without a scale correction. By contrast, captured Servo_GetCustomPropertyValue clones the value and invokes to_resolved_value; CSSPixelLength::to_resolved_value divides by the final style.effective_zoom. A consumer then applies its own computation scale to var tokens. These three boundaries explain why one path exposes a halved custom value while another exposes doubled consumed geometry.

The current source captures for properties/data.py, properties/properties.mako.rs and computed/length.rs are compared against Searchfox in SOURCE-COMPARISON.json and difference patches. Differences concern rule-context bookkeeping and FitTolerance imports/types; the traced Zoom initialization, dependency and resolution code matches. Relevant older captured glue/value bodies are separately pinned. No live source or build was changed by this audit.

The accepted root-rlh-zoom repair43afd2c6f3500cee4a2dd07d07eb14aca723fae3 changes only the Rlh root reference-size path to avoid a second multiplication. This lead uses absolute px and registered value boundaries, with no rlh expression. It is distinct from that accepted repair, but should not receive a new count until a standalone fix and normative WPT are validated.

Merely ensuring Zoom before every registered computation cannot fix all outputs: it would move the literal case toward the current ready-primary case, correcting CSSOM while doubling substitution consumption. A coherent representation must define the scale of stored registered computed values, CSSOM export, var-token export, initial values, inherited/CSS-wide copies and re-cascade/animation values together. The likely contract is canonical unscaled registration storage with each consumer applying its own zoom once; adoption requires a structural normalization audit rather than blindly invoking all of ToResolvedValue (which can also resolve colors and other non-length state).
