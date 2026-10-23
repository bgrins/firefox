# Four-phase hidden-flex WPT driver review

Verdict: **GO_REVERSIBLE_DIAGNOSTIC_ONLY** for the exact authenticated inputs. No build, browser, source swap or Git mutation was executed by this reviewer.

## Authentication

- INPUTS.json: `cbabee42336e512b92cc43d463dadda148abc7fa6e119c1e2cfeb21005835ce2`
- experiment.py: `4278966f479bce8163253fef75f30717d31cac22c9148cc9f4d41ef574d7d508`
- run_wpt.py: `edb300cb17286a9c01ca0776d931560d7e73dcb0543cc57c2bd880c215f2a7cd`
- HEAD at preflight: `209dc941c40a5e0b34724bdac38b607b1f67dda6`; index empty, exact staged-entry hash matched.

Independently checked all 52 payload hashes, 16 existing-test/support hashes, 25 current source hashes, all 20 original/live and HEAD/Git source pairs, test installation absence-or-identical-byte conditions, and Python syntax without executing the driver. Both scripts match the reviewed draft snapshots. Final CONFIG supplies the source/support coverage that was pending in the draft. `FINAL-PREFLIGHT.json` retains counts and external pins.

Read all three new tests. `ROSTER-CHECK.json` independently reconstructs their loops' exact ordered names: 48 measuring cases, 32 fixed-size cases and 44 placement/descendant/anonymous/positioned cases. The measuring test is byte-identical to the previously reviewed release-derived proposal. The expanded tests retain explicit arithmetic expectations and visible reference calibration; all phases are sampled before assertions. Ahem readiness is awaited for text-range cases. Multicol controls do not establish arbitrary fragmentation correctness, and style-change controls do not prove a particular native dirty-bit state.

## Isolation and restoration

The driver rejects nonisolated, site-enabled or optimized Python before other imports; bytecode is disabled before helper loading. The helper is imported only after its payload authentication. It is an imported helper, not a separately guarded standalone runner.

All original source/test bytes are captured before mutation. The protected region includes temporary test installation, lint, replacing the 20 prototype files with exact committed bytes, and all four phase builds/tests. Finally attempts every source/test restoration independently, including recreating missing files, before the restoration build. Receipt-write errors are accumulated rather than preventing restoration. Failure to open the rebuild log falls back to inherited output. Final checks compare HEAD, index, all 25 source pins and each test's bytes/presence. Any primary/recovery error, unsuccessful restoration build or state mismatch makes the driver exit nonzero. Abrupt process/OS termination outside Python finally and concurrent external edits remain operational boundaries; no fault-injection execution is claimed.

Only the flex source varies across phases: committed full-key baseline, one-line candidate, original-four-field key, and original key plus the same candidate. Source-only review separately verified the candidate and key projection. This is an exact committed-branch experiment with two key inputs removed in diagnostic phases, not an entire-upstream checkout or runtime.

## Evidence integrity

The helper pins all 20 overwritten files plus five fixed native guards during each test, along with browser/XUL, tests, Ahem and testharness resources. It discovers local HTML link/script/image dependencies recursively and records per-test and ancestor metadata absence or hashes. It is not a complete JavaScript/CSS transitive dependency resolver or hermetic build-system inventory; full installed SDK/build-config inputs are not archived by this driver.

Raw completeness requires WPT exit 0/1, one suite_end, exactly the 15 owned test_end identities, unique test/subtest pairs, only owned test_status IDs, and admitted row/end statuses. The three new test name rosters must match exactly. Existing regression subtest rows are retained but do not have a separate independently enumerated expected name roster. Tests/statuses and source/binary pins are retained before/after. Missing/extra new cases, unexpected harness failures or source changes abort the experiment and invoke restoration.

Numerical failures intentionally do not abort a completed diagnostic phase. In particular, removing key inputs can regress the caption/padding tests in both original-key phases. Compare like-key phases and retain those failures. Completion alone is not all-pass, performance, native acceptance, universal dirty-subtree correctness or a proof of the broader caller/provider contract.

## Recommendation

Run exactly these pins with sole ownership of the shared source/build during the experiment. Inspect baseline/candidate raw differences, calibration failures, all restoration receipts and lint/build outcomes before deciding native acceptance. The accepted narrow direct-frame proof does not substitute for this run or prove the MarkPrincipalChildrenDirty implementation.
