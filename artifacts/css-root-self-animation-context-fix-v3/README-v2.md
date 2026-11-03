# Root-self animation fixture setup correction

This v2 package corrects only the WPT document setup in sealed v1. An explicit `<body>` now precedes the inline script, so the immediately invoked promise-test callback can append its iframe. The inline JavaScript, all 14 named callbacks, first/settled assertions and calibration controls are byte-identical. FIXTURE-DELTA.patch records the single insertion.

The actual v1 archived-original run a9086f/session90291/1d05bb exited0 as an observation owner, but all 14 WPT callbacks failed during setup because document.body was null. Those failures are not a root-font bug baseline and cannot be compared as repaired CSS behavior. The sealed v1 source package and runtime remain unchanged. A new archived-original run is required for this corrected fixture; no outcomes are predicted.

The native glue.rs candidate 554d1fb2ab9e0e8865b3cc3f0b0c111e4ac6fd5877cffe1070dbdc5479563dec and native.patch remain byte-identical to v1. The five extracted positives/five compiled rejection controls, source roundtrip, source/spec trace and independent original 16 diagnostic replay are inherited historical evidence for those unchanged bytes. CHECK-v1.json and README-v1.md preserve their original scope. None establishes that this candidate compiles or passes native browser tests.

Actual a15b7c/0 reran genuine WPT lint/Manifestv9 generation and registered 14 callbacks on one long page. e37ce7/0 parsed both documents with HTML5lib: the old main script belongs to head, the corrected main script belongs to body; the negative old structure is rejected. It also checked exact JavaScript/roster/native equality and the single insertion. BODY-CHECK.json and WPT-CHECK.json record those results. This addresses why the previous static registration-only check missed the setup problem; it is not a browser result.

The corrected WPT remains standalone for root font-size and root line-height identity. It does not require the variation-parent or descendant invalidation repairs. Native compilation and a fresh original/candidate comparison remain pending. No live source, application, index, canonical state or browser was changed during preparation.
