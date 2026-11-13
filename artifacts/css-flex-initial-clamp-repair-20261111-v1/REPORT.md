# Initial flex clamp diagnostic repair

Local validation passed. The source repair preserves early `Freeze()` timing and delays only inflexible clamp classification until automatic base/minimum resolution completes, using the final item fields. This fixes privileged clamp metadata; the baseline rendered sizes were already correct. Root independent acceptance remains pending.

## Exact final change

The final deliverable is **standalone-expanded.patch**, containing exactly:

- `layout/generic/nsFlexContainerFrame.cpp`: relocate clamp classification after `ResolveAutoFlexBasisAndMinSize`; compare final item base/min/max.
- `dom/flex/test/chrome/test_flex_item_initial_clamp.html`:48 cases /144 assertions.
- `dom/flex/test/chrome.toml`:one additive test registration.

Native before SHA256 is `210a38a494eba5ebc666ad6409c4b4f5b6651668c8bc6f9ef5b02834d578e733`; after is `f1df613c89d38ca0d7f7dbe9d18e71da2908dd5ffdb79882cfbc1987e9f29d06`. BEFORE/AFTER snapshots preserve the initial reviewed version. AFTER-EXPANDED and expanded/ preserve the final requested tests; no prior baseline or snapshot was overwritten. Scoped formatting changed zero bytes. Existing seven chrome tests and the native header/DOM file remain byte-identical to PROTECTED.json, preserving earlier pending changes.

## Validation

| Actual run | Assertions | Result |
|---|---:|---|
| Original final-test baseline, old binary |108|6 FAIL /102 PASS|
| Expanded baseline, same old binary |144|15 FAIL /129 PASS|
| Focused regression, rebuilt binary |144|144 PASS|
| Complete dom/flex chrome suite, rebuilt binary |682 across8 files|682 PASS; all8 file outcomes PASS|

The added controls preserve all original36 case expectations and add automatic minimum with explicit10px base, equal bounds, conflicting min/max normalization, and base equal to both bounds in row/column/column-reverse. The expanded old-binary failures include all three minimum-only auto cases, proving the bug is not limited to stale unconstrained bases. Genuine min/max clamps, explicit/flexible, no-max, aspect-ratio and equality controls are retained. All used-size and base-size baseline assertions pass.

The existing objdir's `mach build binaries -j2` child exited0 in45.65s with0 compiler warnings. Full log includes nonfatal mach progress-display `KeyError('export')` callbacks and the successful build completion; they were not removed or called compiler failures. Executable/XUL identities are pinned before/after every build/test; both baselines use the same old binaries and both repaired tests use the exact new binaries. Native source/test pins were checked before and after each command. Scoped clang-format/ESLint/Stylelint commands exited0 with0 errors/warnings/fixes, and exact hashes confirm no formatting changes.

`validate.py` parses the full raw logs, exact failing labels,144 before/after assertion correspondence, all8 selected test files, binary continuity, protected source hashes, final lifecycle evidence and patch roundtrips. RESULT records PASS_LOCAL_VALIDATION, not root acceptance.

## Why chrome and why preserve freeze timing

FlexItemValues is `[ChromeOnly, Exposed=Window]`. An ordinary WPT cannot inspect `clampState`, and a rendered-size WPT would miss this defect. The new test follows the existing dom/flex chrome API usage. No WebIDL/API surface changed.

Automatic content measurement uses `IsFrozen()` to select forceBResize behavior. Moving Freeze would broaden the layout change; this repair leaves it untouched. The normal constructor starts unfrozen, the inflexible branch freezes and clears flags, and automatic base/minimum resolution does not classify them. The final classification therefore sees resolved values with fresh flags. Flexible items retain their existing resolver path. No assignment to rendered/base sizes was added.

## Lifecycle evidence and limitations

TERMINALS lists actual owner handles/chunks and child exits. The initial baseline owner exited1 for the expected failed assertions. Subsequent wrappers also returned1 because the immediate process-group drain/inspection gate failed even when their children succeeded. Original COMMANDS records remain unchanged. Separate ps plus killpg inspections confirmed exact owned groups absent before subsequent stages; FINAL-ABSENCE freshly confirms all seven absent. This distinction is retained rather than relabeling wrapper outcomes.

No native binary proof, whole Flexbox refinement, browser cross-engine comparison, or correction to the accepted Lean target is claimed. The prior theorem preserves initially frozen metadata supplied by its producer; this repairs that producer's diagnostic meaning. Parent's pending sources/proofs/fix/test artifacts were not overwritten. No commit, signing, Try, or shared tool update was attempted.

## Patch transport and cleanup

Final eight isolated apply/check/reverse commands passed against both the exact dirty preimage and HEAD5fcf976eeb79ddc057e9c73d7b73a422058b1903. Exact before/after and reverse identities were checked; owned temporary patch directories were removed. The intentional three-path repair remains in the working tree for root acceptance. Existing native build products are retained for this tested binary; they were not treated as disposable scratch. The earlier temporary diagnostic probe and its registration were removed in the separately frozen probe capsule.

No repaired test needs rerunning because formatting changed nothing. Root can replay `python3 -I -B artifacts/css-flex-initial-clamp-repair-20261111-v1/validate.py` to independently verify the retained evidence without launching a browser/build.
