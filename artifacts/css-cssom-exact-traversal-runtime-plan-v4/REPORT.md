# Traversal v4 runtime preparation review

**GO for the bounded reversible experiment after fresh INPUTS pins these reviewed scripts, source roles, HEAD and staged state. Signing need not block it.** This is driver/source review, not a runtime or native acceptance. INPUTS was not yet present at this checkpoint.

## Preserve the staged research

The inspected index contains 229 staged paths, all under artifacts, with none under the v4 runtime output directory. STAGED-STATE records the path list, HEAD, binary cached-diff hash and full `ls-files --stage -z` hash. The current driver does not run add, commit, stash, reset, checkout or an index-restoration command. Native writes are confined to the four explicitly pinned source files and one temporary WPT, which are restored from pre-run bytes/absence.

The updated v4 driver now:

- Requires INPUTS to match HEAD, cached binary diff and full stage-entry hashes before mutation.
- Requires every staged path to be artifacts-only and outside its output directory.
- Inherits `GIT_OPTIONAL_LOCKS=0` in both its Git helper and all Mach/browser subprocesses.
- Records both index hashes in BEFORE, compares the complete diff and stage-entry byte streams during restoration, then obtains fresh final hashes after the two restored timing processes.
- Writes FINAL with HEAD, both index hashes, original/fixed source hashes and temporary-test absence before marking STATE terminal. Both analyzers join those values to BEFORE and INPUTS.

These checks preserve exact staged entries, content object IDs, modes and stages. They do **not** prove byte-identical physical index storage, stat cache, assume-unchanged or skip-worktree flags. No task here depends on changing those flags. Avoid describing this as a raw-index-byte restoration guarantee. If that stronger requirement is later imposed, add explicit raw-index/flag observations rather than copying an old index over a potentially changed one. The current staged commit contents do not require a successful signature to remain protected.

The no-concurrent-HEAD/index/native-writer agreement is part of this experiment's execution contract. Keep the signer paused throughout it. Do not add a stash/reset workaround. Git path parsing in the driver is line based; the captured current staged roster contains ordinary path names, so arbitrary newline/quoting support is not claimed.

## Minimal changes reviewed

Compared with sealed v3, experiment.py changes only the proposal location, explicit staged-state admission/checks, inherited optional-lock setting, added BEFORE index-entry hash and FINAL checks. Both analyzers change proposal location and enforce the new before/final/input joins. run_browser.py, benchmark, capture, probe, WPT and TESTS bytes are unchanged. REVIEWED-DIFF retains the exact Python delta; eight old/new Python script snapshots parse successfully without executing them.

Use `python3 -I -S -B experiment.py`, and the same isolated, nonoptimized invocation for analyzers. Their assertions are operational gates; do not use `-O` or drop isolation. run_browser.py checks this itself. The main driver/analyzers rely on the launch contract.

The source roster remains the four traversal files; proposal-v4/capsule contains all four original and candidate snapshots. DOMRect remains a fixed input, captured by WPT and timing and included in final restoration checks. This is still the shared build including the earlier DOMRect fix, not a standalone upstream test.

## Keep the existing comparisons

Preserve the 23-file, 74-subtest WPT roster, exact retained DOM-only baseline comparison, four new-test outcomes and unchanged-other-outcome checks. Baseline exit 1 is intentional when the two precision assertions fail; the driver correctly compares complete keyed outcomes instead of requiring a zero baseline exit. Candidate must retain the two expected failures elsewhere and fix the two large precision cases. Do not count four new tests as four newly fixed failures.

Preserve all six topologies, two processes per phase, 11 rotating 100,000-call batches, 10,000-call warmup, three-second startup, visibility/geometry/checksum checks and contemporaneous source/binary pins. V3's ordinary path improved while transformed costs remained mixed and unresolved. V4 should be assessed against its own surrounding baselines; v3 is historical context, not a newly paired sample. Keep per-process distributions and transformed cases separate from ordinary gains. No larger suite or changed batch policy is needed for this comparison.

## Retained-analysis dependency check

Fresh INPUTS must pin the reviewed v4 scripts/test inputs and full intended source/proposal/review dependencies, not merely copy v3's 700-pin record. `analyze.py` intentionally requires live restored inputs. `analyze-retained.py` reads non-artifact inputs from captured baseline inputs, verifies all baseline/candidate input snapshots and uses captured phase source bytes; artifact-prefixed INPUTS still resolve to sibling artifact paths. Its PROPOSAL variable is currently unused for phase source selection. Keep those immutable dependencies available and authenticated, or copy/rebase them explicitly before claiming a self-contained relocated replay.

The final checker should retain the established independent reconstruction of raw WPT rows and timing batches; neither unchanged CONFIG nor a STATE success flag substitutes for it. Retain FINAL in the frozen roster. Historical binaries are supported by contemporaneous hashes, not archived or rebuilt by analysis.

## Restoration limits

The normal and Python-exception paths restore saved source bytes and remove the temporary test in finally; candidate mutation sets changed before the first write, causing a restoration build after partial installation. The added FINAL check extends preservation through restored timing. No driver can guarantee cleanup after SIGKILL, machine loss or an unrelated process concurrently replacing source files. Under the existing serialized execution contract, no additional source/index restoration mechanism is needed for the staged research commit.

The sealed v3 manifest and all 217 payloads were authenticated before review. No build, browser, native-file edit or Git/index write was performed for this plan.
