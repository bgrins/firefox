# Registered-property observation V2: independent replay

Firefox 158 and Chrome 156 complete all four callbacks and all recorded phases. The Firefox unregistered, universal-registration and typed-registration callbacks fail their tentative fallback assertion; the literal callback passes. All independently recomputed registration, syntax, source, timing and identity calibration checks pass, as does the literal active control. The harness ends OK. Firefox therefore has a complete observation but a failing WPT suite. Chrome passes all four callbacks; neither observation settles normative animation-taint policy.

| Firefox mode | Initial four sink reads | Ordinary-mutation four sink reads | Callback |
| --- | --- | --- | --- |
| Unregistered | vertical-rl throughout | vertical-rl throughout | FAIL |
| Registered universal `*` | vertical-rl throughout | vertical-rl throughout | FAIL |
| Registered `<custom-ident>` | vertical-rl throughout | vertical-rl throughout | FAIL |
| Literal | vertical-lr throughout | vertical-lr throughout | PASS |

The two registered cases successfully registered with inherits=false and initial horizontal-tb. Calibration independently distinguishes that behavior from unregistered inheritance; the typed case also rejects a multi-identifier declaration while the universal case retains it. The active custom value remains vertical-rl, with duration2000, time750, progress.375, paused state and retained identities in both phases. These controls establish that the requested configurations were exercised, not which internal provenance path produced a sink value. Timing/source/identity details are sequential observations after the four sink samples.

Saved replay 2b6087/0 reconstructs the full captured payload using the exact pinned report.js in a DOM-free Node VM. It joins raw request to REPORT, nonce/run ID, command URL, effective resource hashes, active owner policy/manifest, UA, terminal48509/922fa0/0 and cleanup receipts. The VM exposes only recorded inputs and fake completion/fetch functions; it performs no DOM or network queries. Both recorded booleans and the complete reconstructed report are checked. The initial cleanup group operation's PermissionError remains in the receipt; the recorded direct-process reap/census finishes with owned group, profile commands and temporary directory absent. This reviewer performs no fresh process/app check.

Chrome replay 98f03e/0 authenticates terminal71944/e3db75/0 and the same resource/nonce/policy/report joins. All four callbacks PASS and the harness ends OK. All four modes yield vertical-lr for all eight readings, and every reference/literal check passes. The first phase distinguishes the fallback from both the underlying horizontal-tb and animated vertical-rl values; the later underlying value equals vertical-lr, so that phase alone would not discriminate selection. The complete literal records are exactly equal across browsers.

RUNTIME-SEALS.json binds the final fourteen-payload Firefox and Chrome manifests (b107bff8 and b2b86450). Authentication482b01/0 confirms every frozen payload equals its pre-freeze replay input hash; all54 reference hashes are retained. The earlier V1 Firefox timeout remains unchanged and cannot be converted into success by this successor. Hiding the diagnostic pre is the sole fixture change; completion here does not by itself prove the old timeout cause.

The measured difference includes both registered syntaxes, with successful registration and distinct initial fallback controls. This supports keeping registered producer scope as an acceptance obligation. The experimental native proposal's singleton gate excludes registered sources, but these installed-browser observations do not establish its native behavior or a normative registration exemption. No accepted fix, security conclusion, normative policy verdict or new theorem is asserted. No browser, native, Git, control, cleanup or current-state operation was performed for this replay.
