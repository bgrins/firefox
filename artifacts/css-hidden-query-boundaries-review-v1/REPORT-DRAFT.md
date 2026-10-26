# Hidden-query boundary runtime review (pending restoration)

Independent reconstruction of complete baseline raw events and RUN. This is a review of runtime evidence, not an independent review of the controller I authored. Final acceptance/seal awaits root terminal restoration and runtime FILES pin.

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
