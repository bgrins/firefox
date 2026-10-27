# Integer offset browser reproduction

The existing working Firefox build reproduces four exact-integral offset errors: both offsetLeft and offsetTop return ±8388610 for separately calibrated base ±8388600 plus margin ±9, whose exact geometry is ±8388609. All16 input/style/parent/DOMRect calibrations and repeat/restored stability checks pass. First, repeat and restored snapshots each have12 matching and4 mismatching integer offsets. Removing the margin on the same DOM recovers all16 matches.

The exact proposal-v3 JavaScript was inlined and a result POST appended; observation generation and validator are unchanged. The native helper independently reproduces the arithmetic defect for supplied app-unit values. This browser run does not log the actual native input, although exact calibrated geometry agrees with the proposed witness.

Session16591 exited0. All source/index/build pins were preserved; the owned browser process group terminated and disposable profile was removed. No native changes, compilation, acceptance or commit occurred. This is the shared project build including previous geometry fixes, not an isolated upstream or release-browser comparison. The WPT proposal asserts integer offsets without requiring DOMRect calibration or earlier fixes.

The browser log retains a headless SWGL framebuffer warning, restricted cpuinfo sysctl messages and channel errors during intentional shutdown. Complete measured geometry and cleanup are retained; no paint or performance conclusion is drawn.

Next: narrow CSSOM integer conversion repair, paired WPT validation, existing observer controls, and standalone dependency check. General fractional rounding policy remains outside this integral-identity claim.
