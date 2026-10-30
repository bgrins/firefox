# Registered keyframe defaulting observations

Both installed Firefox158 and portable Chrome156 completed all three calibration callbacks with harnessOK. Root verified raw request/report equality, exact served resources, owned process/profile absence and saved runtime seals. Independent JavaScript calibration replay is pending. Firefox owner61007/b0f784/0; Chrome owner12941/aee22e/0.

| Case | Firefox custom value, initial → ordinary mutation | Chrome custom value | Firefox sink | Chrome sink |
| --- | --- | --- | --- | --- |
| Invalid typed keyframes (`one two`) | horizontal-tb → horizontal-tb | horizontal-tb → horizontal-tb | horizontal-tb → horizontal-tb | horizontal-tb → horizontal-tb |
| Valid typed keyframes | vertical-rl → vertical-rl | vertical-rl → vertical-rl | vertical-rl → vertical-rl | vertical-rl → vertical-lr |
| Literal sink control | vertical-rl → vertical-rl | vertical-rl → vertical-rl | vertical-lr → vertical-lr | vertical-lr → vertical-lr |

Each sink entry represents four equal readings. Custom-value and timing diagnostics occur afterward; they are not a simultaneous snapshot. The invalid trajectory agrees with the registered initial value and does not follow the changed underlying declaration. This does not prove which internal filtering/defaulting path produced it. The invalid sink has no asserted normative verdict.

The Chrome valid case changes sink after the ordinary mutation while the animated custom value stays the same. This differs from the earlier registered-scope observation. A prior subject-style read, equal-token animation introduction and an independent opacity driver distinguish the new fixture. Their individual causal effects have not been isolated. Treat this as an ordering/invalidation discriminator to investigate, not a universal Chrome oracle or a confirmed additional bug report.

The calibration-only WPT passes do not establish correct animation taint. No native candidate, accepted fix, or canonical Lean coverage is added by these runs. The portable Chrome input remains needed for the follow-up discriminator; both owned temporary profiles were removed.
