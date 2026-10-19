# All shorthand ordering browser pair

The final WPT has 40 subtests. Baseline: 16 failures and 24 passes. Candidate:
all 40 pass. The 61 existing regression subtests also pass in both phases;
105 unique outcome keys include four successful harness outcomes. All 16 changes
are FAIL to PASS; the other 89 outcomes are unchanged.

The regression compares cross-mapping pair order with fresh all expansion, so it
does not choose the unresolved absolute canonical order. Equal-value assignments
exercise the preparation gate. Controls cover longhand ordering, declaration-list
parsing, CSSOM priority replacement, excluded properties and unique identities.
The first failure in an assertion loop aborts later assertions; baseline failure
does not establish that later seeds ran.

Source/configuration/binary pins are stable within each phase. Only the target
native file changes between phases. Candidate Rust compilation and linking exit
successfully, as does WPT lint. Full logs retain four link build-monitor exceptions.
This is a shared local macOS build, not an isolated upstream or release-browser
measurement. The source patch is checked separately against retained upstream.
