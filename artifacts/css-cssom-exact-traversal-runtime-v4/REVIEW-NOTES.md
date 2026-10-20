# Reversible traversal v4 experiment

Use fresh baseline, candidate and restored-baseline builds, retaining DOMRect
fix 102 throughout. Install only the existing four-case untransformed-edge WPT
and swap the four reviewed traversal files. Restore source/test state in finally
and rebuild after any candidate installation. Preserve unrelated prototypes.

Keep the v3 protocol: 23 files, 74 subtests, six fresh headless processes,
100000 calls per batch, 11 samples and 10000 warmup calls per case. The baseline
must match retained DOM-only results; candidate changes only two expected large
edge failures to passes. The other outcomes, geometry, visibility and checksums
must remain unchanged. Fixed phase order and two processes per phase limit
performance interpretation; no statistical or browser-wide claim follows.

Signing is unavailable. The 229 staged research paths stay untouched. INPUTS
binds HEAD, the staged binary diff and full stage-entry hashes. Staged paths must
be artifacts-only and outside this runtime directory. Git/Mach run with optional
Git locks disabled. Final checks after restored timings join HEAD, stage entries,
staged contents and native pins to the starting state. Index stat-cache bytes
and flags are not covered by that equality claim. Do not sign or otherwise mutate
the index during the experiment. No stash/reset/index restoration is needed.

Run with python3 -I -S -B and no optimization after independent source and driver
review and fresh INPUTS binding. Pause all agent compiler/browser work during
timings. The driver is a local experiment, not native acceptance.
