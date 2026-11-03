# Fallback and invocation scope

Retrieved 2026-11-02. Current draft queries and the depth-nine, untruncated property-to-guard trace are saved alongside this note; `spec-exists.log` validates the current anchors. The historical URL was readable through the web tool; the CLI failed to resolve that versioned path and its failure is preserved. This is a draft-based implementation analysis, not evidence about a browser.

Scenario: same element, no animation taint, `--a: var(--b, var(--a))`, with settled `--b: 1px`. Compare unregistered `--a`, and `--a` registered as `<length>` with a valid independent initial.

1. [Values 5 property replacement, step 1](https://drafts.csswg.org/css-values-5/#property-replacement) enters substitution with the property's name in its context.
2. [Substitution, steps 1 and 3](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) guards that context for the invocation and rejects a context marked cyclic, including a mark created by a nested call. [Guard matching](https://drafts.csswg.org/css-values-5/#guarded) lasts for that guard; it is not a permanent element-wide tombstone.
3. [Variables 2 replace-var, steps 2 and 4](https://drafts.csswg.org/css-variables-2/#replace-a-var-function) obtains the referenced computed value and substitutes the fallback only for a guaranteed-invalid result. Here `--b` is valid, so the nested self reference is not evaluated. With invalid `--b`, the fallback is evaluated, reenters `--a`, and marks the property invocation cyclic.
4. [Typed attr, steps 6 and 7](https://drafts.csswg.org/css-values-5/#attr-substitution) gives raw attribute-text substitution its own named context. A failed body can cause its caller to choose the outer attr fallback. That does not clear any still-active ancestor mark.

**Verdict: REACHED** — under the current guarded substitution algorithms, the valid-primary example avoids the self fallback. The invalid-primary control reaches it. An implementation must still preserve separate non-substitution computation dependencies.

Registration does not turn mere tokens into a final numeric receipt. [PVAPI substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) requires the registered computed value. Its [relative-unit rules](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) retain additional font-size/line-height dependencies, including root-relative cases. Consequently the `<length>` result `1px` needs its normal registered conversion; a substituted `1em` cannot bypass FontSize readiness or the semantic unit node. These rules are kept separate from the selected lookup trace.

This differs from [Variables 1, 16 June 2022 CR, section 2.3](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#cycles). That snapshot required graph edges for references inside fallback arguments as well. Under that historical rule the example has a self-edge despite its valid primary. The current draft algorithm is the authority used here; this note does not silently rewrite historical model assumptions or claim those two specifications have identical behavior. The published local ReferenceWalk already follows selected fallbacks and cites the corresponding later resolution.

Rejected route: adding every syntactically present fallback as a current substitution invocation would import the historical rule and would not follow current replace-var step 4. Conversely, deleting registered unit edges because they do not appear as lookup requests would ignore PVAPI's additional constraints.
