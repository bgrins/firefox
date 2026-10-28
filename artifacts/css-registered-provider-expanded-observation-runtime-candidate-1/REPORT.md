# Provider-default candidate comparison

The compiled v4 candidate changes the exact 775-assertion baseline from 679 PASS / 96 FAIL to 699 PASS / 76 FAIL. Thirty harness endings remain OK and six reftests remain PASS. The observation wrapper completed successfully, with WPT returning 1 for the remaining expected research failures. All source, binary, application, index and temporary-process preservation checks passed; the staged 36-file research commit is unchanged.

Twenty readiness assertions change FAIL to PASS: mixed logical-viewport/line-height 2, line-height-only 2, and supplemental defaults 16. All 64 readiness assertions now pass. The 34 missing-reference/cycle assertions stay passing. The original 668 subset changes only its two mixed-readiness failures to PASS; the earlier broad/zoom assertions retain their signatures.

Four color-context tests remain FAIL but their full snapshots change. On the dark-scheme step, ordinary invalid or missing-reference registered defaults previously produced blue; the candidate returns cached red. Direct literal light-dark remains blue and the no-declaration registered initial remains red. This changes ordinary invalid-default behavior, not merely failure diagnostics. The shared @property admission/computation policy is unresolved in the captured specification research, so this result does not establish a new normative bug or justify accepting the cached-default behavior.

The other 751 full assertion signatures are unchanged. No formerly passing assertion failed, but that alone would miss the four behavior changes. COMPARISON.json preserves complete before/after messages and parsed color snapshots. compare.py replays both raw logs and requires exact assertion identities, counts, terminal statuses and preservation evidence.

The patch remains experimental and unaccepted. The next implementation decision must address context-dependent initial values without a syntax whitelist or suppressing these observations. Valid pending-provider scheduling and broader resolver integration remain separate unfinished work. Accepted fixes remain 138; no new standalone fix is credited here.

Build: provider-default-candidate-build-2. Observer: css-registered-provider-expanded-observation-v3. Outer execution: session 72723, launch 481cbf, terminal 3024cf, exit 0. The browser binary was built before the 36 research files were staged; the observer explicitly records that artifact-only index delta without rewriting build provenance.
