# Landing partition addendum

**Recommend a two-path native fix commit: nsBlockFrame.cpp and hidden-float-owner-queries.html.** This supersedes only the three-path packaging recommendation in css-hidden-float-native-review-v1; its correctness review and scoped acceptance recommendation stand unchanged.

The main WPT contains all four direct/inline, root/leaf regressions plus four visible controls. Its exact unchanged bytes ran against the standalone source phases: four PASS/four FAIL became eight PASS, with an OK harness end in both phases. Its fixtures and cleanup are self-contained; it does not import or depend on the separate multicol test.

visible-float-push-calibration.html never enters the new hidden-owner guard and does not prove native pushed-bit coverage. It is unnecessary to reproduce or guard this repair. Keep its existing file and successful runtime receipts in the preceding research material, rather than include it in the native fix commit. There is no need to land it as a separate production WPT merely to preserve the diagnostic.

The native code and main WPT remain byte-identical to the reviewed and tested artifacts. Removing an unrelated file from the proposed landing partition changes neither implementation nor regression test, so it requires no new browser/build run. The full twelve-case and earlier 95-case receipts remain valid historical evidence. Any later source or main-test change would need its own review and appropriate validation.

No new source, test-tree, index, browser, build, or compiler work was performed. BINDINGS.json records the exact retained payloads and independently selected eight-case results.
