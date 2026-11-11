# Snapshot runtime preparation review

Ready for the parent-owned reversible baseline/candidate experiment. No blocking
finding in the frozen preparation inputs, comparator, or restoration workflow.
This is readiness for an optimized prerequisite-preservation run, not acceptance
of the native refactor or a missing-pseudo fix.

Reviewed capsule: `css-pseudo-animation-snapshot-runtime-20261110-v1`.
Frozen `RUN-INPUTS.json` SHA256:
`1eee630c4c76f63f09efb454bbf6fa84bca20103e7c822ac968d293db7352c23`.
Execution HEAD: `f3949d2992abdc02536b9a61e51dc7d603ce0868`.
Native patch remains the source-reviewed two-file snapshot extraction,
SHA256 `b37e4885614c5b2acb7fa4320ca734fd2c7fa1062e12f5b55c6e60be71d25166`.

## Independent preparation checks

The reviewer ran the frozen preparation checker without `--check-live`: all
19 inputs authenticated and all 20 negative controls passed. A separate
review-owned checker authenticated helper origins, the exact native patch and
both copied native files, immutable Git source/metadata objects, directly
included scripts for all eleven pages, and the retained-build receipt chain.
`preparation-check.json` and `CHECK.json` record these checks.

No live binary, fixture-absence, or working-tree-cleanliness check was run by
this reviewer, avoiding races with root's subsequently started transaction.
Root owns those preflight and terminal checks. This reviewer launched no native
build or browser test and changed no frozen input, source, Git index or commit.

## Test, metadata and preference coverage

The eleven explicit pages are the ten-page source plan plus the committed
12-case keyframe attribute-mutation test. The original 20- and nine-case pseudo
fixtures are byte-identical to the earlier composition-extraction inputs and
are the only temporary pages. Existing pages exercise target/null-target
behavior, CSS `getKeyframes`, JS `setKeyframes` generation opt-out, effect
replacement, and four named-range/implicit-endpoint paths. The added attribute
test targets the locally added `aReferencesAttributes` forwarding path.

All 34 page/script and metadata-presence entries match their immutable execution
HEAD objects, including absent per-page metadata and ancestor metadata. Every
direct `<script src>` in the eleven pages resolves to a pinned file, and no page
declares additional URL variants. This is a bounded direct-script inventory,
not proof of every dynamically loaded harness dependency.

Pinned ancestor metadata enables properties-and-values and scroll-driven
animations for CSS animation pages; scroll pages additionally enable Typed OM.
The web-animation ancestor enables all three. Existing per-page expected
failures remain in place. The clean pinned checkout and normal WPT preference
setup supply the rest of the environment; this wrapper adds no speculative
feature-pref override.

The baseline is fresh and does not inherit older total-count or status tables.
Known failures may remain, so baseline review must confirm the intended CSS
generation and attribute assertions actually ran and distinguish supported
passing controls from retained missing-pseudo failures. The parser enforces
exact 20/9 fixture names, 24 target assertions, and all 12 attribute names;
the other seven pages require complete lifecycles and at least one assertion,
then candidate comparison requires their exact observed baseline inventory.

## Strict comparison and lifecycle handling

Parser keys and comparison keys retain assertion/harness record kinds, so a
null-named assertion cannot overwrite or be overwritten by `test_end`. Duplicate
callbacks, harness endings, parsed comparison keys and JSON object keys are
rejected. Missing/extra result identities necessarily produce a difference
because accepted statuses cannot be null. A synthetic null-name regression
reproduces the old untyped-key collision and proves the current comparison
rejects it.

The parser requires one ordered suite lifecycle, exact expected page identity,
paired starts/ends, and OK harness endings. Callbacks must be PASS or FAIL;
timeouts and not-run statuses are rejected. Crashes, structured ERROR/CRITICAL
logs and out-of-range native assertion counts reject the run. Both WPT command
exit zero and exit one still require successful parsing and comparison; neither
exit alone certifies preservation.

The comparison gate is exact status and identity preservation, including known
failures. It is not a comparison of computed values hidden inside failing
assertions. Messages/expected fields remain available in the raw and parsed
logs but are not equality-gated. Full text logs still need review for diagnostics
not represented by structured failure events. The preparation controls cover
these intended parser boundaries without claiming browser execution.

## Retained build and reversible execution

The baseline is the retained optimized clip-fix-171 build, BuildID
`20261110165601`. Its receipt records build HEAD `713bb6d3`, repair commit
`7382007a`, and the final repair's source/config/binary hashes. The copied receipt
matches its pinned original, its recorded repaired source bytes match execution
HEAD, and no tracked production paths changed between repair commit and
execution HEAD. This establishes the documented source linkage without
misrepresenting baseline as a build at the later execution HEAD. Root separately
checks the three live sampled binaries before execution.

Candidate requires a successful, restored baseline with the same frozen-input
digest and retained binary identity. It installs only the two copied native
files and runs a real `mach build binaries -j6`. Test commands use the explicit
objdir application, one WPT process, headless execution and full text/JSON logs.
Source/config/binary identities are recorded and sampled binaries are checked
again after testing.

The full-application and process-group helpers are byte-identical to their
reviewed composition-extraction origins. Before mutation the runner backs up
all application files, modes and symlinks plus the gtest XUL, application.ini
and wptrunner.local.ini extras, and records the index fingerprint. Owned process
groups must become quiescent before restoration. Source and fixture restoration
checks their installed bytes to avoid silently overwriting detected concurrent
edits. Full app/extras are restored and verified; owned fixtures and backups
are removed only under the documented successful checks. Failed verification
retains backups and emits a distinct restoration failure.

No concurrent native build, browser test, relevant file edit or Git mutation is
an operational precondition supplied by root. The capsule's lock does not
implement a machine-wide build lock or prove the absence of all external
mutators. Whole-app restoration cannot attribute every hypothetical concurrent
app write to its owner. Build intermediates are not rolled back. The reviewed
workflow is appropriate under the explicitly coordinated exclusive transaction.

## Remaining CSSOM and ownership limits

The source ownership addendum correctly identifies a real aliasing distinction:
the old const pseudo-request reference points into the live target, while the
new one points into the snapshot. The copied request intentionally stays paired
with its captured element under hypothetical retargeting. This is not a proof
of observational equivalence under arbitrary reentry or a deeply immutable
effect snapshot. The current run exercises ordinary synchronous preparation.

The extraction captures completed CSS frames, does not refresh range timing,
and adds no missing-pseudo CSSOM hook. Fresh provider/base context, range
regeneration, cascade masks, lazy-recursion/revalidation and final debug coverage
remain separate gates. This optimized preservation experiment does not waive
the missing-pseudo debug requirement and counts no new Firefox bugfix.
