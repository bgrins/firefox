# Saved-data comparison for one-Rule payload workloads

Prepared only. No recorded-run comparison or browser/native execution was performed. The script is for the separately frozen css-revert-rule-indexed-single-trigger-wpt-v1 package, whose exact seal is pinned in compare.py. It inherits the previously reviewed integrity/raw-event replay function unchanged.

Run after A1, B1/B2 and A2 have closed:

```sh
python3 -I -S -B artifacts/css-revert-rule-indexed-single-trigger-comparison-v1/compare.py --a1 A1-RUNTIME --b B1-B2-RUNTIME --a2 A2-RUNTIME --output artifacts/NEW-COMPARISON.json
```

Inputs are the directories containing the timing runner's top-level RESULT.json, PINS.json and repeat-N children; do not pass the outer native-build owner directory or a single repeat child. A1/A2 must contain one baseline repetition each; B must contain two indexed-candidate repetitions. Output must be new and under artifacts. Run without Python optimization.

The script authenticates the frozen wrapper package, exact baseline/candidate native source-role pins, copied application metadata, run_info binding, explicit preferences, complete runtime gates, preserved pre/post state and owned-process cleanup records. It replays raw callback/fault assessment and full chunked benchmark-report validation, and checks staged resources. It reads saved records only; it does not assert the current application is restored or independently establish source-to-binary provenance.

All output axes are payload_blocks, taken from report rows' payloadBlocks. This counts matched custom-only blocks, not Rule triggers, total source nodes or indexed declarations. At zero payload, Rule mode still has one Rule declaration, while literal and Layer modes have none. Their generated CSS differs: those three zero-payload medians may reflect actual fixed index-construction cost and must not be treated as an identical-CSS noise floor.

Output retains A1/B1/B2/A2 row medians and samples, baseline/candidate median ranges, descriptive ratio ranges, round medians and zero-payload mode medians. Ratio ranges are observed combinations, not confidence intervals; zero denominators produce null. The optional 20-microsecond-grid residual is an observation, not timer calibration. No significance test, timing-acceptance threshold or performance acceptance is applied. Preserve literal/Layer controls and baseline drift when interpreting the one-trigger cost.

CHECK.json records syntax parsing, a synthetic fifteen-row descriptor check, correct zero-payload labeling, package integrity and unchanged raw-replay logic. These checks do not execute a browser or analyze future measurements. Existing packages/data were not changed. FILES.json seals this comparator preparation.
