# Final FontFace WPT v3 run admission

This minimal final-run package preserves integration-v2 and its test execution/acceptance semantics. The 16 native pins, context, resources, regression sources, config, case lists and commands are byte-identical. TEST-PINS proposed hashes change to the two reviewed WPT v3 files. METADATA-PINS changes exactly one path from its pinned three-line file to absent: `fontface-descriptor-updates-2.html.ini`. The inherited `live` test hashes remain historical installation context and are not repurposed as final test hashes.

All four dependencies are authenticated before helper import or execution: integration-v1, candidate-v2, integration-v2 and WPT-v3. The harness changes its build-to-run admission, records that witness, and adds a strict final-regression gate. No new tests or browser executions were introduced. The obsolete FAIL expectation is removed explicitly, based on the retained v2 pair: the style/family subtest changes from expected FAIL to unexpected PASS; all other regression result tuples remain unchanged.

## The actual build snapshot stays authoritative

Root began build 72558 with the retained v2 candidate-build-before snapshot. An exact copy is under `evidence/v2-build-before.json`, identified by EVIDENCE.json. Packaging does not assert a build terminal status.

For the final run, admission requires:

- The supplied build snapshot has the authenticated integration-v2 package identity, candidate phase and exact 16 candidate native hashes.
- The final run snapshot has integration-v3 identity and the same phase, Mach/Python identities and every fixed pin except the two tests and the single expectation-file removal.
- Each test changes from its exact v2 hash to its exact v3 hash. Authentication and source checks establish that these are solely the two contiguous spec metadata comments and identical ternary whitespace transformations.
- The exact three-line expectation file changes from SHA f53f02424e025e273c3d7c473f933ca11e714b1aab3b43adcf43d42f47389a1a to absent. Its original bytes, removal patch and actual v2 regression records are retained. This is an expectation correction, distinct from semantic-free test formatting.
- Every other fixed input remains unchanged. The final harness still checks its complete fixed pin set and requires identical pre/post browser snapshots.

The old pre-build binary hashes may differ from the newly built run binaries; that is the original harness's build-output boundary. The build-before snapshot, supplied successful terminal status and full build log remain root's evidence of compilation. No post-build snapshot is renamed or treated as pre-build evidence. A v3 snapshot supplied as `--build-before` is rejected.

`build-admission.json` records this distinction and is hashed in the final run receipt. `before.json` in the final output is only a pre-WPT snapshot. The source checker derives a proposed final pin set to test admission; it explicitly labels that as a check-only value, not an observed run or new build snapshot. Seven negative controls reject native/config/Mach drift, missing v3 tests and mislabeled build evidence.

## Source-only replay

Pin FREEZE.json externally, then:

```sh
python3 artifacts/css-fontface-provider-integration-v3/check.py
```

This authenticates all inputs/dependencies, proves exact harness replacements and invariant JSON bytes, checks actual retained build-snapshot admission, verifies metadata deletion and retained original bytes and raw v2 regression evidence, exercises the final-regression gate, and reruns the unchanged offline integration-v2/WPT-v3 checkers. It does not execute a build/browser or test callback. Python 3, Node and patch are required. The metadata deletion check uses patch -E and verifies absence. Exact original bytes are retained for restoration; automatic reverse-deletion handling is not claimed because BSD patch rejected recreation during packaging. The failed packaging attempts are retained under evidence/. CHECK-RESULT.json is excluded from source inputs.

## Root final matrix command

Finish and retain the exact v2 pair first. Install the two authenticated WPT v3 files and remove only the named metadata file. Do not capture a new build-before receipt and do not overwrite any v2 result. Once build 72558 has an actual successful terminal status, run:

```sh
python3 artifacts/css-fontface-provider-integration-v3/harness.py \
  --repo /Users/bgrins/code/firefox --phase candidate --suite matrix --execute \
  --build-before artifacts/css-fontface-provider-local-validation-v2/candidate-build-before/before.json \
  --build-log artifacts/css-fontface-provider-local-validation-v2/candidate-build.log \
  --build-exit-code 0 \
  --out artifacts/css-fontface-provider-local-validation-v3/final-matrix
```

Use the actual retained build-log path if root named it differently; the harness records its digest. Then run `--suite regressions` with a fresh final-regressions output and the same actual build evidence. That final rerun is required after the expectation removal. It must return zero with 19 subtests PASS and harness totals 4 PASS / 1 expected FAIL / 3 OK. The gate compares every exact status/expected tuple to v2, changing only the repaired subtest from unexpected PASS to normal PASS; the override-descriptors reftest remains expected FAIL. Final matrix success still requires all 68 subtests PASS, three harnesses OK, terminal zero and stable pins. Root must review the separate final receipt alongside the unchanged v2 pair and the explicit test-and-expectation delta. This package does not make integration-v2/compare.py silently accept v3 tests or declare cross-platform/lifetime acceptance.
