# Selected-color V5 candidate: 42 passing browser cases

Actual owner 86757/2c6dfe/b6d89a/0 built successfully and ran the exact42 suite: 42 PASS, zero FAIL, three OK page endings, browser exit0. The clean-provider baseline at the same branch HEAD had29 PASS/13 FAIL. All13 baseline failures became passes; all29 passing controls retain their complete result signatures. Independent reviewer27674/0e3950/a7c7fc/0 authenticated raw results, exact resources, source/build/browser provenance and restoration. The equality comparison gate remains false because the failure cohort improved; native acceptance remains false.

Eight improved cases concern identifier/color union or cyclic-default dependencies; five concern image color/unit/inheritance behavior. These are failing cases, not13 independently classified bugs. The current42 image-unit cases include scheme-dependent colors, so the three prepared absolute-color unit cases still need original/candidate validation. Standalone union-only/image-only patches and their reconciliation remain unfinished.

The runner restored all three source preimages and identities, the original20ab application, semantic index/staging and controls; owned process/profile cleanup passed. It verified and removed1,008,605,176 backup bytes. Root refreshed only raw-index bookkeeping after independent review. HEAD and149 accepted native fix commits remain unchanged. The installed baseline application is distinct from the ecfe candidate build used for these tests.

V3/E0502 andV4/E0106 failed attempts remain immutable. V5's explicit tracker lifetime correction compiled in actual Stylo; the successful browser result is evidence for the combined candidate, not a substitute for the remaining patch-isolation work or an all-CSS correctness claim.
