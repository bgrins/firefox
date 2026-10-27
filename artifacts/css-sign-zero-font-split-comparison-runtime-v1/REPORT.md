# Split relative-length and Sign comparison

All three phases passed their comparison policy, and the original working stack was restored and rebuilt. Campaign session 80904 exited 0. The separately reviewed final checker, session 24470, exited 0 with COMPARISON_PASSED_VERIFIED_RESTORED. ROOT-FINAL-CHECK.json is an exact copy of its original output in css-sign-split-final-checker-bound-v1.

| Phase | PASS | FAIL | New landing cases passing |
| --- | ---: | ---: | ---: |
| Normalized HEAD90 baseline | 996 | 41 | 8/19 |
| Raw intermediate transport only | 1002 | 35 | 14/19 |
| Raw transport plus deferred Sign | 1007 | 30 | 19/19 |

The raw repair fixes six cases and passes its eight-case WPT independently. Sign adds five repairs and passes its eleven-case WPT with the raw prerequisite. All 1,018 existing control outcomes remain unchanged: 988 PASS and 30 FAIL. Every baseline PASS and exact retained failure is preserved; combined also preserves raw-only results. All phase builds passed. WPT exits were 1, 1 and 0 according to the retained metadata.

The final checker rejoins each phase's exact 67-source map, built binary hashes, 497 input roles and complete 1,037-case raw results. It verifies all 40 saved native originals, the original 36 changed native paths, semantic index with 925 staged research paths, 11 installed test body/inode identities, 427 resources, both rebuilt binaries and the 496 final roles. Owned fixtures and source temporaries are absent. No recovery errors occurred.

The restored browser contains the previously installed stack through fixes 117/118; it does not contain these experimental math changes. The two candidates remain subject to separate acceptance and installation decisions. Sign depends on raw transport and is not independently safe on HEAD90. Formal models and finite helper checks do not prove full native or provider correctness. No push or external submission occurred.
