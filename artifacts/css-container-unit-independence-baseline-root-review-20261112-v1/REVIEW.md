# Container units in registered initial values

Status: baseline reproduction accepted after independent source and report inspection. The repair is not installed or tested. This is one pre-existing conformance defect, not 72 separate bugs or a new security finding.

The [registration algorithm](https://drafts.css-houdini.org/css-properties-values-api-1/#dom-css-registerproperty) rejects a typed initial value when computing it requires CSS-dependent information. Container-relative lengths depend on ancestor selection and sizing; their ordinary validity as lengths does not make them valid registered initial values. The existing upstream computational-independence WPT already expects rejection.

The original six-case WPT reuses `--x`. Its first cqw case is incorrectly registered, so the other five tests fail with InvalidModificationError rather than testing their own units' computational independence. Its six existing failures therefore cannot independently establish acceptance of all six units.

The new diagnostic assigns a unique property name to every case. Root read the complete execution/assertion code and independently matched every report entry to its declared case. The 72 failing registration cases cover all six units, both CSS.registerProperty and @property, both length and length-percentage syntax, and direct, calc, and additive-calc forms. JavaScript succeeds where SyntaxError was expected; @property exposes a computed initial value where the invalid registration should have been ignored.

All 18 ordinary width-support controls pass. All 16 registration controls pass, covering absolute and viewport lengths as valid initial values and font-dependent lengths as invalid. The WPT file itself finishes OK; its process exits 1 because its 72 expected-to-pass assertions fail. That exit is preserved as evidence, not treated as a passing regression suite.

Root authenticated 13 retained files, checked all 106 distinct case IDs, independently constructed the complete registration-case matrix, verified matching before/after binary manifests against the current restored build, and confirmed the temporary probe is gone. `VERIFICATION.json` records the counts. `SOURCE-INPUTS.json` pins the precise evidence files in the author's capsule. Root did not rerun the browser.

Next: inspect the isolated parser guard patch and permanent WPT, run an actual rebuilt browser against the same diagnostic and surrounding registration/container-unit regressions, then package the native fix and regression separately from this research. No accepted fix or commit count changes yet. The investigation came from source/spec correspondence work; no Lean theorem discovered or proved this browser defect.
