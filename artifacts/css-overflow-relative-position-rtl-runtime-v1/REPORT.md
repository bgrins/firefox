# Relative overflow positioning: RTL and shared-caller regressions

The extended matrix adds RTL alongside LTR to the proposed standalone WPT and
corrects 60 failures in 280 subtests, preserving 220 passes. All zero-origin
calibrations pass. Thirty-two failures were initial translations and 28 were
updates from a nonzero inline offset. The native patch is unchanged from the
first paired experiment.

Sixty-one existing non-flex CSS Break files selected using Searchfox cover block,
grid and fieldset fragmentation. Their results are identical before and after:
24 PASS, 36 expected FAIL, one OK testharness file with three passing subtests.
Expected failures remain explicit; these tests do not establish coverage of every
caller or branch. No unexpected candidate result occurred.

The input snapshots include complete linked references and metadata. All
non-native/non-binary inputs are identical across the pair; all inputs stay
stable within each run. Candidate and restore builds passed. Source, temporary
WPT removal, HEAD and index restoration were verified. The flex final-size fix
remains installed in both builds. No isolated upstream build is claimed.

This capsule is supplementary regression evidence; the separate native repair
still awaits final review, formatting/lint and packaging. Percentage/auto offsets
and arbitrary skipped/reparented histories are not claimed to be tested here.
