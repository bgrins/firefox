# Independent final repair receipt review

Accept the frozen local repair evidence for the focused repeated-child-reflow regression. Source/receipt checker bc66a0 exits zero. It authenticates all 77 manifest files, replays the retained verifier, independently matches raw WPT status records with reports, verifies exact command vectors and installation hashes, and applies/reverses the patch against the recorded HEAD in fresh temporary files. No compiler or browser was rerun.

The final test/native hashes are the already reviewed versions: asynchronous promise_test child-only WPT, opt-in flag set only around PresShell's non-root initialization, actual override-branch recognition, and arithmetic-only suppression retaining property/cache/relative-size bookkeeping. No source weakening was introduced during packaging.

## Runtime and build linkage

Baseline-v3 reports harness OK with 28 FAIL and 92 PASS among 120 unique named cases. Fixed reports the same 120 names, all PASS. Raw test_status/test_end records match both reports. The selected three existing reftest outcomes are unchanged: one PASS, two FAIL. The two failing report screenshot pairs match; this review additionally decodes all four embedded raw PNG payloads and verifies byte-identical SHA256s between baseline and fixed. These are preserved preexisting failures, not corrected cases. The fixed mach run exits zero under its configured expectations.

The baseline binary manifests match build-before; build-after matches both fixed before/after manifests. XUL changes across the build. The retained verifier reauthenticates current installed candidate source and binary bytes against those after hashes. Build INSTALL.json contains the exact four candidate source/test identities. Build command is mach build binaries -j2; baseline and fixed commands select the actual local Nightly executable, one headless WPT process, explicit raw/report outputs and the exact four tests.

The build exits zero after about 928 seconds. Its terminal log says the build was successful, while also retaining export-tier monitor KeyErrors and a summary of 21 compiler warnings. This is successful build/runtime evidence, not a warning-free build or proof that the monitor had no defect. The resulting binary is the one pinned for the successful WPT run.

The process helper marks cleanup unsafe before launch, checks owned/current and earlier groups, and retains uncertainty on inspection/signaling errors. The three accepted command records have no such error, no timeout, and record group absence/safe cleanup. This review authenticates those historical records without fresh process inspection. The driver intentionally leaves the successful candidate installed and built; it is not a source-restoration transaction and should not be described as one.

## Independent patch isolation

Fresh application starts from git object 5fcf976eeb79ddc057e9c73d7b73a422058b1903 for the three native paths, not from the current worktree. All before and applied hashes match STANDALONE-HEAD-CHECK.json. Reverse application reproduces every native original and removes the added WPT. Five read/apply commands exit zero, retained in HEAD-COMMANDS.json; only owned temporary files were modified and they were removed afterward. No index, commit, signing or live source change was made.

The standalone HEAD ReflowInput hash differs from the runtime candidate's baseline because the runtime also carries the independently accepted used-margin refresh. The patch roundtrip demonstrates that this four-file delta applies independently; it is not a separate build/test of the pure HEAD-plus-only-this-patch binary. Runtime before/after keeps that other change fixed. The patch contains no unrelated used-margin hunk.

## Preserved exclusions

The first test attempt's promise_setup/test harness error and the extended baseline-v2 parent-font failures remain retained without repair credit. The supplemental parent-refresh probe, including its later-discovered clone-insertion perturbations, is not read or used by this acceptance check. The separate installed Firefox158 priming probe and its cache-path attribution also do not contribute to the 28-correction count.

Targeted lint records zero problems, and the source-review/proof artifacts remain separate. The mathematical feedback model proves specified scalar histories, not native refinement. This receipt acceptance does not close theme/SVG-specific runtime coverage, every parent reset route, baseline measurement-cache behavior, signed32 padding overflow or the larger exact geometry migration. No universal browser correctness or security conclusion is claimed.
