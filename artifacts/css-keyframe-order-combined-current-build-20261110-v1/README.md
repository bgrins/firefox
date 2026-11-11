# Combined keyframe repair build

The optimized browser includes combined repair #172 (`824de5537a87`). It was
built from clean tracked `daaf9f0c4c9be813f693bf1401c5a4e33aca588e` and is left installed at
`objdir-full.noindex/dist/Nightly.app`. BuildID is 20261110181740.

The focused percentage, existing named-range merge and new named-range WPT pages
exit zero: 36 PASS, two unrelated expected FAIL callbacks and three OK harness
endings. All 41 results are expected. Native/test hashes match the tested
pre-rewrite candidate and combined commit. The index and all 527 preexisting
untracked paths (29 status entries) were preserved. The successful build retains
four known nonfatal Mach tier-monitor KeyError diagnostics.

`BEFORE.json`, `BUILD.json`, `WPT-RESULTS.json` and `build-result.json` bind the
inputs, commands and results. The process helper is hash-authenticated against the
preceding signed runtime capsule and enforces bounded process-group completion.
This final build supplements the independently reviewed 95- and 99-record
comparisons; it does not add debug, sanitizer, performance or release validation.
The earlier percentage-only build receipt remains historical.
