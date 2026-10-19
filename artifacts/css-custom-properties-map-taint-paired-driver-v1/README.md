# Paired taint diagnostic and regression driver

This is a root-executed proposal. The worker has performed only source preparation, Python AST checks, identity extraction and read-only replay of retained raw logs. No build, browser or live source change was performed by the worker.

## Execution

Start with the exact original native files (the completed count+iterator repairs, without the two taint edits). All nine WPT files must already be installed with the retained bytes. The original binary must match the frozen routing `BUILD-ASSOCIATION.json` and enumeration `BUILD-MATRIX.json`; every retained source/binary/prior-test association pin is checked. Root must first ensure no other browser/build job owns the shared outputs.

```sh
python3 -I -S artifacts/css-custom-properties-map-taint-paired-driver-v1/run.py --repo /Users/bgrins/code/firefox --output /ABSOLUTE/NEW/PAIR-DIRECTORY
```

When root executes this driver, it:

1. Authenticates all package inputs and the existing build association, requiring exact original sources and existing binaries. It does **not** rebuild the baseline.
2. Runs all 82 subtests on that baseline, retaining complete raw and console logs. The new nine outcomes must match the prior four-FAIL/five-PASS baseline; the 41 enumeration controls must pass. Existing attr-security results are retained for exact paired comparison.
3. Writes the two exact candidate snapshots, runs `mach build binaries` once, checks native/protected inputs before and after, and requires XUL's hash to change. All build output, including warnings or monitor exceptions, is retained; exit 0 is not described as warning-free.
4. Runs the same 82 subtests and checks all nine target cases pass and all 73 existing control outcomes remain unchanged. It requires exact subtest identities, nine harness OK identities and suite completion. No ordering between test files is assumed.
5. Retains candidate sources after success. On failure after mutation, it only restores known original/candidate bytes to the candidate; unexpected external edits are never overwritten. A failed build/test does not claim the binary matches restored source. A failure before mutation leaves originals untouched.

The driver makes no Git/index changes; its Git commands only record HEAD and current tracked dirty paths. Native mutation and build occur only when root deliberately executes `run.py`. It never installs tests, formats code, kills processes or deletes prior evidence. A new output directory is mandatory.

## Exact set and oracle boundaries

- 9 `map-taint-equality.html` cases: literal image-set and parent/child value/taint prerequisites execute before the final assertion; no hidden skip.
- 32 existing `attr-security.html` cases: retained identities come from actual JS registration. Its 29 `test_attr` cases condition assertions on feature support; three helper cases are unconditional. This existing limitation is not relabeled as full feature coverage.
- 41 final enumeration/defaulting controls across seven files: identities and PASS observations come from the retained combined raw run.

Total: **82 subtests plus nine harness results**. `EXPECTED.json` records exact names keyed by test path. The driver explicitly enables the known properties-and-values preference. There is no invented attr preference. Directory/file metadata and testharness resources are pinned at execution.

The retained original nine-case receipt is unchanged. Complete original/candidate sources and exact `native.patch` are included. Candidate map SHA is `58c66ad3893b79282538386480db8ea6475b49e6744f4d74ffdf3b68ae8d9d86`; candidate cascade SHA is `714f7d9a36d25206fb1721a9c3eafef32ad55cfd8b1be82be7d4ff04ea733d55`. If formatting changes these bytes, use a new versioned package or separately reviewed binding; do not silently alter this seal.

This driver establishes local phase receipts, not an isolated upstream build, release-browser result, universal proof, or final native acceptance. Root and the independent reviewer must inspect build/source association and raw result messages.
