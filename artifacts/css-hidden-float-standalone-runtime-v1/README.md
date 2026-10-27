# Standalone float comparison

Root reviewed and enabled this local comparison after independent controller review and successful build-free cost calibration. No preparation or execution occurred at enablement. The readiness receipt preserves the disabled draft; execution state is recorded separately.

Both phases normalize the same 24 sources to saved HEAD `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`. Baseline uses those exact HEAD bodies. Candidate changes only `nsBlockFrame.cpp` to float-only body `0ac7d9decf238af84cc22441ab2e42b0993a9f422f8f362b84a68ea9adb421fd`. The accepted block-line loop is absent; column and Grid sources also retain HEAD bodies. Five additional HEAD-identical sources complete the 29 guards.

Preparation snapshots all 24 original working bodies, including accepted overlays and older prototypes. It checks their 29-body pins, full native diff, HEAD, and index against the completed float comparison and projected MathML final snapshot. Both earlier campaigns must be terminal and restored. Initial binaries must match the MathML diagnostic's authenticated restored build. Each WPT run records and checks its actual binaries before and after testing. Restoration rebuilds original sources; it does not promise byte-identical rebuilt binaries.

## Test and resource transfer

Only the two final WPT files from `css-hidden-float-landing-proposal-v2` are installed, linted, and executed: eight direct/inline-nested query cases and four visible push controls. These exact cleaned bytes have not run yet. Baseline predicts eight PASS and four exact change-stage hidden-query failures; candidate predicts twelve PASS. These are predictions transferred from the earlier comparison, not observed outcomes without accepted overlays. Raw rows, messages, changes, and discrepancies are retained. Unexpected outcomes stop the comparison and trigger restoration; expectations are not relaxed.

Nine existing WPTs remain read-only guards: five tracked and four accepted untracked. They are not executed because some require the deliberately absent repairs. `tests` retains the eleven-file resource inventory; `run_tests` selects the two owned files. All 30 historical test/support/metadata pins are retained with exactly two approved HTML replacements. Missing metadata remains absent. Resources and read-only ownership are checked across phases. Only the two owned files are removed. The MathML temporary test and other historical temporary files must remain absent.

## Cost and restoration

After each successful WPT phase, one invocation of sealed `css-hidden-float-cost-v1` runs before any source change or rebuild. It passes all 29 guards and the current Firefox binary to the existing runner, using a new phase-specific output directory. Actual before/after receipts must equal the preceding WPT's 29 sources and both binary hashes, plus the six sealed fixture execution inputs. The controller requires terminal cleanup, no live process group, removed profile, no cleanup errors, and the exact 60 rows, 148 progress receipts, and 1,968,000 timed reads.

Both phases require no clean-query or visible-recovery mismatches. Candidate additionally requires no hidden-recovery mismatches. Baseline hidden mismatches remain measured classifications, not equivalent work for timing comparisons. Raw results and summary hashes are saved before outcome gates. A failed cost run stops the campaign and restores sources. No compiler, Lean, build, other browser, or competing measurement should run during either cost phase. These bounded observations cannot establish a general performance guarantee.

`run_wpt.py` and the complete exception/restoration tail are byte-identical to the completed 95-case comparison. The three `.diff` files expose controller changes. The exact 925 staged research paths, full index entries, cached diff, and every staged blob remain bound to the existing boundary evidence. The controller never writes Git data. Source, index, signer, and build writers must remain stopped throughout execution.

After any normalization attempt, cleanup restores each original independently, removes only owned temporary tests, and rebuilds originals. Success requires restoration-build exit zero, no recovery errors, exact final source/native-diff/HEAD/index identity, unchanged resources, and temporary-file absence. Native pushed/overflow/continuation behavior and dirty-root/clean-leaf histories remain outside this comparison. Visible push placement does not prove native pushed-list membership. The run does not automatically accept a repair.

After root enablement and resealing:

```
python3 -I -S -B artifacts/css-hidden-float-standalone-runtime-v1/prepare.py --draft-sha REVIEWED_ENABLED_DRAFT --expected-head 90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e
python3 -I -S -B artifacts/css-hidden-float-standalone-runtime-v1/experiment.py --inputs-sha PREPARED_INPUTS
```
