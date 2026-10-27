# Hidden-query landing comparison

All five builds and the restoration build passed. Exact named outcomes match in all five 79-case runs: baseline 62 PASS / 17 FAIL; column only 64/15; block only 73/6; Grid only 66/13; all three 79/0. All 50 tracked controls pass in every phase. Each repair passes its own final landing files, with no new baseline failures or calibration failures.

The phase builds normalize 24 source files to the pinned HEAD roles and guard 29 files. Restoration returns to the original working sources, including older unaccepted prototypes. ROOT-FINAL-CHECK confirms original/final/live source, HEAD and index identity, resource identity and absence of temporary tests.

This run validates exact cleaned landing files and individual repair attribution. Broader boundaries, standalone variants without fixes 104/105 and limited column/block costs are retained in the preceding boundary campaign. Float queries and table continuation coverage remain open. No isolated whole-upstream runtime, new Grid performance measurement or whole-CSS proof is claimed. Native acceptance is recorded separately.
