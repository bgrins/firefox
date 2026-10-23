# Cost-v2 both timeout: bounded interpretation

## Observed

Copied only completed timing-subrun receipts, not the enclosing live experiment. Baseline/principal-only/OOF-only each returned84 measured rows, elapsed466/584/564ms respectively. Both returned no result observation before the75-second runner deadline. Its pinned binary/fixture/source inputs remained stable, profile was removed, leader exited−15 following the owned TERM, and final original-group inspection was empty. Cleanup errors were empty. This is distinct from the older v1 cleanup EPERM after completed observations.

No HTTP GET or progress receipts existed in v2. Therefore zero result observations cannot establish that the fixture loaded or reached a particular layout operation. Both's log uniquely contains missing `refresh-profile-instead` and incomplete initial-document localization messages. The generic headless/GFX/cpuinfo/channel-exit messages also occur in completed phases; they do not isolate the failure.

## Source-supported startup explanation

Narrow Searchfox discovery locates `refresh-profile-instead` in browser/base/content/safeMode.xhtml. BrowserGlue._beforeUIStartup opens that dialog modally under Services.appinfo.inSafeMode, before the first command-line handler/window. The safe-mode dialog's acceptance continues startup; cancel quits. toolkit/xre/SafeMode.h separately permits macOS Option-key startup unless MOZ_DISABLE_SAFE_MODE_KEY is set, and inherited MOZ_SAFE_MODE_RESTART. Fresh profile creation alone does not exclude these triggers.

This is a credible pre-URL startup explanation, not a proven reconstruction of the observed run. The previous environment/key state and requested-page GET were not captured. SOURCE-JOIN records full discovered source hashes and comparison with named local files (three full files identical; BrowserGlue differs globally but the retained complete _beforeUIStartup body is identical); it does not assert source-to-binary interpretation. Searchfox's installed CLI lacked --permalink; discovery is preserved by bytes/hash instead of an invented revision link. Initial sandbox DNS failures were retried read-only successfully. No user-global profile was inspected.

## Proposed next experiment

Use additive css-hidden-layout-cost-v3 for baseline/both with identical controlled child environment, server request log and acknowledged startup/per-batch progress. Preserve the exact query ordering and all full rectangle checks. Do not insert async yields between first and repeat queries. Keep currentv2 immutable and preserve its negative result. V3 runtime remains unexecuted.

A missing batch-end identifies only that interval. The between-batch45s deadline cannot interrupt synchronous work, while the runner75s deadline covers startup and execution. If a repeatable batch is isolated, a separate reduced operation diagnostic can refine the boundary. Current evidence does not justify claiming a native infinite loop, cost regression, or completion of the timing gate.
