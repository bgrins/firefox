# Standalone overflow candidate: focused regression gate

The paired run covers34 existing flex fragmentation tests and the336-observation candidate WPT. All35 files finish in both runs. Existing results are identical:24 PASS and10 FAIL. The ten failures are retained expected failures in this checkout; they are not reported as passing. They include container/column fragmentation cases. Candidate mach wpt exits0 with no unexpected results; baseline exits1 due to the new WPT's112 failing observations.

The candidate WPT passes336/336;224 prior passes are preserved and112 failures corrected. Test inputs, linked references/scripts and metadata pins are identical across the two runs. Native and browser pins remain stable within each run. Complete raw logs and retained input snapshots distinguish this paired regression result from a claim that all existing fragmentation behavior conforms.

The selection covers overflow children with borders, floats, relative/absolute positioning, vertical writing modes, fragmentainer resize and eight crash regressions. It does not prove every helper branch executes. Separate branch diagnostics and source review remain necessary. Both candidate and restoration builds exit0 with zero compiler warnings; known mach monitor exceptions remain in logs. Source/build, HEAD and the staged binary diff are restored, and the temporary WPT is removed.

No native acceptance is claimed by this gate. Formal/source ordering review, offset/child-mode coverage and final formatting/lint remain outstanding. The patch changes only overflow reflow timing/final-size input; exact cumulative arithmetic is not included.
