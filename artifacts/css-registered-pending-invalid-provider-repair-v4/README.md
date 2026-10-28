# Registered-provider default proposal v4

Successor to sealed v3, changing only `drop(state)` after the root substitution's final cycle-participant check and before mutable context operations. The actual v3 native build failed with eight E0502 errors because the state destructor kept references to substitution storage alive until function exit. The final check consumes all needed state information; releasing that state ends these borrows without cloning names or changing cycle/default semantics. The cascade candidate is byte-identical to v3.

The full two-file patch still applies to the original committed baseline. V3-DELTA.patch is the one-line compile correction. Transport/format checks do not establish native compilation; root will build this successor separately. All v3 review limits remain: custom-property recursive participant scope only, initial-value CSS-rule policy unresolved, no native acceptance or new bug count.
