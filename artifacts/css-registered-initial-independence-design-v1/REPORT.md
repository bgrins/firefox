# Initial-value computational independence: implementation decision

Recommend a separate JS registration fix that validates the selected typed value before registration/cache insertion. Do not add rejection inside Color parsing, reject all color/image types, or infer dependence from used-value behavior. This is a source/spec design, not an implemented or accepted fix.

## Observed scope

The preserved 775-assertion local baseline contains 21 JS registration assertions: 12 pass and nine fail because SyntaxError was not thrown. The failures are cqw/cqi lengths, calc containing cqw, unequal color light-dark, Canvas, a Canvas color mix, two gradients containing dependent colors, and translateX(cqw). Existing passing controls include currentcolor, physical vw, absolute mixtures/gradients/transforms, and image light-dark(none, none). These are branch-browser observations; they are not installed-release observations. No new browser execution occurred in this audit.

## Algorithm boundary

The JS algorithm parses first, then checks the resulting value for computational independence. Alternatives are tried in declared order. Thus `<color> | <custom-ident>` with Canvas must not become an identifier merely because the selected color is dependent; reversing the alternatives selects an identifier and changes the answer. The definition concerns obtaining a computed value, not paint or layout. The same specification currently has inconsistent-looking @property wording; retain the separately captured policy caveat instead of silently changing that path. [Properties and Values API](https://drafts.css-houdini.org/css-properties-values-api/#the-registerproperty-function), [alternatives](https://drafts.css-houdini.org/css-properties-values-api/#combinator).

## Actual upstream route and omissions

`Stylist::register_custom_property` calls `PropertyRegistration::validate_initial_value`, then inserts the registration and rebuilds initial values. The validation helper also serves CSS-rule registration. `SpecifiedValue::parse` selects a complete component/list, but `Parser::parse` currently passes DISALLOW_COMPUTATIONALLY_DEPENDENT into each alternative's parser. `LengthUnit::from_str_with_flags` applies it to font-relative units, while all six container units lack that guard. Specified Color parsing does not apply it to System or LightDark. Nested gradient colors and transform lengths use those ordinary parsers, explaining the observed breadth without assuming nine independent native defects.

The post-selection insertion point is after `ValueInner::Component`/`List` is formed, before returning or computing it. A JS-specific validation entry point can initially use ordinary grammar parsing and then this check, leaving the ambiguous shared @property policy unchanged. Merely adding a second check after the existing restricted parse does not fully fix alternative selection: the earlier restricted parse may already have chosen a different branch. Keep reference/CSS-wide/universal validation and duplicate-registration ordering intact.

## Computed representation, including image caveat

`Color::to_computed_color(None)` already preserves CurrentColor symbolically and recursively handles mixes and relative colors; System and LightDark require Context. It is a useful primitive, not an exact independence predicate: two independently computable light/dark branches may compute identically even though this helper requests Context. Compare independent computed branch representations where needed; equality of two dependent source branches alone proves nothing. Do not resolve currentcolor against an element just to validate registration. [Color 4 resolution](https://drafts.csswg.org/css-color-4/#resolving-color-values).

Fresh upstream `computed::image` capture shows `ToComputedValue for specified::Image` DOES call `ld.compute(context)` for LightDark and converts selected None to transparent Image. The reverse conversion labels retained LightDark unreachable. GenericImage having a LightDark variant does not establish that it survives computation. This is upstream evidence only; no exact equality to the active branch's untouched image source was asserted.

Color 5 explicitly describes computed branch choice for the color form, while the image form is described as returning an image. That textual difference and the implementation deserve separate treatment. Do not promote unequal direct image branches to a required rejection based on the nine failures: those image failures are gradients with dependent color stops. Preserve the equal-none positive. Add direct unequal image branches as an observation/clarification control until the image computed-stage oracle is settled. Nested colors still require validation at the stage where gradient components compute. [Color 5 light-dark](https://drafts.csswg.org/css-color-5/#light-dark).

Container units depend on CSS-selected ancestor size; absence of an eligible container in one registration environment does not prove independence for all CSS contexts. Check each admitted numeric expression and nested length-bearing component, including all list members. Preserve percentages that remain symbolic and physical viewport controls. Logical viewport units need their own element-writing-mode audit; do not assume a passing physical-vw control covers them. [Conditional 5 container units](https://drafts.csswg.org/css-conditional-5/#container-lengths).

## Concrete implementation route

1. Add a selected-value independence operation on SpecifiedValue/SpecifiedValueComponent, with recursive handling of lists and the actual numeric, color, gradient/image and transform representations. This is structural recursion over admitted values, not a whitelist of registration syntax strings. A literal named `Canvas` admitted as an identifier must never enter color logic.
2. Ensure the selected representation retains dependencies through parser simplification; a post-parse scalar is not sufficient evidence if a contextual expression was folded earlier. If necessary, carry per-alternative dependency information alongside the successful parse and commit it only when that alternative wins. Do not leak information from failed alternatives. Share length dependency classification with existing parsing restrictions, including all six container units. Inspect calc children and nested lengths; do not scan source text for unit substrings or use current container availability. Avoid changing general declaration parsing.
3. For colors, preserve symbolic currentcolor and context-free relative/mix forms; reject actual scheme-dependent computation. Handle equal independent branch results without rejecting the existing equal-none image control. Walk nested color-bearing image forms instead of rejecting Image as a category. Unknown cases require an explicit implementation/spec decision, not a blanket failure or silent certification.
4. Invoke this operation once after normal typed grammar selection in the JS initial-value path, before cache insertion. Keep @property behavior separately documented until its policy is resolved. A later shared-policy change should be separately reviewable.
5. Build and compare the unchanged API21 plus the decisive controls below. Preserve the full existing provider/zoom regressions; this proposal does not repair pending-provider cycles or initial-cache publication.

## Minimal additional controls

- Canvas with `<color> | <custom-ident>` rejects; reverse order admits an identifier. Also explicit `Canvas | <color>` admits the literal. Verify a rejected registration does not reserve its name by immediately registering an independent replacement.
- Container-unit length lists with only a later member dependent; all six cq units; calc and transform-list nesting. Pair with independent px/percentage forms and ordinary declarations to ensure the check stays at registration.
- Nested currentcolor mix/gradient positive controls; absolute nested colors; equal independent color branches as a separate positive. Retain light-dark(none, none).
- Direct unequal image light-dark is observational pending the precise computed-stage oracle; do not label a failure a tenth bug.

## Limits and provenance

No native patch, build, lint, browser run, live source/epoch/index query, or Lean claim is part of this package. Source captures are current Searchfox upstream reads, not proof of branch identity. The source-to-observation explanation is an inference to test, not native formal verification. The API21 and policy research artifacts are pinned in REFERENCES.json. Existing @property color failures remain conditional observations, and provider candidate acceptance must inspect their full snapshots rather than unchanged FAIL statuses.
