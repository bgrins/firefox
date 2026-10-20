# Reversible traversal v3 experiment

Use fresh baseline, candidate and restored-baseline builds. Keep the committed
DOMRect double-coordinate fix installed in all phases. Temporarily install only
the four-case untransformed-edge WPT; swap only the four reviewed traversal
source files. The driver restores source/test state in finally and rebuilds if
candidate source was installed. Existing unrelated native prototypes stay pinned.

Require baseline outcomes to match retained DOM-only calibration: 23 files and
74 subtests. Candidate must change only the two expected large-edge failures to
passes, preserve small controls and all existing file/subtest outcomes, including
the two unrelated expected failures. Capture DOMRect explicitly for both runs.

The benchmark retains ordinary, leaf-transform and root-transform chains at
depths 8 and 128. Each of six fresh-profile processes uses 100,000 calls per batch,
11 samples and 10,000 warmup calls per case. Check all geometry, checksums, batch
order, visibility and source/binary stability. Runs remain fixed before/candidate/
restored phases; descriptive results do not establish significance or broad
browser performance. No concurrent agent compiler/browser work during timings.

Execution is pending final source/driver review, signed checkpoint and INPUTS
binding to the resulting HEAD. This document records a plan, not a result.
