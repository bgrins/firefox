# When are relative-unit cycle edges collected for registered properties?

Draft question for CSSWG; not submitted.

For a non-inherited registered `<length>` with initial value `0px`, consider:

```css
.target {
  --size: 20px;
  --v: var(--size, 1em);
  font-size: var(--v);
}
```

Should the unused `1em` fallback add a font-size dependency edge under [Properties and Values API §2.7.1](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles)? Does “contains” inspect the value after substitution, or can this cycle rule inspect the original token stream while substitution is being scheduled?

[Variables](https://drafts.csswg.org/css-variables-1/#using-variables) now short-circuits unused fallbacks, and [Values 5](https://drafts.csswg.org/css-values-5/#resolve-property) places substitution before other value introspection. The registration specification still describes additional dependency-graph edges without identifying that phase.

Installed Firefox 158 and Chrome 156 both resolve this registered value to `0px`, with font-size inherited. Removing the primary correctly exercises the genuine `1em` cycle; a literal `20px` control resolves normally. The same contrast persists when the primary changes to `30px`. These observations do not settle the normative question. An explicit unused-unit example or a link between the cycle rule and substitution algorithm would resolve the model's remaining premise.
