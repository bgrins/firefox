# Clip auto optimized runtime acceptance review

The completed v2 experiment supports bounded local acceptance of the reviewed
three-file guard relocation, after correcting an analysis-only key collision
in this independent review. No browser rerun is needed for that correction:
the complete raw evidence retains the omitted records. The candidate build
succeeded, exactly four intended CSS callbacks improved, all sampled SMIL
behavior was preserved, and the original application and sources were restored.

Native patch SHA256:
`5e85b5ad7ab7279cf2d7a1594cd5bf0aa32fbce495c28d7d65e466837c5040f5`.
Reviewed runtime capsule: `css-clip-auto-runtime-20261110-v2`, with frozen
`RUN-INPUTS.json` SHA256
`1b3d8da29aab6ff3d32646d090488c752e8ad8831ca3c80d146cdc79a17703d7`.
Completed candidate `RESULT.json` SHA256:
`b47e8be83b39565c7132f3580c10269ac11f9f56d30e9d3c4b0281ef2e948ef0`.
`CHECK.json` binds the raw logs and other receipts by hash.

## Results from independent raw-log reduction

| Evidence per variant | Result |
| --- | --- |
| WPT subtests | 48, with exactly four intended FAIL to PASS changes |
| WPT harness endings | Three OK, unchanged |
| Mochitest assertions | 5,061, with 5,002 PASS and 59 expected todo FAIL, unchanged |
| Mochitest harness endings | Four PASS, unchanged |
| Distinct assertions plus harness endings | 5,116, same inventory in both variants |
| Mochitest message/occurrence inventory | All 5,061 unchanged |
| Tagged SVG observations | 12, identical fixed inputs and computed clip strings |

The four improvements are matching-auto iteration composition, effect add,
effect accumulate, and the existing incompatible-clip iteration callback.
The other new numeric, mismatch and top-level-auto controls remain passing.
The existing unrelated expected failures remain unchanged. Each SVG diagnostic
record remains paused; the numeric positive-control WPT passes in both runs.
These 12 records are preservation observations, not additional WPT assertions
or a settled conformance oracle for every mixed-auto SVG case.

`inspect.py` independently reads the completed raw traces, validates lifecycle
pairing and harness endings, counts repeated callbacks, rejects crash records,
compares status inventories, and compares all Mochitest message labels in order.
It does not import the author's analyzer. The candidate's optimized native
build exited zero. Both Mochitest commands exited zero. Both WPT commands
exited one for understood expectation mismatches: baseline has the three new
failures; candidate has the existing clip case's unexpected pass. The full
text summaries agree with the structured results. No test metadata was changed
to hide these outcomes.

## Two distinct harness issues

V1 had an adapter error: it required `OK` for Mochitest harness endings, whose
actual status is `PASS`. V2 changes only that flavor-specific check and its
synthetic controls, preserving the runner and native candidate. V1's browser
results were retained and the transaction restored correctly; its parser
failure was not a native test regression. A fresh v2 baseline was run.

The v2 comparison has a separate bookkeeping defect. Mochitest sends
`subtest: null` for these assertions. `compare()` keys a first assertion as
`(flavor, test, null, 0)` and later uses the identical key for `test_end`.
Consequently its reported 5,112 rows omit four first assertions. The harness
endings remain present; the first callbacks are what get overwritten.

This review includes the record kind in every key. All four actual first
callbacks pass in both variants and have the unchanged message
`should be paused by <svg> load handler`. `controls.py` changes each one to
FAIL in copied parsed data: the frozen analyzer incorrectly accepts each of
the four mutations, while the corrected kind-tagged comparison detects an
additional fifth change and rejects it. `CONTROLS.json` records those four
reproductions and rejections. Frozen v2 inputs were not edited. Future reuse
of that comparator should incorporate this fix and control before execution.
The current review's complete comparison supplies the missing acceptance gate.

The review checker's first attempt used the same untagged key shape and
rejected the predicted total of 5,116; examining that mismatch exposed this
defect. The final successful receipt uses distinct callback/harness tags.

## Source, binary and restoration evidence

The build receipt identifies exactly the three candidate source hashes and
the pinned optimized configuration. Its binary hashes equal the sampled
binary receipt and differ from the retained baseline. The runner checks those
samples again after each test command. Baseline reuses the documented retained
build; it is not represented as a newly rebuilt baseline. This review does not
infer binary correctness from hashes alone.

After terminal `RESULT.json` appeared, this reviewer independently verified
the live restored application: all 9,379 entries' kinds, modes, file hashes and
sizes, and symlink targets match the saved original manifest. The three extra
build/test files, three native source files, three retained binary samples,
61 pinned test/harness files, mozconfig, and temporary fixture/metadata absence
also match. Backups were removed. Both terminal receipts report no error and
verified restoration; every owned command reports its process group absent.
Git HEAD/index preservation was checked by the runner and recorded in its
receipts; this reviewer did not independently repeat those Git checks.
Build intermediates are not claimed to be restored.

Full text and structured logs were inspected. Build output reports success
with 31 compiler warnings outside the changed clip files; detailed suppressed
third-party warnings were not separately audited. Both Mochitest runs warn
about an existing separate `/Applications/Firefox.app` process and disabled
refcount leak logging. The tests explicitly launch the objdir application,
have complete paired lifecycles, and report zero unexpected Mochitest results.
These warnings do not change the scoped result, but no leak-detection coverage
is claimed. `LOG-SCAN.json` retains the relevant text-log records and hashes.

## Acceptance limits

Together with the already reviewed source audit and universal Lean guard
relocation theorem, this optimized native build and focused comparison are
sufficient for bounded local acceptance of this clip fix. No new
assertion-sensitive changed path was identified in the earlier gate
reassessment: the extra component evaluations are scalar operations, and the
existing variant guards remain in place. Debug coverage remains unrun, rather
than silently treated as passing or as a requirement borrowed from the
separate missing-pseudo work.

Direct native count-zero FFI execution remains untested; normal repetition
usually bypasses that call. Count-zero preservation is supported by source
inspection and the abstract proof/model only. The theorem assumes pure total
component computations and does not establish IEEE arithmetic behavior,
generated Rust/C++ refinement, arbitrary animation/SMIL behavior, security,
or whole-browser correctness. The runtime evidence covers the named tests
and controls on this optimized build.

This reviewer ran only local read-only evidence/hash checks and analysis
controls, writing this review capsule. No browser, build, native source,
canonical library, Git index, or commit was changed.
