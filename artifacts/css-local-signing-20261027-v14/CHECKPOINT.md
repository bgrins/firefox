# Registered-number research signing checkpoint

| Commit | Work |
| --- | --- |
| 5dd16a257c43c3662b8b5c1c862e7f106fb10586 | Captured native admission and dependency proposals; independent review |
| c970ff09275b25d0193397e7976e27dadac0984c | 58-target browser comparison and pending-demand test overlay |
| 3e038c3a87cc7e57b50c63b8c445f411a7c6d1e7 | Five Python formatting changes; identical ASTs |

Accepted fixes remain 137 (138 tracked records, held fix 120 excluded). These commits do not accept a new native fix. The new browser and GTest cases have not run. Static artifact checks and independent reviews passed.

All 140 source pins in the signed unfinished-work checkpoint v8 match either their live bodies or the preserved prototype bodies. The current tracked native tree is committed HEAD for a standalone baseline comparison; 50 prototype files are intentionally parked, and their untracked companions remain in place. Restore the prototype only after the standalone comparison. No prototype body was discarded.

The first baseline build failed on stale generated declarations. The retry passed Rust compilation and was stopped cleanly during C++ compilation for this signing session. Both process groups are gone; preservation checks passed. Neither attempt is a completed native validation.

Resume from artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json after final signing synchronization. Use WPT capsule v2; v1 is historical and unexecuted. Restart build.py with a fresh label, head-original-build-3. All intermediate build outputs are retained for incremental reuse. The checkpoint records immutable runtime material; CURRENT-EPOCH.json, OWNED.json and ROLE.json remain mutable continuation files.

The previous prototype integration and unfinished WPTs remain recoverable through the signed v8 snapshot. The nested CSS Lean repository is unchanged. No push, Try submission or Phabricator action was taken.
