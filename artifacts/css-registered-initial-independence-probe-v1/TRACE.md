# Initial-value registration probe

Question: must JavaScript registration reject typed initial values whose computation depends on CSS-controlled element context?

Scenario: each call uses a fresh custom-property name, a supported syntax, an explicit initial value, and `inherits: false`. Ordinary-property parsing is calibrated first. Invalid registration must leave the name available for a subsequent valid registration. This does not test the separate `@property` rule.

1. [Properties and Values API, register a custom property, step 4](https://drafts.css-houdini.org/css-properties-values-api-1/#dom-css-registerproperty) parses the initial value and requires computational independence before inserting the registration. Its deciding action is “throw a SyntaxError” when that condition fails. Independence permits global information that CSS cannot change, but excludes dependence on other element properties.
2. [Color 5, light-dark](https://drafts.csswg.org/css-color-5/#light-dark) computes the color form by selecting a branch using the element's color scheme. Distinct red/blue branches therefore depend on CSS-controlled context. The identical-image-branch control is deliberately retained; rejecting every occurrence of the function is not justified by this witness.
3. [Color 4, resolving other colors](https://drafts.csswg.org/css-color-4/#resolving-other-colors) resolves system colors during computation; the scheme-sensitive Canvas value is distinct from currentcolor, which computes to itself. The latter is a positive control, not a proposed invalid initial.
4. [Conditional Rules 5, container lengths](https://drafts.csswg.org/css-conditional-5/#container-lengths) evaluates container units against eligible ancestors on each axis. Those dimensions are CSS-controlled; absence of a container in a particular page does not make the syntax generally independent. Nonzero container units in calc and transforms retain that dependence. Font-relative units supply existing invalid controls; absolute lengths, physical viewport width, absolute colors and gradients supply valid controls.

Verdict: REACHED for the JavaScript registration rejection requirement in these dependent cases. The nested gradient and transform cases use the same computation requirement compositionally. This is an oracle trace, not evidence of browser failure or a native fix.

The current `@property` initial-value descriptor prose differs from the JavaScript algorithm; no assertion about its rejection behavior is included. CSSWG issues [12735](https://github.com/w3c/csswg-drafts/issues/12735) and [13628](https://github.com/w3c/csswg-drafts/issues/13628) discuss these restrictions. This probe follows the current published JS algorithm, without treating an open proposal as an implemented spec change.

Primary drafts were read on 2026-10-27. `webspec-index` was unavailable (command exit 127), so the trace uses the primary specification pages directly. Searchfox's existing register-property-syntax-parsing.html includes the identical-image light-dark control. No native or canonical Lean proof is claimed. Browser execution and independent oracle review remain pending.
