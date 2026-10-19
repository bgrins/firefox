# Loaded FontFace descriptor update validation

The reviewed provider change uses fresh native font entries when changing descriptors on a loaded FontFace. The stack already includes worker family cleanup from repair #50. The standalone patch includes the same necessary four-line cleanup and was built and tested on upstream `976279105b2e78b8666a959eb3f25c9176cefaf8`.

Without that cleanup, the isolated candidate passes 68 of 76 new subtests. Four descriptor-only worker cases retain obsolete family/coverage entries, and four worker removal cases also fail. Adding only the cleanup makes all 76 pass. Across the full matrix, eight checks improve and 82 retain their result; one preexisting override-descriptor reftest remains an expected failure. The test harness reports 90 expected checks and zero unexpected results.

The earlier shared-tree comparison established 38 improvements in the original 68-case matrix; these isolated runs specifically establish the worker dependency and validate the complete standalone final state. They are not an isolated pristine-base comparison against the provider changes as a whole.

The full initial build and incremental support build exited zero. The latter compiled layout/style and relinked XUL despite Mach progress callbacks reporting KeyError export. Binary and source hashes are retained before and after testing.

Validation is local macOS CoreText. Other platform backends have source review, not compilation or runtime validation here. Nonloaded provider sharing, shutdown/reentry scheduling, external local-font replacement and full native lifetime proofs remain outside this repair's established coverage.

`stack-native-wpt.patch` contains 16 native files, three WPT files and removal of obsolete expected-failure metadata. `standalone-native-wpt.patch` additionally includes the worker cleanup. Neither patch contains research tooling or documentation.
