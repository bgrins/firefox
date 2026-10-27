# Counter range and additive symbols comparison

Actual session49842 exited0 after four isolated build/test phases and successful original-stack restoration. Root checker82153 exited0 with COMPARISON_PASSED_VERIFIED_RESTORED. Independent phase and actual binding reviews pass; final terminal review and separate native acceptance remain pending this sealed archive.

| Phase | Harness cases | Rendering references | Improvements from baseline |
| --- | --- | --- | --- |
| HEAD90 baseline |66 PASS,10 FAIL|2 PASS,2 FAIL,1 scoped crash|—|
| Counter range only |66 PASS,10 FAIL|3 PASS,2 FAIL|Counter rendering crash repaired|
| Additive symbols only |76 PASS|3 PASS,1 FAIL,1 scoped crash|Ten CSSOM cases and additive rendering repaired|
| Combined |76 PASS|4 PASS,1 FAIL|All twelve improvements retained|

All28 range CSSOM cases and32 additive CSSOM cases pass in the combined phase. The counter-only repair eliminates the reproduced content-process Option unwrap panic in Servo_CounterStyleRule_IsInRange; the additive-only repair preserves that baseline crash while correcting its own ordering/rendering outcomes. Both single variants preserve every baseline PASS and exact retained-failure diagnostic. Combined preserves baseline and both singles. The remaining descriptor-calc reference failure is historical metadata-expected, unchanged across all four phases. There is no broader release-browser, memory-safety or security-impact claim.

All four comparison builds, fixture lint and the final original-stack build exit0. The genuine final checker independently parses all twelve raw captures, joins their exact source/build/binary records, verifies the actual terminal state and corroborates the live restored tree:72 guarded sources,37 saved originals,36 native modified paths,925 staged paths with full semantic index digests,11 existing installed WPT identities,494 resources and568 complete final roles. All six owned fixtures are removed. Recovery errors are empty. Root observed both process exits; they are retained in ROOT-CHECKER-EXECUTION.json.

The saved working stack through118 is restored. The compared counter/additive candidates are not installed or committed by this campaign. The pending119/121/122 repairs remain separately accepted and awaiting installation;120 remains held. Source audits identified these descriptor representation errors; abstract Lean models support the admission/export and meaning-ordering invariants. The browser comparisons supply the observed repair evidence, not an automatic extraction/refinement proof of Gecko.

This immutable archive precedes the final independent terminal review. Any later acceptance belongs in separate records, leaving this evidence unchanged.
