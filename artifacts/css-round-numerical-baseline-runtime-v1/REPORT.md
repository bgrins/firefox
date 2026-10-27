# Numerical baseline on the installed stack

Local capture61360 exited0 after42 cases and four OK harnesses. The underlying WPT command exited1 for failing assertions; this is a completed diagnostic, not an all-passing test run. Classification passes with11PASS/31FAIL:29 calibrated numerical mismatches and two nonnormative implementation-policy differences. There is no required failure count and no new accepted fix.

| Family | Pass | Fail | Interpretation |
| --- | ---: | ---: | --- |
| Finite negative zero observed through pow |4|4|Four final negative-zero mismatches; all four preservation cases pass.|
| Runtime NaN |2|8|All eight final NaN-propagation targets fail; finite controls pass.|
| Deferred value with infinite step |2|17|Observed route and all sixteen independently sampled contexts fail; two constant-integer controls pass.|
| Integer admission policy |3|2|Two expressions are admitted despite predicted rejection; these are not counted as normative bugs.|

All admission, setter retention, finite/range, font/sign and repeat-stability calibrations preceding numerical targets pass. Failed targets return finite opacity0.5 or1 instead of0. The two policy differences preserve setter/support agreement and stable admission. Their exact expressions, serializations and expected/observed booleans are retained in raw logs and CLASSIFICATION.json. The deferred-value repair needs renewed admission analysis before comparison.

No native candidate was applied or build run. The full605-role map preserves the original599 roles and six new absences,72 sources,21 installed identities,925 staged payloads and42 modified native paths. Four temporary fixtures were removed by exact body/inode ownership; the WPT process group is absent. FINAL-PINS explicitly retains every absence, and the root receipt binds its hash. The installed123/124 source and binaries remain unchanged. Independent terminal review is pending at sealing.
