# Reproduced initial flex clamp diagnostic mismatch

The existing local Firefox build reports the wrong privileged `clampState` for measured, inflexible column items. One headless chrome run completed 36 cases / 72 assertions: **6 FAIL, 66 PASS**. All 36 used-size assertions passed. This is a diagnostic metadata defect; the experiment does not show an incorrect rendered size.

For a 20px content base with `flex:0 0 auto; min-height:0; max-height:100px`, column and column-reverse report `clamped_to_max` although base and used size are both 20px. Setting min-height:30px produces correct used size 30px but still reports max-clamped rather than min-clamped. A 20px maximum (equal to the base) also incorrectly reports max-clamped. The corresponding row cases, explicit 20px basis, flexible auto-basis, genuine maximum clamp, no maximum, and three aspect-ratio cases all pass. The aspect-ratio route was investigated and did not fail in this matrix.

## Reproduction and provenance

The exact probe is `test_flex_initial_clamp_probe.html`; `CASES.json` supplies its 36 expectations. `COMMAND.json`, full `baseline.log`, and structured `raw.log` preserve the actual single-file headless mochitest invocation against `objdir-full.noindex`. Runtime app identity is Firefox 160.0a1, appBuildID **20261111194312**, platformBuildID **20261111185634**. The copied generated `application.ini` contains a different BuildID and is not substituted for the observed runtime identity. `BINARY-IDENTITY.json` records post-run executable/XUL hashes, explicitly not before/after binary provenance.

No feature preferences were overridden by this probe; the normal chrome harness profile was used. The log records non-e10s and fission disabled. This is the local development build with existing root patches, not a release-channel or cross-browser observation. The current source pins include the finite-weight cpp SHA `210a38a494eba5ebc666ad6409c4b4f5b6651668c8bc6f9ef5b02834d578e733`.

## Source and specification rationale

The frozen audit `../css-flex-current-native-join-audit-20261111-v1` retains the exact source chain and independent proof-version comparison. `GenerateFlexItemForChild` classifies an inflexible item from its earlier local base before `ResolveAutoFlexBasisAndMinSize` measures an unconstrained block-axis base. `SetFlexBaseSizeAndMainSize` then updates base/current without replacing those clamp flags. `UpdateFlexLineAndItemInfo` exposes the stale flags. Runtime base=20, delta=0 and the control pattern match this path; no instrumented native trace was run.

[Flexbox §9.7](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths) assigns inflexible items their hypothetical main size. Base 20 bounded by [0,100] requires no clamp; bounds [30,100] increase it to 30. Gecko's existing chrome clamp test uses `unclamped`, `clamped_to_min` and `clamped_to_max` with those meanings. `clampState` itself is a privileged Gecko diagnostic interface, not a standardized web observable. Consequently this is not labeled a WPT/spec layout failure.

## Repair direction for review

Preserve the early `Freeze()` timing: measuring-reflow behavior consults frozen state. Defer the inflexible clamp classification until after all automatic basis/minimum resolution, and compare the final item's base/min/max, not earlier local variables. Check that this also preserves genuinely clamped and aspect-ratio cases. No C++ repair was made here. The accepted caller proof preserves supplied initially frozen flags and does not establish their acquisition meaning, so this defect does not falsify its theorem.

## Lifecycle and restoration

Actual owner session 51678 terminated exit 1 (`6eca79`). The mach child also exited 1 for the six assertion failures; the browser itself exited normally. The reused bounded wrapper additionally hit PermissionError in final group inspection, so it correctly retained the temporary source/registration. This wrapper failure remains in `COMMANDS.json` and `RESTORE-PENDING.json`.

A separate escalated `/bin/ps` and `killpg(22968,0)` inspection (`57810a`) proved the group absent. Only then were the exact original chrome.toml bytes restored and the owned probe source removed (`b3070c`). All 11 protected original source/test hashes still match, including preexisting dirty tests. The owned installed probe symlink was removed; shared installed manifest symlink and other tests were preserved. `RESTORED.json` and `INSTALL-CLEANUP.json` record these actions. No native build/edit, commit, signing, Try submission, or user browser tab change occurred.

`analyze.py` independently parses all actual rows/assertions and authenticates restoration. The original audit remains frozen; this successor adds the actual reproduction. Root review/repair ownership remains separate.
