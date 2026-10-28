# Current-base Round arithmetic prerequisite

The existing context-dependent Round quotient defect is the arithmetic prerequisite for stepped deferral. It is already browser-observed, not merely a new proposed regression: the historical six-case diagnostic has four calibrated failures and two controls. The same-unit opacity expression is a distinct **predicted exposure route** into that same arithmetic family after deferral. It has not been run in this package and adds no bug count.

The candidate changes only the finite branch of `CalcNode::resolve_internal` in generic calc. Its current base is the committed b1cae69e source, SHA b9a36918…. It carries the exact prior reviewed f64 remainder reconstruction onto that base: compute the truncating remainder, return exact multiples unchanged, reconstruct toward-zero and adjacent multiples in f64, select the requested bound, then convert once to f32. It does not use a type whitelist or reject contextual inputs.

Accepted125's NaN-first runtime classification is retained exactly. The special zero-step/infinity branches, child evaluation/type joining, accepted126's parse-time finite-zero correction, and shared `ModRemOp::apply` including accepted128 are byte-identical. Removing this one replacement recovers the entire base. This is preservation of bodies, not sufficient evidence of all composed behavior. The new readiness guards remain a separate proposal; this package does not activate them or claim to repair consumer retention.

## Why this route matters

`CalcNumeric::resolve` maps leaves in Context and resolves the reconstructed tree without resimplifying. A mixed-unit sign input already prevents early Round folding and reaches the bad quotient branch on the original source. The historical browser run proves the observable result, though it does not provide a native branch trace.

For `opacity: sign(round(down, 1em, 0.3333333432674407958984375em) - 0.8px)` at font1px, the current early same-unit fold is predicted to produce opacity0. Deferral alone can route the resolved operands to the quotient branch and produce1 instead. With the arithmetic repair, the selected multiple is about0.6667px and opacity remains0. At font2px both expected routes give1; at zero basis the invalid math reaches top-level opacity0. This is a regression-prevention witness, not evidence that the current branch already fails that same-unit case.

The length-percentage pipeline may resimplify after context conversion; a plain width example therefore cannot establish this numeric evaluator route. ModRem already shares its operation across stages. The direct Round finite branch needs the coherent arithmetic repair regardless of how the eventual context scheduler is implemented.

## Bounded executable evidence

The reused exact-Fraction/binary32 oracle and extracted scalar branch adapter ran successfully:494 operand pairs ×4 strategies =1976 checks;288 old finite differences, zero candidate differences;452 special-value checks unchanged. Zero signs, exact multiples and the four historical directed witnesses are explicit checks. The old branch is a decisive negative control. The rejected prior f32 reconstruction and its13 one-ULP mismatches remain in the immutable predecessor; it is not silently revived.

These are finite sampled checks, not exhaustive IEEE proof. The adapter starts after child resolution/type joining, supplies a unit type tag and numeric-zero trait, and does not compile CalcNode or certify native providers. rustc1.92.0 compiled only a temporary helper; scratch was removed. No configured Gecko check, linked browser, performance measurement or canonical Lean change occurred. Replay `check_helper.py` only in a separate copy: it regenerates helper.rs and its JSON receipts; do not execute it inside this sealed package.

The patch applies and reverses in private scratch. Changed lines match the repository formatter. Whole-file rustfmt reports two inherited differences (import order and an unrelated Random tuple); the base/candidate formatted delta is exactly this same arithmetic replacement, and those unrelated lines were preserved.

## Witnesses and next execution

The historical14-case WPT is byte-identical. A separate four-case WPT captures all four font snapshots before assertions and exports them in diagnostics: down/to-zero exposure plus nearest/exact-quarter controls. Its comparisons require admitted syntax, actual font, literal calibration, resolved-pixel reference and repeated-read stability. They are prospective tests, not observed passes. Total proposed assertions18.

`observe.js` is a standalone callable diagnostic: load it then run `await observeRoundQuotientPrerequisite()`. It returns all34 snapshots across the original six routes and four exposure/controls. It creates and removes its own iframe, retains the target declaration across font changes, records support/specification/computed/literal/resolved values, and never treats unsupported syntax as a pass. Caller/browser/source identity must be recorded by root. No expected failure count is imposed.

Next: run this diagnostic on the exact current build; typecheck/build the arithmetic-only candidate and replay original14 plus new4 with existing preserved controls. For the integrated stepped candidate, repeat the exposure cases and the original18 zero-basis cases, then the existing consumer suite. Accepted125/126/128 WPTs and broad Round/signed-zero/unresolved-serialization controls are pinned in CONTROL-PINS. Preserve full baseline signatures, including existing failures.

This arithmetic prerequisite does not settle parse-time NaN classification, contextual steps/bezier/linear storage and admission, targetless API policy, dependency publication/invalidation, or generic integer export. Those remain explicit integration obligations; restoring the arithmetic witnesses is not acceptance of the full deferred-operation patch. The independent linear second-position crash guard is a separate current-source defect and can proceed without this arithmetic work.
