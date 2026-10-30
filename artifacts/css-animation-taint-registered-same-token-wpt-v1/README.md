# Registered same-token animation taint regression

Three focused tentative WPT callbacks cover universal registration, typed registration and a literal sink control. Each establishes an ordinary vertical-rl value before activating valid constant vertical-rl keyframes. Source tokens stay unchanged while animation provenance is introduced. A later underlying mutation uses horizontal-tb, distinct from animated vertical-rl and fallback vertical-lr.

The expected non-animatable sink fallback is the same tentative rule used in the existing animation-taint suite. These callbacks add registered equal-token activation coverage; the installed ordering experiment directly exercised typed registration, while this new page also tests universal registration. No browser result is claimed for the exact new page before execution.

Registration syntax/non-inheritance is calibrated before creating the subject. Both phases collect the first sink read and three passive-frame reads before source/timing/identity diagnostics. Calibration assertions run before sink verdicts, so setup failures cannot masquerade as taint regressions. The before-animation computed read intentionally establishes an existing value to test metadata-only invalidation. Its sink is recorded without a policy assertion, preserving the separate unresolved name-global versus active-value scope question. No diagnostic report transport or extra global browser hooks are included.

The existing120-case suite must remain an exact subset when this page is added. Clean-provider original and candidate outcomes must be observed rather than inferred from held-provider or installed-browser results. This artifact is prepared research, not a new accepted fix or standalone native commit.
