# Current local browser after bug 2085413

The signed repair 90e0949346b5 is built successfully and left installed at
objdir-full.noindex/dist/Nightly.app. The active objdir is retained. This build
contains the query handoff repair alongside the previously committed branch work.
It does not apply the held combined producer/drain candidate for #160.

INPUTS.json and build-result.json bind the exact two Rust files, final WPT,
commit, application metadata and binary hashes. The build exits zero. The
same source bytes passed the preceding 26-case comparison and the final 13-case
comparison with four Stylo threads requested. This final rebuild is retained
for manual testing; the browser tests were run on the immediately preceding
candidate build, not rerun on this final build.

The earlier scope-cache baseline has been replaced intentionally. Subsequent
experiments should use this new build receipt when authenticating the current
local browser. Historical restoration receipts correctly refer to their earlier
baseline and should not be rerun as current-state checks.
