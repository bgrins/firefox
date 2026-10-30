# Independent direct-attribute observations

Both installed-browser observations complete with successful cleanup, and both independently recomputed reference checks and active controls pass. Firefox and Chrome differ on the active tainted variable reached through typed attr, as they do on the matched direct var case.

| Mode | Firefox 158 active first read + three frame reads | Chrome 156 active first read + three frame reads |
| --- | --- | --- |
| Tainted typed attr | horizontal-tb at all four reads | vertical-lr at all four reads |
| Direct var | horizontal-tb at all four reads | vertical-lr at all four reads |
| Untainted typed attr | horizontal-tb at all four reads | horizontal-tb at all four reads |
| Literal typed attr | vertical-lr at all four reads | vertical-lr at all four reads |

For the tainted and direct-var rows, both engines read vertical-rl before animation creation and at all four cancellation samples. The untainted and literal controls retain their respective values throughout. Active custom values and fixed 2000 ms duration, 750 ms currentTime, .375 progress, paused state and retained identities satisfy the pinned calibration. These timing and identity fields are collected after the four samples; they are not simultaneous first-read measurements.

The untainted control demonstrates successful recursive substitution of attribute text in this fixture, and the literal control distinguishes supported typed syntax from the distinct outer fallback/inherited vertical-rl. Chrome's tainted output matches the nested vertical-lr fallback prediction. Firefox's horizontal-tb output matches the animated source token. These observations distinguish outcomes without proving an internal substitution path. The separate spec trace conditions its direct interpretation on the ordinary writing-mode context; this report assigns no normative policy verdict and makes no alias-provenance or native-candidate acceptance claim.

Saved replay d1b28a/0 (Firefox) and 4a0928/0 (Chrome) joins each raw request to REPORT, authenticates exact effective resources and activated policy, and checks run ID, nonce, command, UA/schema and recorded cleanup. It extracts the calibration and activeExpectation functions from pinned observe.js and evaluates them in a DOM-free Node VM. Every named check and expectation matches the recorded report. Active untainted/literal controls pass in both engines; the two tainted predictions are false in Firefox and true in Chrome. False predictions remain data and do not alter observation completion.

Actual terminals are Firefox 7576/338f8b/0 and Chrome 62892/c8b7ea/0. Root receipts independently report group/profile/temporary absence. The reviewer did not inspect live processes or applications. FIREFOX.json and CHROME.json retain full observations, recalculations and input hashes. RUNTIME-SEALS.json and REFERENCES.json authenticate both frozen runtime manifests and all payloads, joined to the independently read inputs.

review.py invokes no browser, runner main, process control, Git or native operation. It requires completed reports and explicit actual terminal receipts; it is not a partial-report recovery tool. No fixture, owner or runtime body was modified.
