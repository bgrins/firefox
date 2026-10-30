# trace: `CSS-PROPERTIES-VALUES-API-1#register-a-custom-property` -> `CSS-PROPERTIES-VALUES-API-1#computationally-independent`

Max depth 9, kind `step`. Found 1 trace(s).

## Trace 1 (1 hop(s))

1) `CSS-PROPERTIES-VALUES-API-1#register-a-custom-property` step 4 calls `CSS-PROPERTIES-VALUES-API-1#computationally-independent`
   > If syntax definition is the universal syntax definition, and initialValue is not present, let parsed initial value be empty. This must be treated identically to the "default" initial value of custom properties, as defined in [css-variables]. Skip to the next step of this algorithm. Otherwise, if syntax definition is the universal syntax definition, parse initialValue as a <declaration-value>. If this fails, throw a SyntaxError and exit this algorithm. Otherwise, let parsed initial value be the parsed result. Skip to the next step of this algorithm. Otherwise, if initialValue is not present, throw a SyntaxError and exit this algorithm. Otherwise, parse initialValue according to syntax definition. If this fails, throw a SyntaxError and exit this algorithm. Otherwise, let parsed initial value be the parsed result. If parsed initial value is not computationally independent, throw a SyntaxError and exit this algorithm.

