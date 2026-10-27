# Disabled build-free float fixture diagnostic

SOURCE_READY_NOT_PREPARED_NOT_RUN. Root must review and wait for css-hidden-query-boundaries-runtime-v2 terminal restoration. Author did not read partial outcomes or run this controller.

After review, root may invoke `python3 -I -S -B run.py --manifest-sha <INPUT-FILES hash> --execute`. Omitting --execute stops before snapshot or temporary-file work. No source edit, compilation, native build or Git mutation is in the controller.

The previous reviewed root fixture runner is reused, with byte-identical run_wpt.py and exact12+4 WPT payloads from css-hidden-float-wpt-draft-v1. Changes: prior runtime v2; two temporary test paths/16 ordered subtests; explicit execute gate/scope check; additive failure classification; final dangling-symlink absence check. run.py.diff records the controller delta.

Before any test installation, require prior STATE terminal/restored/build0/no recovery errors; match current28-source/HEAD/index/native-diff snapshot to prior FINAL; require empty index and both temporary paths absent. Snapshot binaries and resources. Exclusively create only those two tests, lint, then run headless single-process WPT. Finally delete only successfully installed paths and require source/HEAD/index/binaries/resources unchanged and both paths absent. This deliberately uses restored working sources and their existing binary, which can contain other native prototypes: fixture calibration/discovery only, not clean-source candidate acceptance.

All16 complete raw test_status rows and two OK file ends are required. PASS and FAIL are both legitimate diagnostic observations. Failed calibration assertions do not abort collection or cause a second build; incomplete harness results, drift, lint failure or cleanup failure still fail the controller. No timing or baseline/candidate claim.

CLASSIFICATION.json separates visible-push-calibration4, main-visible-control6 and main-hidden-query6, with hidden calibration failures identified by their assertion label. First reported warm/hide/change/show/restore stage is retained where present. A selected-query failure is not automatically attributed to a native implementation. Passing a whole test proves its assertions ran; a failed test reports only the first failing assertion and does not reveal all later assertions or native PUSHED state.

The speculative four-case float column-placement fixture is separate from the ordinary query file. Its failures remain calibration limits and must not block or weaken the main12 geometry contract. Pushed-bit/continuation coverage requires additional source/runtime evidence even if its four geometries pass. Current owner-list repair may not fix nested-block cases independently of skipped-line marking.

No INPUTS/BEFORE/STATE, profile or runtime output has been created by the author. INPUT-FILES freezes source inputs only. Parent owns execution and terminal sealing after review.
