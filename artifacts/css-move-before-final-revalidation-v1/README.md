# Revalidate the completed final moveBefore run

The completed browser run produced70PASS/12OK/childexit0 and preserved state, but the original final wrapper exited1 because its projection incorrectly removed known_intermittent field presence on seven selector rows. Every other field of all82 callback/ending signatures matches. The original raw log, failed ASSESSMENT/RESULT, binding and sealed promotion remain immutable.

WPT SubtestResult normalizes an absent intermittent list to []; testrunner passes it explicitly to mozlog. The optional logger field defaults to None and is omitted only when equal to that default. Therefore [] remains present. Separately, test_status removes expected when it equals status. The corrected assessor changes only expected FAIL→PASS/absent on the exact seven prior PASS rows, retaining known_intermittent=[] and present=true. No global field or signature comparison is removed. SOURCE-CONTRACT.json pins the exact signed/current logger source and bounded excerpts; Searchfox discovery9abc33/5dc9e1/b42aaa/ee0e49 agrees.

replay.py authenticates the completed phase, reproduces every published field under the old assessor, then assesses the SAME raw events under the corrected projection. The entire corrected assessment must equal the failed assessment with only comparison_errors=[] and comparison_gate_passed=true. Every status, message, field-presence bit and ending remains exact. check.py adds negative controls for absent/null/nonempty intermittent lists, old incorrect omission, changed controls/results/endings/counts/expectations and nonzero child exit.

revalidate.py reuses the sealed final.py full source/application/epoch/control/deletion/ownership and preservation checks. Its driver delta replaces browser launch with authenticated replay of the already completed phase, verifies its original/result/cleanup and exact metadata/binary/snapshot joins, then repeats all guards. It writes only a NEW css-move-before-final-revalidation-runtime-1 receipt directory. No browser or build is launched and no canonical/source/index/history is rewritten. The result explicitly says browser_execution_performed=false and reassessed_actual_completed_run=true; original wrapperexit1 is root-reported64291/9d9000, not relabeled as a successful execution.

Root-only command after review/seal:

    python3 -I -S artifacts/css-move-before-final-revalidation-v1/revalidate.py REVALIDATION_FILES_SHA adcdca56d3ca738477e7df9c4b725ad6d3b3fbaab122f24578e418002ab4fe4a 6a097e0a1c42caef5ca5575193c37e70e7efa1cbe6fb8f518e9b88c1f2245799 artifacts/css-move-before-final-binding-v1/BINDING.json 2743faddb2192a599f167984bb6c75d7dfa9179b39e1edd97379e6c24bec43f7

No second browser run is needed to repair this deterministic assessment error, provided the fresh full guards succeed. No native acceptance is allocated by this package.

Actual saved replay36cbe9/0 passes; twelve semantic negatives reject. Independent bounded code/pin review a459b8/ffd591 clears the exact correction and driver. b7e52c authenticates all eighteen references and proves the original final preflight/verify body is byte-identical; Python AST parses. These preparation checks did not execute the full current-state guard or revalidation main.

Root full replay/driver and exact-delta review52cb69/f61d13 cleared the sealed revalidation for root execution. No fresh browser run is performed by this driver.
