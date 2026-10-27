# Counter commit packaging draft

No acceptance or ledger mutation is performed by this package. The live comparison is still running. DRAFT-ENTRY.json deliberately keeps observed candidate results and signed commit fields unset; expected fields are a comparison policy, not observations.

## Reviewer summary

Appending a counter reset, set or increment can be last in its containment scope's local list while retained uses exist in child scopes. The local calculation leaves those uses stale. Marking the counter name dirty when child scopes exist reuses the existing parent-before-child recalculation and text notification. Childless scopes keep the existing path. The new WPT covers three changes, counter()/counters(), direct/nested containment, and trailing-use controls. It captures the immediate mutation result before a fresh construction can affect invalidation.

The standalone commit must contain exactly nsCounterManager.cpp, nsCounterManager.h and css/css-contain/counter-scoping-append-invalidation.html. It introduces no fields and has no dependency on the preceding quote fix. Put research, models, runtime evidence and acceptance in its immediate parent research commit. Reviewer lookup reports the Herald group #layout-reviewers.

## Before accepting or signing the native fix

Require all four captures complete with no infrastructure faults: counter rows 12 PASS/12 FAIL, 24 PASS, 12 PASS/12 FAIL, 24 PASS. Both originals must agree exactly and both candidates must agree exactly; this is not merely a count comparison. Preserve all 64 quote subtests, eight existing counter regression ends, and two normal harness ends. Require all three builds to finish successfully with their owned process groups absent, the driver's success RESULT, no FAILURE, final candidate source/binary preservation, and independent terminal review. The old tool session is unavailable; report any substituted process-terminal evidence accurately rather than inventing an observed outer exit code.

The WPT lint already has zero errors for the exact fixture hash. No rerun is required for unchanged bytes. Confirm the current native/WPT patch equals the proposal and the eventual commit delta has exactly these three files. Sign and verify the research and native commits, preserving unrelated work and the nested library. No push.

Populate DRAFT-ACCEPTANCE in a new acceptance directory with actual reviewed evidence and references. Populate DRAFT-ENTRY from actual observed results, remove expected_* keys, set status COMMITTED_NATIVE_WPT, fill commits, signature/installation booleans and authenticated terminal/commit receipts. Do not present expected results as measured data.

## Five current ledgers after successful signing

1. CURRENT-COMMITS.json: append populated entry to new_queue, set committed_native_fixes 134 -> 135. Keep accepted_pending_native_fixes = 1, accepted_pending_native_fixes_on_hold = 1 and accepted_pending_native_fixes_excluding_holds = 0: this schema includes held fix 120 in the first field. Preserve latest_signing in local_signing_history, replace latest_signing with the new signed fix136 record, and point latest_research_signing/latest_verified_working_epoch to real new receipts, retaining histories. Add latest_counter_fix, without deleting latest_quote_fix. No canonical coverage increment. In the existing fix135 entry, replace the stale limitation 'Adjacent counter append hypothesis is unrun and not included in this fix.' with 'Adjacent counter append invalidation is tracked separately as fix 136.'
2. GROUPS.json: append the exact same entry to the Text and fonts group's fixes. Set that group's committed/total 14 -> 15; its pending/held remain zero. Top-level committed/accepted 134 -> 135, tracked 135 -> 136, accepted_pending remains 0, held remains 1; head becomes the signed native fix hash. Correct fix135's stale adjacent-counter limitation here too. Preserve all other groups and canonical checkpoint counts.
3. PLAN-OF-RECORD.md: insert the new current summary immediately below the title, keep the quote summary but replace its last stale 'unrun and uncounted' sentence with a pointer to fix136. Update the first current count banner, Text and fonts row, total row, and current 'All 134 accepted fixes remain committed' sentence to 135. Execution item1 should retain both independently reviewable quote135 and counter136 fixes. Animation integration stays the next substantive project task.
4. BUGFIX-COMMITS.md: insert the same current summary below the title, add the new row before the first '| 135: Contained quote append |' row, and make the same current summary/banner/table/count corrections. Leave older historical narratives and their counts untouched.
5. css-fix-readout-20261023/README.md: same current summary, new commit row, first banner/current table/count corrections. The later 'Historical checkpoint text follows' section and its older tables are historical and must not be blanket-replaced.

Suggested current summary after evidence and signatures are verified:

Fix 136, contained counter append invalidation, is committed as `<native>` after research `<research>`. The original/candidate/original/candidate comparison gives 12 PASS + 12 FAIL / 24 PASS / 12 PASS + 12 FAIL / 24 PASS. All 64 quote subtests and eight existing counter regressions stay passing. Three builds and WPT lint pass. Tentative P3 visual correctness. Source audit and browser reproduction found the issue; the separate Lean model corroborates conditional delivery laws (14 audits, 12 examples, five rejected false claims). No clean-upstream build, security, measured performance or universal native-refinement claim.

Suggested commit-table row:

| 136: Contained counter append | `<native>` | `<research>` |

The final banner is: **135 accepted fixes: 135 committed locally, 0 accepted pending, and 1 additional held repair excluded.** The Text and fonts group becomes 15. The numbered sequence reaches136 because held120 remains excluded from accepted counts.
