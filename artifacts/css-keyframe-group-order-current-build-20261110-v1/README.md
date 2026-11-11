# Current committed keyframe-order build

The local optimized Nightly at `objdir-full.noindex/dist/Nightly.app` now includes
repair #172, signed commit `883d620fdbd6`, together with the earlier branch fixes.
BuildID is `20261110174523` (160.0a1). The build completed successfully and is left
installed for manual testing.

The final committed WPT and metadata pass: 31 PASS, two existing expected FAIL
callbacks and one OK harness result; all 34 results are expected. Exact callback
names/statuses match the candidate page from the preceding nine-page comparison.
Native/WPT source bytes, binary samples and the original 29 untracked status
entries (527 expanded paths) were authenticated before and after testing.

`build-result.json` and `WPT-RESULTS.json` record the actual commands' outcomes,
source/binary/log hashes and validation scope. Four nonfatal Mach tier-monitor
KeyError diagnostics remain in the successful build log. This final build is
separate from the reversible comparison, which established exactly two
improvements across 95 records and complete restoration before delivery.

No debug, sanitizer, performance benchmark or isolated upstream/release result
is implied. The missing-pseudo CSSOM repair remains separate unfinished work.
