# Loaded FontFace baseline

The local baseline binary was rebuilt successfully before running the exact v2 tests. All retained receipt, raw output, snapshot and build hashes authenticate. The matrix completed all 68 subtests with 30 PASS, 38 FAIL and three OK harnesses. No candidate native sources were installed.

The regression run completed all eight harnesses. Eighteen subtests pass and one fails; four reftest/crashtest harnesses pass, one fails, and three testharness harnesses are OK. Existing failures are `Font matching uses updated style and family name` in `fontface-descriptor-updates-2.html`, and `fontface-override-descriptors.html` (800 differing pixels). These are baseline observations; the candidate comparison must retain their exact outcomes and identify any improvements or regressions.

The before-build snapshot and successful terminal result precede both browser runs. Tests, resources, metadata, configuration and contextual source pins were stable. This is shared-tree local macOS evidence, not a clean-base or other-platform build. Root has not accepted the native candidate.
