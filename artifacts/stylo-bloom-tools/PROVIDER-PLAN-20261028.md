# Provider and registration verification: current continuation plan

This supplements PLAN-OF-RECORD.md with the completed 2026-10-28 candidate experiment. Accepted fixes remain 138, all committed locally; held fix 120 is excluded from that total. Signing of five further research groups is pending after two 1Password errors; the first 36-file group remains staged. No native fix is accepted by this update.

## Evidence and current decision

- Installed Firefox 158 reproduces the original readiness discrepancy: 28 PASS / 4 FAIL across 32 assertions under WPT preferences.
- The expanded accepted-build baseline completes 775 assertions: 679 PASS / 96 FAIL.
- The compiled provider-default v4 candidate completes the same 775 assertions: 699 PASS / 76 FAIL. All 64 readiness assertions and 34 missing-reference/cycle controls pass. The four same-FAIL color cases change ordinary invalid-default dark-mode output from blue to cached red. Keep v4 unaccepted pending a principled context/policy decision. See ../css-registered-provider-expanded-observation-runtime-candidate-1/REPORT.md and COMPARISON.json.
- Installed release Firefox 158 now confirms the JS admission failures: 27 PASS / 41 FAIL across 68 assertions, two OK harness endings, with all failures caused by missing SyntaxError after successful ordinary syntax calibration. The original 21 full signatures match the local baseline. This is 41 conformance cases, not 41 independent bugs. See ../css-registered-initial-release-observation-runtime-1/REPORT.md. Nine of the original 21 assertions fail. The separate implementation audit found that initial-cache construction reparses the value, so validating a selected alternative only at JS entry is insufficient. The selected grammar interpretation must survive admission and cache computation.
- The canonical CSS Lean library remains unchanged. The new alternative-selection model adds 22 checked declarations and six rejected false claims, with independent bounded review. The cycle and alternative-selection models are scoped research artifacts; they do not prove native Rust equivalence or comprehensive CSS correctness.

## Ordered work

1. Preserve the completed release68 and candidate775 evidence. Keep the five unrun ambiguous image/normalization observations outside normative pass/fail claims. Preserve syntax-alternative ordering, all list members and nested positive controls.
2. Advance the inactive seven-path AST inspection prototype into a compiled, tested implementation. Implement independence validation after ordinary grammar selection, preserving the selected interpretation through initial-cache construction. Keep JS registration and unresolved shared @property policy distinct. Do not reject broad types or accept unknown traversal cases to pass a small suite.
3. Resolve the provider-default candidate's actual color-context behavior change. The four observed deltas come from the ordinary post-graph invalid-value handler changing to cached initials; they do not by themselves prove all recursive defaults require a wider resolver. Preserve the ordinary target-context contract and separately establish whether recursive defaults are ready, context-independent, or require an explicit demand and retry. Compare full snapshots, preserve inherited values/taint/cycle participation/zoom, and do not hide the issue with a type whitelist.
4. When validation supports acceptance, package each confirmed fix and its WPT together in one standalone commit, with research/tooling preceding. Resume prepared signed research commits when 1Password works; do not bypass signing or discard the staged patch.
5. Rebase the parked numeric-admission and production resolver work over accepted zoom fix 139. Continue ordinary/animated resolution, current-base freshness, selected dependency edges, endpoint/effect isolation and memory reporting.
6. Resume Bloom milestones 1–6 and broader specification correspondence. Keep local-only work, the original 50 parked prototype snapshots, the 140-entry recovery inventory and unfinished project files preserved.

The main roadmap consolidation proposal remains unpublished while the signed checkpoint is pending. This supplement is the current execution plan; earlier intermediate statuses in the main document must be read with this update.
