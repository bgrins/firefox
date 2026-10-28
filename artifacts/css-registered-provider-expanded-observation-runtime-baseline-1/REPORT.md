# Expanded provider baseline

The accepted zoom139 build completed 775 assertions: 679 PASS and 96 FAIL, with 30 OK harness endings and six passing reftests. All prior 668 full assertion signatures are unchanged. Source, index, binary and metadata preservation passed; the owned process group is absent and its temporary profile root was removed. WPT returned 1 for investigative failures; the complete observation wrapper returned 0.

| Additional page | PASS | FAIL |
|---|---:|---:|
| Line-height-only readiness | 14 | 2 |
| Provider defaults supplement | 16 | 16 |
| Missing references and cycle controls | 34 | 0 |
| Conditional initial-color observations | 0 | 4 |
| JavaScript initial-independence probes | 12 | 9 |

The 34 error/cycle controls are baseline passes, not newly found browser bugs. They include the A/B/C fallback counterexample for our uncompiled draft repair. All 12 registration controls pass, including font-relative rejection, symbolic currentcolor and identical-image light-dark acceptance. Nine dependent initials are accepted instead of throwing SyntaxError: container lengths, including calc/transform wrappers; scheme-dependent colors; and nested gradient colors. These are new local observable leads, with source/spec follow-up and release confirmation still pending.

The four color rows fail their no-declaration initial calibration. Their recorded snapshots show ordinary invalid/missing provider defaults following light/red, dark/blue, light/red, while no-declaration registered initial values remain red. Their current @property admission oracle is conditional; they cannot establish a provider bug alone. A candidate that uses the initial cache may change target values while retaining FAIL status, so full messages and snapshots must be compared, not only status counts.

Next install/build the reviewed participant-preserving provider-default candidate and repeat exactly this suite. Keep color-policy changes visible and resolve the current @property specification distinction before acceptance. No new fix is accepted.
