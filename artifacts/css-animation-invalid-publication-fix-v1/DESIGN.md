# Preserve guaranteed-invalid values during animation publication

Candidate, not accepted. The original16-case probe has ten failures and six passing controls on the unchanged fix81 build. A final WPT must avoid depending on the earlier explicit-inheritance repair for noninheriting registrations.

The current `CustomAnimatedValue` separates absent outer endpoints from a present value whose inner payload is guaranteed-invalid. `to_declaration` currently converts the latter to CSS-wide initial; recascade uses the registered initial value, which need not be guaranteed-invalid. This changes both computed custom values and var() fallbacks.

Introduce an internal `CustomDeclarationValue::GuaranteedInvalid` variant. It has no references and removes the property value from the appropriate substitution map after marking the declaration seen, preserving lower-priority suppression. Converting it back to an animated value retains outer presence and inner invalidity. Explicit initial/unset/inherit declaration behavior stays separate.

Use the existing css(skip) derive handling: empty serialization and unsupported typed reification. Neither an empty Unparsed token list nor a removed declaration represents this invalid computed value correctly. The variant is internal and not parsed from author syntax.

Normative basis independently checked by root: Properties/Values §2.3 CSS-wide defaulting, §2.4 universal syntax computed value including guaranteed-invalid, §2.5 computed-value animation; Cascade explicit inherit copies the parent computed value; Variables §2.2 empty serialization does not equate invalidity with an empty token list, and §3 selects the var() fallback for invalid values. Web Animations implicit keyframes use the underlying value. These sources establish the observer; source/compiler/map and complete scheduling correspondence still require separate evidence.

Sources:
- https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values
- https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior-of-custom-properties
- https://drafts.csswg.org/css-cascade-5/#inherit
- https://drafts.csswg.org/css-variables-1/#guaranteed-invalid-value
- https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect

Native patch is intended to touch only the custom declaration enum and its cascade/animation conversion consumers. Source snapshots preserve all unrelated local modifications so the eventual patch can exclude them. No native acceptance, independent landing, complete animation proof, release impact or novelty is claimed yet.
