# Independent CSS/WAAPI browser observation

Both completed observations calibrate correctly. Pure script effects and matched CSS animations behave alike within each engine, but their active writing-mode differs across engines. No normative taint verdict is assigned.

| Engine / mode | Before | Active first read + three frame reads | Cancel first read + three frame reads |
| --- | --- | --- | --- |
| Firefox 158, WAAPI | vertical-rl | horizontal-tb, horizontal-tb, horizontal-tb, horizontal-tb | vertical-rl at all four reads |
| Firefox 158, CSS | vertical-rl | horizontal-tb, horizontal-tb, horizontal-tb, horizontal-tb | vertical-rl at all four reads |
| Chrome 156, WAAPI | vertical-rl | vertical-lr, vertical-lr, vertical-lr, vertical-lr | vertical-rl at all four reads |
| Chrome 156, CSS | vertical-rl | vertical-lr, vertical-lr, vertical-lr, vertical-lr | vertical-rl at all four reads |
| Both, literal | vertical-lr | vertical-lr at all four reads | vertical-lr at all four reads |

The active custom value is horizontal-tb in every mode. Later details show duration 2000 ms, currentTime 750 ms, progress .375, paused state and retained identities. After cancellation the ordinary custom value is vertical-rl, the held animation is idle with null currentTime, and current membership is empty. Timing/membership fields follow the samples and are not simultaneous first-read snapshots. The CSS rule remains present after cancellation.

The pure WAAPI iframe contains no CSS keyframes rule. Chrome's sink outputs therefore match the active-value fallback prediction for this script case; it does not settle Variables' written @keyframes producer condition. Firefox consumes the active token in both modes. The sealed scope note retains INCONCLUSIVE for the normative WAAPI bridge. These installed-browser observations neither validate the native candidate nor increment accepted fixes.

Saved replay a12865/0 joins each raw request to REPORT, validates run-id/nonce/command and UA/schema, and verifies exact served resources, runtime policy and result/cleanup receipts. It executes the calibration function extracted from pinned observe.js in a DOM-free Node VM, compares every recomputed named check with the recorded arrays, and finds all true. FIREFOX.json and CHROME.json retain all rows, owner results and exact input hashes. RUNTIME-SEALS.json and REFERENCES.json join both later frozen manifests and every payload to those inputs.

Actual terminals are Firefox 82087/667f1a/0 and Chrome 58909/74eea5/0. Both execution and observation completion are true, separately from successful reference checks. Root receipts independently report group/profile/temporary absence. This reviewer did not recensus processes or authenticate live apps; root's cleanup verification remains separately attributed.

review.py reads saved inputs, runs only the pure JavaScript calibration and writes a new result under this review directory. It does not invoke browser, runner main, cleanup, Git or native operations. No sealed runtime, fixture or owner was modified.
