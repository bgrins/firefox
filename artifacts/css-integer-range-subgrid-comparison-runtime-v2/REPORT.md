# Integer-range and saturated-subgrid comparison

Session92779 terminated with exit0 after all four comparison phases, full source restoration and a successful original-stack rebuild. Root checker46766 exited0 with COMPARISON_PASSED_VERIFIED_RESTORED. Independent terminal review and native acceptance remain separate pending gates.

| Phase | PASS | FAIL | Reftests PASS |
| --- | ---: | ---: | ---: |
| Original HEAD90 baseline | 291 | 48 | 6 |
| Integer range only | 299 | 40 | 6 |
| Subgrid cache only | 297 | 42 | 6 |
| Combined | 305 | 34 | 6 |

Each phase completed339 harness subtests and six reftests across21 files. The range candidate repairs eight failures (seven new cases plus one existing test); the cache candidate repairs six. All31 targeted landing cases pass combined. Both single variants preserve baseline passes and exact retained failures; combined also preserves each single variant. The remaining34 failures are retained baseline outcomes, not new regressions.

Root final verification authenticates raw results, architecture/build/source joins and comparison receipts, then verifies all69 original source guards,42 saved originals,36 native differences,925 staged paths,11 installed test inode/body identities,461 resource roles and532 final roles. Both rebuilt binary hashes join the live files. Owned temporary tests and replacement paths are absent. The original working stack through118 is restored; neither candidate is installed by this campaign.

The exact root receipt is ROOT-FINAL-CHECK.json, copied from css-integer-range-subgrid-final-checker-bound-v2. Its native_acceptance remains false. This report records a successful controlled comparison and restoration, not a signed fix, security classification or full Stylo refinement proof.
