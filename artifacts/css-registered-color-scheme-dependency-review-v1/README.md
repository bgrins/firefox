# Selected custom identifiers and ColorScheme dependency

The current specification supports a focused false-cycle lead: a registered union containing `<color>` does not make a selected `<custom-ident>` compute as a color. The source nevertheless adds a ColorScheme edge from the registration union. This package supplies one tentative WPT page with five callbacks. No browser was run, and no native defect or fix is accepted.

## Narrow normative trace — 30 October 2026

Scenario: register `--v` as `<custom-ident> | <color>` (or the reversed union), with initial `normal`, inherits false. Specify `light`, then `dark`; neither token is a color. Use `color-scheme: var(--v, attr(data-unused type(<custom-ident>), light))`. There are no animations, keyframes, inherited custom dependencies or active attr calls.

1. [Values property replacement, step 1](https://drafts.csswg.org/css-values-5/#property-replacement) invokes substitution with the color-scheme property context. Its later steps parse the returned tokens and retain the parsed result on success.
2. [Generic substitution, step 2.4](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) dispatches to the selected function's replacement algorithm. [Variables var replacement, step 2](https://drafts.csswg.org/css-variables-2/#replace-a-var-function) fetches the referenced computed custom value.
3. [Properties and Values §2.4](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) applies the computed-value rules of the first matching union clause. Its custom-ident rule says “the computed value is as specified.” Here the chosen identifier does not require color resolution. [§2.7](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) substitutes the serialized computed value.
4. Var replacement step 4 evaluates the fallback only for an invalid primary. The valid identifier therefore leaves the attr fallback unused. No nested replacement asks for color-scheme again.
5. [Color Adjustment's property table and light/dark definitions](https://drafts.csswg.org/css-color-adjust-1/#color-scheme-prop) define the computed value as normal or a color scheme support. For light/dark, that support includes the specified keywords in their specified order. The one-keyword cases therefore retain light or dark in the computed support; the probe checks its CSSOM serialization, not the user's preferred or actually used UI scheme.

**Verdict: REACHED** for the narrow expected computed values: both --v and color-scheme remain light, then dark. A registration-union edge that invalidates this acyclic selected identifier would contradict that result. This is not a general specification of all color dependency cycles. The [explicit additional dependency rules](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) concern present relative units; they do not override the first-matching-clause computation in this scenario. The conclusion follows the positive identifier computation route, not a claim that a global absence search disproved every color dependency rule.

The bounded index trace found zero routes at depth nine because the generic function dispatch is not expanded to the var-specific algorithm. The explicit deciding steps and current primary bodies above supply the manual bridge; zero routes are not a NOT REACHED result. Seven shipped anchors resolve. The Properties index body is older (959d45…) than the freshly captured primary (2e733…); the first-clause and identifier rules were checked in the latter. Values/Variables indexed hashes match current captures. Initial unsupported URL/readonly-cache/DNS attempts and an imprecise source identifier search are preserved alongside successful queries.

## Concrete source route

`find_non_custom_references` unconditionally adds COLOR_SCHEME whenever registration.syntax.dependent_types includes COLOR, whereas length edges additionally inspect the value. Both this helper and `might_have_non_custom_or_attr_dependency` were read from current indexed Searchfox; exact frozen bodies are retained in SOURCE-EXCERPTS.json. This is an implementation lead, not a claim about installed-browser behavior.

The admission detail matters. The frozen helper admits plain var() on FontSize/LineHeight, or ATTR on other longhands. Therefore plain `color-scheme:var(--v)` need not reach the old graph's ColorScheme backedge. An unused attr fallback sets the source inventory's ATTR bit; `maybe_note_non_custom_dependency` then records ColorScheme. The selected var still points to --v, whose union-induced ColorScheme edge can close the false cycle. This is a source-shaped prediction. The new contextual prototype traverses all priorities and can expose the plain form too; that does not establish an old browser failure.

## Five controls and observations

- Union, plain var: separates the old admission route from the union edge.
- Union, unused attr fallback: suspected existing-source trigger.
- Reversed union, unused attr fallback: light/dark select custom-ident even when color is tried first.
- Ident-only, unused attr fallback: removes COLOR from registration while keeping the same sink expression.
- Union, literal color-scheme: removes the sink's custom-property dependency.

Each callback uses an isolated iframe/registry and calibrates invalid registered syntax to initial normal before inserting the target. It captures the first computed color-scheme and then the custom value for both light and dark before assertions. These sequential getter snapshots are not simultaneous internal state. All full records are retained in the hidden output and failure diagnostics; no private PASS transport is added. Setup/acquisition failure can precede full diagnostics. No animation or timer is needed for these ordinary synchronous style updates.

The five cases expect the same selected identifiers; they are not a probe of light-dark(), system colors, used color preference, animation taint, or registered-invalid policy. The suite is separate from frozen125 and adds no current-state binding or execution owner.

Validation: saved b4ad46/0 generated the genuine manifest, inertly registered five callback names, and passed WPT path/content lint. Shared harness bytes match the frozen harness. No full lint repository scan, Git, browser or native operation was performed.
