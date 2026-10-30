# trace: `CSS-VALUES-5#property-replacement` -> `CSS-VALUES-5#cyclic-substitution-contexts`

Max depth 9, kind `step`. Found 3 trace(s).

## Trace 1 (2 hop(s))

1) `CSS-VALUES-5#property-replacement` step 1 calls `CSS-VALUES-5#substitute-arbitrary-substitution-function`
   > Substitute arbitrary substitution functions in prop’s value, given «"property", prop’s name» as the substitution context. Let result be the returned component value sequence.

2) `CSS-VALUES-5#substitute-arbitrary-substitution-function` step 1 calls `CSS-VALUES-5#cyclic-substitution-contexts`
   > Guard context for the remainder of this algorithm. If context is marked as a cyclic substitution context, return the guaranteed-invalid value.

## Trace 2 (2 hop(s))

1) `CSS-VALUES-5#property-replacement` step 1 calls `CSS-VALUES-5#substitute-arbitrary-substitution-function`
   > Substitute arbitrary substitution functions in prop’s value, given «"property", prop’s name» as the substitution context. Let result be the returned component value sequence.

2) `CSS-VALUES-5#substitute-arbitrary-substitution-function` step 3 calls `CSS-VALUES-5#cyclic-substitution-contexts`
   > If context is marked as a cyclic substitution context, return the guaranteed-invalid value. Nested arbitrary substitution functions may have marked context as cyclic in step 2.

## Trace 3 (2 hop(s))

1) `CSS-VALUES-5#property-replacement` step 1 calls `CSS-VALUES-5#substitute-arbitrary-substitution-function`
   > Substitute arbitrary substitution functions in prop’s value, given «"property", prop’s name» as the substitution context. Let result be the returned component value sequence.

2) `CSS-VALUES-5#substitute-arbitrary-substitution-function` step 3 calls `CSS-VALUES-5#cyclic-substitution-contexts`
   > If context is marked as a cyclic substitution context, return the guaranteed-invalid value. Nested arbitrary substitution functions may have marked context as cyclic in step 2.

