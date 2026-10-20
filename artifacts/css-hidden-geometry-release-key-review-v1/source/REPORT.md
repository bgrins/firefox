# Release-only original measurement-key probe

**Prepared, not browser-executed.** This is a discriminating follow-up to the hidden clean-item measurement hypothesis, not a confirmed release bug or attribution to a particular cache field.

## Fixture and oracle

The flex subject and its host stay 100×64 with zero border/padding on the items. A 100px item uses `flex: 0 1 auto; min-width: 0`. A second equal item is appended or prepended while the subject is hidden. Two equal shrink factors and bases divide the 100px negative free space equally: each item becomes 50px wide, with unchanged 32px height. These are exact small integer dimensions. [Flexbox flexible-length resolution, current ED inspected 2026-10-20](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths).

The matrix has 48 configurations: direct item or clean 100%-width nested descendant; append/prepend; shrink/no-shrink/zero-width sibling; visible/hidden; bounding rectangle/offset dimensions. Every configuration has five ordered phases: warm visible, apply visibility, insert, remove, show. Each phase first reads the **outer subject's** client-rect count and scroll dimensions, then queries the target three times without intervening DOM mutations. A separately constructed visible fixture provides the same final arrangement, checked against the independently specified 100→50→100 arithmetic. The measured target itself is never resized by a direct style mutation.

The 240 stage records preserve all three reads, the visible reference, the fixed arithmetic expectation, and the outer flush results. No-shrink and zero-width-sibling controls preserve 100px. Hidden versus visible controls distinguish ordinary resizing. Nested/prepend cases query a clean descendant after its flex ancestor's size changes. Warm/remove/show phases expose initial calibration and recovery. The protocol deliberately begins visible to populate a prior measurement and clean frames; it does not claim coverage of initially-hidden construction.

The hidden measurements are retained as comparisons, not made into a hardcoded runner-success condition. Existing source reasoning points to skipped layout plus a clean target bypassing forced-layout recovery. Whether the original key actually misses, which frame is dirty, and which callback writes its size require source instrumentation if this fixture produces a difference. A negative result does not disprove the separate containing-block-key regression hypothesis. Current containment handling is complex; this probe does not derive all forced-hidden-layout requirements from the visible sizing rule. [CSS Containment content visibility](https://drafts.csswg.org/css-contain-2/#content-visibility).

## Source link and independence

`ORIGINAL-KEY.txt` retains the complete indexed `CachedBAxisMeasurement` class: its key uses computed size, computed minimum/maximum block size and available block size. `SOURCE-ROLE.json` pins the complete retained source and extraction. This is source discovery evidence, not proof that the installed release executable corresponds byte-for-byte to that indexed revision.

The proposed mechanism is an original-field change: shrink changes the item's computed inline size from 100 to 50 even without the locally added containing-block or border-padding fields. Parent dimensions and item border/padding are fixed. The runtime uses only installed release 158, pinned to the binaries used by the successful earlier release probe. There is no dependency on the current project binary, live native source, pending HEAD isolation build, or our added key fields.

## Runner safeguards

`run_browser.py` adapts the known successful LaunchServices route (`open -W -n -g -a /Applications/Firefox.app --args -headless -no-remote -profile ...`). It requires isolated/no-site/nonoptimized Python before importing nonbuiltins, an externally supplied FILES hash, and an absent absolute output directory outside this capsule. It authenticates all listed source payloads and both release binary pins before launch, then hashes them again afterward.

Only localhost is served. The profile is newly created under the explicit output directory. Cleanup identifies browser parent processes by exact binary path plus that full profile argument; it rechecks ownership before signaling. It does not kill a user's unrelated Firefox. Launcher and server cleanup are separate; if owned-process cleanup fails, the profile is retained and the run fails. Process kill, machine failure, or PID reuse between inspection and signal remain OS-level limitations. No global browser preference or main source/index/build change is requested.

The validator reconstructs all 48 keys and all five phases; malformed, duplicate, omitted or nonfinite data fails. Visible-reference calibration failures block interpretation. Hidden geometry differences and repeated-query changes are diagnostic outputs, never silently converted to success or ignored.

Python AST parsing and seven pure validator checks pass (`STATIC-CHECKS.json`). The fixture JavaScript and LaunchServices runner have **not** been executed for this new artifact. No browser/build/native/Git mutation was performed while preparing it.

## Root-owned invocation, after authorization

```sh
python3 -I -S artifacts/css-hidden-geometry-release-key-probe-v1/run_browser.py EXTERNAL_FILES_SHA256 /Users/bgrins/code/firefox/artifacts/css-hidden-geometry-release-key-runtime-v1
```

The output directory must not exist. Preserve `RESULT.json`, `SUMMARY.json` and browser log. A complete 48/240 result with visible calibration passing is the evidence gate; the number and exact phases of discrepancies determine the next source investigation. There is no claimed result yet.
