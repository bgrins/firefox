# Provider default test oracles

Checked current editor drafts on 27 October 2026; this is a manual call-chain trace. webspec-index was unavailable (26e909/127), so official pages were fetched directly and cited element IDs checked in their HTML. SPEC-SOURCES.json pins the captures; ANCHORS.json records successful anchors. No exhaustive graph-tool trace or native correspondence is claimed.

## Missing and rejected values

Scenario: a nonuniversal registered property has an initial vertical-rl, or inherits a parent's vertical-lr. It supplies writing-mode through var(). No selected contextual unit occurs in that provider. A separate registered length requests a fixed line-height.

1. [Registered computed values](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) are grammar-checked; rejection causes computed-time invalidity.
2. [Property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) makes unresolved substitution or failed final grammar invalid. [Invalid substitution](https://drafts.csswg.org/css-values-5/#invalid-substitution) defaults a nonuniversal registered property according to inheritance.
3. [Registered substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) specifies that “registered custom properties substitute as their computed value”. The outside consumer therefore receives the provider's default, not its unresolved text. A consumer fallback is unnecessary when that default is valid.

Typed missing/invalid attributes without fallback reach the failure branch of [attr substitution](https://drafts.csswg.org/css-values-5/#attr-substitution). An unknown env name without fallback makes its containing declaration invalid under [env replacement step 3](https://drafts.csswg.org/css-env-1/#substitute-an-env). Trailing junk after a CSS-wide keyword is not a single keyword and must still satisfy the registration grammar.

Verdict: **REACHED** for the initial/inherited default and the corresponding writing-mode keyword. Root inherited cases have no parent value and use the initial. These tests do not claim a cycle through writing-mode or variable line-height.

## Actual and unused cycles

Scenario: --mode and --other have distinct noninherited keyword initials. Their selected var references form a self or mutual cycle; fallback variants provide horizontal-tb inside that cycle. A separate writing-mode consumes --mode.

1. [Guarded contexts](https://drafts.csswg.org/css-values-5/#substitution-context) mark all participants on reentry: “all participants in the cycle become invalid”.
2. [Substitution step 3](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) checks the mark again after nested replacement. An inner fallback cannot erase it.
3. Defaulting then gives each registered participant its own initial. The outside consumer reads the finalized --mode default. Conversely, a successful primary does not evaluate its unused self-referencing fallback.

Verdict: **REACHED**. This concerns real selected custom-property cycles, not the unresolved unit-to-writing-mode cycle policy. The separate cycle model is conditional on correct participant classification and adds no native proof.

## Initial color calibration

[Color 5 light-dark](https://drafts.csswg.org/css-color-5/#light-dark) selects its first or second computed color according to the element's color scheme. The four tests use @property, a direct literal control and a no-declaration registered-initial control, and light/dark/light mutation. [The current initial-value descriptor](https://drafts.css-houdini.org/css-properties-values-api-1/#initial-value-descriptor) requires matching syntax. In contrast, [JS registration](https://drafts.css-houdini.org/css-properties-values-api-1/#register-a-custom-property) still requires computational independence; these tests do not assume that CSS.registerProperty accepts a color-scheme-dependent initial.

Verdict: **REACHED** for the stated current-ED @property/color behavior. A registration/calibration failure must be reported separately from the pending-provider repair. The early writing-mode consumer intentionally rejects a color. Passing later CSSOM checks does not prove that every earlier initial computation had a ready context or no hidden effects. Color remains a calibration/coverage boundary for the bounded identifier/string proposal.
