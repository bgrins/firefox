# Named-range group-order runtime comparison

Root completed the optimized baseline/candidate comparison after reviewing the
prepared wrapper and freezing execution at signed `6b50ecbc27f1bd9faae795dc14edcc6dcd9da199`.
The baseline has 77 PASS / 12 FAIL callbacks; the candidate has 80 PASS / 9 FAIL.
Both have ten OK harness endings. Exactly the three intended ordering cases
improve; all other statuses and messages match. Build and both WPT lint commands
exit zero. The successful build retains four known nonfatal Mach tier-monitor
`KeyError: 'export'` diagnostics. `ROOT-RESULTS.json` independently checks the raw
records without using the runner's analyzer. Full live restoration is reviewed
separately in `css-named-range-group-order-runtime-review-20261110-v1`.

The remaining preparation description records the experiment's predeclared
gates. Frozen inputs and raw results are historical evidence; the runner is
deliberately tied to its execution HEAD and retained browser, not a command to
rerun blindly after history reorganization.

The baseline uses the retained #172 browser from `css-keyframe-group-order-current-build-20261110-v1/build-result.json`. Candidate installs the exact reviewed Rust glue from patch `c0884212b8fb2d574395950c8e08abb754614809abe36983bd606accd61725cd` and performs `./mach build binaries -j6` with a 2,400-second deadline. Both variants install the corrected existing merge WPT and the exact new three-callback temporary page. Both lint these two WPT paths. The ten-page inventory retains the prior nine-page generation/range/attribute suite and adds the new page.

Require exactly 99 records: 89 callbacks and ten OK harness endings. The expected baseline vector is 77 PASS / 12 FAIL; candidate is 80 PASS / 9 FAIL. The three permitted improvements are the corrected existing merge callback and the new repeated-group and repeated-groups callbacks. All other statuses and messages must match. Attribute mutation retains 12 PASS; percentage `getKeyframes` retains 31 PASS and its two known custom-property FAILs. The new unique-group control must pass. These are predictions/gates, not results of a run.

`EXPECTED-BASELINE.json` derives from the signed prior candidate's observed status vector, with the existing merge callback changed to predicted FAIL for its corrected oracle and the three new callbacks appended. The new repeated-pair case has not yet run. A different actual baseline stops the experiment for review. No callbacks are omitted because their temporary fixture is currently absent. Both that absence and metadata absence are explicit pins; the fixture's final three-case content is separately hashed.

`ORIGINS.json` identifies signed commit `3d55e8e0d364b92dde0110553202aacbb0983dfb`. Bundle/process/analyzer code is unchanged. `WRAPPER-DIFF.patch` is limited to the unset-HEAD guard and linting both WPT paths in both modes. `PARSER-DIFF.patch` makes synthetic controls use the full known baseline vector and adds changed-known-failure rejection. All 26 negative controls pass, including callback/harness key separation, missing/duplicate events, partial improvements and unexpected messages. These controls exercise parsing/comparison, not browser behavior.

`SOURCE-ROLES.json` specifies candidate-only native glue and install-in-both tracked WPT. `runtime-inputs/test-source-pins.json` contains 34 test/helper/metadata presence pins, including current #172 metadata, with no obsolete percentage-failure stanza assumed. `check.py` verifies them against revision `33b02650a474a0a4c2d9f6421283ba89f9a18b1c`, authenticates exact candidate copies, verifies the four retained-build source hashes and artifact-only revision bridge, and checks inventories/status totals. The checked retained source bridge matters because a small sampled-binary list alone cannot prove which native source it contains.

Root's final freeze, after review and the preceding research commit:

```sh
python3 -I artifacts/css-named-range-group-order-runtime-20261110-v1/freeze.py FULL_CURRENT_HEAD
```

This only updates this capsule's HEAD/manifest and performs preparation checks. It requires current HEAD, verifies only artifact paths changed since the pinned source revision, and refuses a second freeze. A failed freeze is a stop condition; inspect its receipt before executing anything. `RUN-INPUTS.json` then binds all executable runtime inputs and installed bytes. Root may launch separate output directories:

```sh
python3 -I artifacts/css-named-range-group-order-runtime-20261110-v1/run.py baseline baseline1
python3 -I artifacts/css-named-range-group-order-runtime-20261110-v1/run.py candidate candidate1 baseline1
```

The existing transaction backs up/restores the full app and three extras, restores tracked WPT/native files under concurrent-edit guards, removes only the exact installed temporary fixture, validates source/test/config/HEAD/index and sampled binaries, and requires owned process-group absence before restoration/backup cleanup. Source and app remain exclusively held through independent terminal review. Build intermediates are not rolled back; no claims of byte-for-byte object-directory restoration are made. An analyzer failure still follows the restoration path and retains raw logs. WPT exit 0/1 is allowed because the baseline has intentional unannotated failures; exact raw inventory and status gates remain mandatory, and root should inspect complete logs for nonfatal diagnostics.

A successful optimized comparison would support this bounded range-order extension. Debug remains unrun coverage; this experiment does not close the separate missing-pseudo CSSOM debug gate or establish memory/performance equivalence. Native delivery, metadata decisions, signing and a final committed-source build remain root-owned follow-up steps.
