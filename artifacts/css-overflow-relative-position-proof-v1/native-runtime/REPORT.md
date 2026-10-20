# Relative positioning of overflow continuations: paired native experiment

The exact proposed nsContainerFrame.cpp patch repairs 30 failures in 140 WPT
subtests and preserves 110 prior passes. Initial layout accounts for 16 corrected
failures; updating an initially nonzero inline offset accounts for 14. The test
calibrates a true zero-offset origin, checks geometry after offsets set before
first layout, then nonzero-to-double, return-to-zero, and zero-first updates.
Horizontal and vertical-lr flex/block and vertical-rl block cases are included;
vertical-rl flex is excluded to keep this WPT independent of the final-size fix.

Both candidate and restoration builds passed. The 35 retained regression files
have identical outcomes: 24 PASS, 10 expected FAIL and the separate 336-subtest
final-size WPT with all PASS. The latter fix is installed in both builds. Browser
runs used the shared combined project tree; no isolated upstream runtime is
claimed. All selected source/test/metadata/reference inputs and binary hashes
are retained before and after each run. verify.py checks input stability and
recounts exact subtest transitions. The expected failures are not passes.

Source and build were restored; the temporary new WPT was removed. The existing
final-size flex source/build remains installed. HEAD and staged index are
unchanged. This is positive candidate evidence, not native acceptance: shared
helper caller coverage, relative/normal-position source correspondence,
formatting/lint and broader lifecycle review remain to be completed.
