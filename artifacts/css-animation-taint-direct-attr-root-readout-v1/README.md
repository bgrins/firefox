# Direct attr substitution: installed-browser evidence

Both installed browsers support this typed attr syntax and recursive substitution in attribute text. The literal and untainted controls pass, as do independently recalculated custom-value, driver, identity and lifecycle checks.

| Active case | Firefox 158 | Chrome 156 |
|---|---|---|
| Tainted var inside attribute text | horizontal-tb | vertical-lr |
| Matched direct tainted var | horizontal-tb | vertical-lr |
| Untainted var inside attribute text | horizontal-tb | horizontal-tb |
| Literal typed attribute | vertical-lr | vertical-lr |

All four first/frame samples agree within each case. The animated token is horizontal-tb; the nested var fallback is vertical-lr; outer attr fallback and inherited writing-mode are vertical-rl. Chrome's outputs therefore match the nested-fallback prediction; Firefox outputs the animated token in both tainted cases. No unsupported-syntax or recursive-substitution control failed.

The direct-property context interpretation is documented in ../css-animation-taint-typed-attr-spec-followup-v1/README.md. Its context-to-property binding remains an explicit interpretation; these observations do not prove an internal implementation route or settle name-versus-value taint outside the active CSS scenario. Alias infection through typed attr remains a separate unresolved question. There is no security/exfiltration claim.

The frozen source audit identifies a potential limitation of the current native proposal: resolving attribute text into cached tokens can discard the nested fallback before a property consumes it. A taint flag alone cannot recover that expression. This route must be tested on the candidate after its current build and 106-case trial; no candidate attr outcome exists yet. The installed-browser evidence does not add an accepted fix.

Firefox session7576, launch4a30e8, terminal338f8b/0, independent cleanup e99a9a/0. Chrome session62892, launch801edf, terminalc8b7ea/0, independent cleanup cb008a/0. Root independently checked raw request/report equality and recalculated all reference checks and active predictions; peer replays d1b28a/0 and4a0928/0 use the pinned JavaScript functions. Both owned process groups and temporary profiles are absent. No preference overrides or existing user profiles were used; these are not performance measurements.
