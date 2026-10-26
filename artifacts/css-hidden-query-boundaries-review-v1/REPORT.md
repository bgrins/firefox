# Hidden-query boundary runtime review

Independent reconstruction of complete baseline raw events and RUN. This is a review of runtime evidence, not an independent review of the controller I authored. Verdict: ACCEPT the bounded historical baseline and successful restoration evidence; no candidate, standalone, performance or landing acceptance.

| Subset | PASS | Query FAIL | Calibration FAIL |
|---|---:|---:|---:|
| Historical66 |55|11|0|
| Compact18 |5|13|0|
| Provider20 |0|12|8|
| Total104 |60|36|8|

All nine harnesses ended OK. Historical66 identities, statuses and messages exactly match the previous baseline. All50 tracked landing cases pass. All28 native phase roles, prepared resources, retained inputs, raw/RUN identities and baseline build exit0 authenticate. Corrected INPUTS pin is `e75b88af92bb13e975ee9eb26062cb403179e0e061a813cc5e34895a9435099b`; its86 payloads and15 external cost pins authenticate.

All eight fragment cases fail visible warm calibration: cell6 was expected at `[150,10,40,20]`, observed `[10,50,40,20]`. These cases did not establish the required visible fragmentation. Their failing statuses cannot count as hidden-query failures or candidate regressions. The twelve ordinary span cases reach query comparisons and fail there. The compact failures cover five ordinary item/inner/leaf width paths, four inline-root/leaf paths, two float root/leaf paths and two outer-width table-first rescue paths. Full identities and assertion text are retained in baseline.json.

The controller stopped inside test_run after retaining complete raw/RUN and calibration receipts. STATE therefore need not contain the phase WPT summary. No cost run or candidate phase ran; no performance, standalone independence, native fix efficacy or landing verdict is supported. In particular, the new query failures are not automatically distinct new bugs. Retain them for comparison after the fragment fixture is separately calibrated/corrected.

No native, browser, build, index or Git operations were performed by this reviewer. The analyzer reads retained artifacts only. The prepared historical HEAD is90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e; a later research commit does not invalidate historical restoration equality.

## Final authentication and restoration

Runtime FILES `26180e0dd0c1304b5e93f3dd31bf64d67ac873bd2f0e86f8f7baf428ce5c8892` authenticates146 payloads. Corrected INPUTS has86 inputs and15 cost capsule pins. Final STATE is terminal with the expected calibration exception, restored=true, restore_build_exit=0 and no recovery errors. Historical BEFORE=FINAL=prepared before. Baseline build and WPT lint both exit0. The controller's overall exit1 is expected failure of the calibration gate, not failure to restore.

Only baseline was executed. STATE lacks a WPT summary because the gate threw inside test_run after saving raw/RUN. The independently reconstructed complete104/9 receipt is therefore the outcome authority. No result or timing is invented for unstarted phases. Root reported current source equality and allfour temporary diagnostics absent at restoration; this review authenticates historical equality rather than requiring that live files remain unchanged during the next diagnostic.

Reproduction: `python3 -I -S -B analyze.py --phase baseline --final-files-sha256 26180e0dd0c1304b5e93f3dd31bf64d67ac873bd2f0e86f8f7baf428ce5c8892`. No browser/build/compiler is used. FINAL.json and its read-pin inventory retain this replay. Assertions and case identities remain unchanged in the historical v1 fixture.
