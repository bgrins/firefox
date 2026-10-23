# Hidden-query repair experiment draft

**DRAFT ONLY: not prepared or executed.** Root must supply the final post-commit HEAD after principal/OOF fixes and ledger signing, review this controller, then separately authorize preparation/execution. No HEAD is guessed or captured by this artifact author.

## Four uninstrumented phases

1. `baseline`: post-commit HEAD, including accepted principal and OOF fixes.
2. `column-provider`: baseline plus the checked immediate table-provider eligibility gate in PresShell.
3. `skipped-line-block`: baseline plus MarkSubtreeDirty on each child of a skipped block line.
4. `both`: the two new candidates together.

Every phase uses the same seven files and exact ordered 66 subtest names. Baseline must exactly reproduce the prior column-runtime both phase's 55 PASS / 11 FAIL status/message tuples and seven OK file ends. Candidate outcomes are retained, including regressions and unchanged failures, without inventing a required all-pass result. Per-phase changes and four-way status transitions are explicit. This is a diagnostic, not automatic native acceptance.

## Source and fixture ownership

The controller preserves the predecessor's 23 native write targets and 28 guards. It saves original working bytes separately from HEAD, resets the 23 write targets to captured HEAD for the experiment, installs only the selected PresShell/block variants, and finally restores every original byte and rebuilds. The other five guards must already equal HEAD. Accepted principal and OOF source bytes are fixed preflight roles, never reverted to the older baseline.

Preparation requires exact retained original PresShell and nsBlockFrame HEAD bytes, principal flex `83c64637…` and OOF absolute `92685802…`. The block candidate is a unique complete ReflowLine replacement in the authenticated retained HEAD full file. Independently regenerating unified diffs yields exactly the supplied column and block patches; no live source is used to construct a candidate.

Five landing WPTs (50 subtests) must be tracked and byte-identical in HEAD, working tree and retained fixtures. They are read and pinned; **never installed, overwritten or unlinked**. Only `hidden-table-column-queries.html` and `hidden-column-independent-trigger.html` (eight cases each) are created exclusively and removed. Preparation and execution reject either diagnostic already existing, including dangling symlinks. Resource, inherited metadata, support/Ahem, Firefox and XUL pins remain in the unchanged WPT runner. All seven fixtures/ordered rosters are byte-identical to the prior experiment.

## Gates and recovery

- Prior column-runtime must be terminal/restored with successful rebuild, no recovery errors and identical BEFORE/FINAL.
- Required `--expected-head` is compared at preparation. Empty index, native pins, tracked tests and exact roster checks precede artifact capture.
- DRAFT and then INPUTS hashes authenticate script/candidate/prepared payloads before imports or writes. Preparation is write-only within this artifact, with read-only Git queries; experiment alone performs the explicitly planned native/test mutations after root authorization.
- Before every build and after tests, HEAD/index, all source guards and resource pins are checked. Raw WPT must complete the exact roster; actual FAIL outcomes are preserved. Build/harness/integrity failure stops phases and enters restoration.
- Finally restores all 23 originals, removes only the two diagnostics actually created, rebuilds whenever native installation started, and records FINAL. Success requires original HEAD/index/native snapshot equality, diagnostics absent, tracked tests/resources unchanged and restore build zero.
- No timing, trace instrumentation, remote browser control, commit or staging operations are included. Runner `run_wpt.py` is byte-identical to the reviewed predecessor; the controller is the smaller derivative documented in the source diffs.

## Commands (root only, after final review/HEAD)

```text
python3 -I -S artifacts/css-hidden-query-repairs-runtime-v1/prepare.py --draft-sha DRAFT_SHA --expected-head ROOT_FINAL_HEAD
python3 -I -S artifacts/css-hidden-query-repairs-runtime-v1/experiment.py --inputs-sha PREPARED_INPUTS_SHA
```

Static checks parsed Python without importing/running preparation or the experiment, authenticated source dependencies, checked exact patch reconstruction and unchanged test identities, and verified the 5 tracked / 2 temporary partition. No browser, compiler, build, Git or live native mutation ran during draft authoring. Review the explicit script diffs before execution. There is no runtime or candidate-correctness claim yet.
