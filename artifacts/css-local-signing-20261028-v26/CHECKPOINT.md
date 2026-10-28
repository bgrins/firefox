# CSS verification checkpoint, 2026-10-28

Accepted fixes remain 138, all committed locally; 139 tracked entries include held fix 120. No new native fix is accepted in this checkpoint.

The new Lean fallback-cycle witness checks seven declarations and rejects three false claims. It formalizes a counterexample found during source review, not an automatically discovered native-code proof. The canonical CSS Lean repository is unchanged.

Installed Firefox 158 reproduced the provider-readiness discrepancy: 28 PASS and four FAIL across 32 assertions, with all full signatures matching the earlier local observations. This used the current repository WPT preferences, not a stock browser-tab profile.

The expanded accepted-build baseline completed 775 assertions: 679 PASS and 96 FAIL, 30 OK harness endings and six passing reftests. All prior 668 full signatures are unchanged. All 34 missing-reference/cycle regression controls pass. Nine JavaScript registration-independence probes fail among 21 assertions; these remain investigation leads. Four color-context observations have a conditional specification oracle, and their complete snapshots must be compared even if both runs report FAIL.

The provider-default v4 experimental patch is preserved with exact base/candidate source snapshots and its patch. Both live modified native files match the committed candidate snapshots byte for byte. The first compilation failed with borrow errors; the one-line lifetime correction compiled successfully in provider-default-candidate-build-2. A subsequent paired browser comparison completed all 775 assertions: 20 FAIL-to-PASS improvements, four same-FAIL color behavior changes, and 751 unchanged full signatures. The candidate remains unaccepted because ordinary invalid color defaults change from target dark blue to cached red. Evidence is preserved in css-registered-provider-expanded-observation-runtime-candidate-1 and queued separately for a further research commit. Compilation and focused improvements alone do not establish correctness.

DRAFTS.json freezes the earlier disabled, unsealed candidate observer preparation and the unpublished roadmap proposal. A successor observer v3 has since run successfully; the archived v2 remains disabled. Neither is an executed or authoritative replacement. Any future observer run must bind the then-current HEAD and preservation epoch; preserve the original baseline and full assertion messages.

All signing changes are research artifacts. The two live experimental Rust edits, parked prototypes, recovery snapshots and unfinished project files remain preserved. The index is checked empty after each commit. No push, Try job or review submission is part of this checkpoint.

Further work after the first signing attempts is queued in artifacts/css-provider-post-signing-progress-v1/COMPLETED-SELECTION.json. Installed release Firefox completed the expanded registration probe with 27 PASS and 41 FAIL across 68 assertions; these are conformance cases, not 41 independently accepted bugs. The current continuation plan is artifacts/stylo-bloom-tools/PROVIDER-PLAN-20261028.md.
