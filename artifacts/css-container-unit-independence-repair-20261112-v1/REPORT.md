# Reject container units in registered initial values

Status: local native repair and focused browser validation passed; three files remain applied. Uncommitted pending signing. The standalone patch contains only the Rust guard, the expanded existing WPT, and its metadata update.

Typed registered initial values must be computationally independent. The length-unit classifier already respects this restriction for font-relative units but omitted it for the six container-relative units. The repair adds the computational-dependence condition while retaining the existing Gecko and page-rule restrictions. Ordinary use of these units remains accepted.

The expanded WPT preserves the six original subtest names and gives every registration a unique property name. This avoids the original test's repeated-name failure contamination. It covers both JavaScript and @property registration, length and length-percentage syntax, direct and calc forms, and positive/negative controls. Metadata removes exactly six expected failures and preserves the existing non-debug x86 crash expectation.

## Validation

- Final candidate WPT on the original binary: 72 failures and 34 passes, retained in `../css-container-unit-independence-probe-20261112-v1/candidate-test-baseline-wptreport.json`.
- Rebuilt browser: 106/106 subtests pass in that WPT.
- Five focused WPT files: 221 subtests pass, all five harness results OK, zero unexpected outcomes. The other files cover JavaScript registration, @property, ordinary container units, and their viewport fallback.
- `mach build binaries -j2` completed successfully in 70.8 seconds. The previously observed resource-monitor `KeyError: 'export'` appears in the retained log; the compiler/link build and subsequent browser run succeeded.
- The three-file standalone patch applies to the preserved HEAD files and reverses byte-for-byte. The owned temporary replay directory was removed.
- Current source bytes, command-log hashes, all WPT results, and the resulting firefox/XUL hashes were independently checked after the runner completed.

The root owner session was 75520, terminal 12a2bc. Independent final validation is recorded by terminal f2a349. `fixed-BINARIES.json` is the new local runtime authority, superseding the grid-trace restored build. No new objdir was created.

## Review and packaging

`INPUTS.json` pins all original and candidate files. `candidate.patch` has SHA-256 `645ff719679a896b670e21e82dab5f6b7ee5ebfb17ce95f84534ab7303d45e0f`. `PATCH-REPLAY.json` records forward and reverse transport. The baseline source/report review is in `../css-container-unit-independence-baseline-root-review-20261112-v1/REVIEW.md`.

Suggested standalone commit subject: `Reject container units in registered property initial values`.

The preceding research commit should contain the baseline, independent review, this validation capsule, and any separately accepted formal classifier artifact. The native commit should contain only the three paths in `INPUTS.json`. No Git signing was attempted or bypassed.

This is one pre-existing conformance defect, already partly covered by expected-failure metadata. It was found during source/spec correspondence work, not by a completed Lean proof. The repair does not establish full classifier refinement or new security guarantees. Cross-platform CI and the retained x86 crash condition were not tested locally; no Try push was made.
