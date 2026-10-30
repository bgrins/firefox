# Independent original same-element diagnostic replay

Frozen runtime 2 authenticates and replays exactly: actual owner 55405/658b02/0, WPT exit 1, one PASS, one FAIL, one OK ending, and both complete private records. The acyclic failure is the intended first-opacity assertion, not acquisition, literal calibration or record transport. The self-feedback callback PASS means its literal controls and ownership assertions passed; it has no contextual endpoint oracle.

| Trajectory | First and three passive values | Later computed CSS duration | Applied effect duration | Interpretation |
| --- | --- | --- | --- | --- |
| Acyclic contextual | opacity 0.75 throughout | `2s, 1.375s` | font 2000 ms; opacity 1000 ms | Font reaches 22 px, while the separately held opacity effect retains its initial duration. Expected finite acyclic opacity is 6/11. |
| Acyclic literal | opacity 0.545455 throughout | `2s, 1.375s` | font 2000 ms; opacity 1375 ms | Literal first/read/passive/details controls pass. |
| Stepped contextual feedback | font 32 px throughout | `1s` | 500 ms | Computed duration and applied duration differ; no observed alternation in the bounded sequence. |
| Stepped literal 500 ms | font 32 px throughout | `0.5s` | 500 ms | Completed-step/fill control passes. |
| Stepped literal 1000 ms | font 16 px throughout | `1s` | 1000 ms | Active-step control passes. |

Both detailed snapshots, before and after membership queries, retain these values. All recorded animation/effect memberships remain true; held times are 750 ms and states paused. The acyclic contextual initial snapshot was font 16 px and opacity duration 1000 ms. Its font driver changed independently to 750/2000, giving 22 px. Thus this is an observed same-element acyclic dependency mismatch on the restored original binary, not evidence that two independent effects require a self-cycle policy.

The feedback initial snapshot was font 16 px, computed/applied duration 500 ms, at time zero. After the sole seek to 750 ms it returns the filled 32 px output, while computed duration becomes 1000 ms and the applied effect stays 500 ms. This is consistent with stale applied timing in this bounded original observation; it does not establish the causal implementation path. The conditional mathematical reevaluation map would alternate its endpoints, but this run neither observes that alternation nor selects a normative cycle policy. Completion within this run is not a universal no-hang/convergence result.

`replay.py` independently authenticates all 28 frozen regular runtime payloads without following symlinks, all 19 fixture payloads, exact tested resources and inherited metadata, exact callback roster/raw assessment, one complete suite, actual terminal/runner/raw joins, both receiver schemas/run IDs, and the failure message's embedded record. It replays pure assertions over saved records: all literal checks pass and contextual acyclic checks reject. It does not execute DOM callbacks or the owner. The byte-identical saved PRE/POST records include control hashes, HEAD, tracked diff/status hashes, real index hash and binary/application/provider pins; this is saved-state verification, not a new live-state check. Owned process cleanup is recorded complete.

Successful independent replay: 923753/0. Earlier runtime 1 (61311/e2b902/0) selected zero tests and is explicitly incomplete harness evidence; it is not a baseline or browser observation. No candidate result, native acceptance, new accepted ID, queue-path diagnosis, or general CSS correctness claim is made here. Existing coupled/zero-start feedback history and its abstract model remain separate retained evidence.
