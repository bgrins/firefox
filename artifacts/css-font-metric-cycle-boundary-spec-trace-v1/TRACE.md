# Registered font metrics and cycle policy

**Question:** Does the current specification give a complete cycle policy for a registered length that needs font metrics and is itself consumed by a font-affecting property?

**Scenario:** A valid registered `<length>` with independent initial value contains `1ch`. Distinguish a separate selected literal weight from a weight whose selected value consumes that registered length. Fonts are available; unrelated font/zoom/layout inputs are fixed. No unused fallback is involved.

1. [PVAPI §2.4](https://drafts.css-houdini.org/css-properties-values-api-1/) converts a registered dimension literal to its canonical unit. [§2.7](https://drafts.css-houdini.org/css-properties-values-api-1/) substitutes its computed value, rather than preserving the original relative unit for each eventual consumer.
2. [Values4 font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths) defines ch from the selected font's zero-glyph advance. Its font-affecting-property exception uses parent metrics. Applying that exception to a registered value merely because it is later consumed by font-weight would require a further bridge; the substituted value has already been computed.
3. [PVAPI §2.7.1](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) explicitly adds current FontSize/LineHeight and specified root-unit edges. Its own registered-em→font-size example is cyclic. This section does not explicitly supply a Weight metric edge or an inherited-metric escape for registered ch.
4. [Current Variables replacement](https://drafts.csswg.org/css-variables-1/) obtains the custom property's computed value. [Values5 substitution](https://drafts.csswg.org/css-values-5/) guards recursive substitution contexts. This read does not establish how a later font-metric computation extends those guard lifetimes or maps a metric readiness wait to CSS invalidation. The old PVAPI graph wording and current substitution wording need an explicit integration argument.
5. [CSSWG8169](https://github.com/w3c/csswg-drafts/issues/8169) resolved the direct font-affecting parent-metric rule while assigning a separate action for typed custom properties. [Houdini1080](https://github.com/w3c/css-houdini-drafts/issues/1080) specifically discusses a registered ex/weight cycle missing from the graph. [CSSWG9517](https://github.com/w3c/csswg-drafts/issues/9517) follows up the custom-property question. The retrieved issue pages display open unresolved follow-ups; their cached status is not a fresh GitHub API verification.

**Verdict: INCONCLUSIVE** for the complete registered metric-cycle policy. This does not make the separate literal-weight case uncertain: no circular read is present there, and the canonical registered ch value must use the element's selected font. The existing observed wrong-weight result is useful acyclic repair evidence. It does not select an outcome for a genuine registered metric/weight recurrence.

| Proposed shortcut | Missing justification |
|---|---|
| Resolve every registered metric against the parent | Discards the current-element meaning in the independent case. |
| Add every font scheduling edge to FontSize's CSS SCC | Conflates completed size with unfinished metrics and can create a false cycle. |
| Treat any Pending prerequisite as a cycle | Pending may be an acyclic computation that has not finished. |
| Use current builder font on recurrence | No proof that it equals either the final selected font or a specified cycle default. |

Implementation can therefore repair acyclic metric readiness separately, while naming and testing a deliberate experimental policy for actual repeated metric readiness. That policy must not rewrite completed em/size values or activate merely because metrics are Pending.

## Access limits

This is a manual primary-prose trace, not an exhaustive indexed call graph. `webspec-index specs` returned an empty list; Values4 query/exists failed with a readonly database error, and the Houdini URL was unsupported. Anchor validation did not complete. GitHub API access via web failed, and direct saved fetches failed DNS; cache-busting issue URLs also failed. PRIMARY.json records the primary reads and their freshness limits. No issue was filed or modified, no native algorithm or browser was run.
