This disabled runner collects the sealed standalone partial-base page in installed Firefox 158.0 or retained portable Chrome for Testing 156.0.8078.80. It assigns no contextual timing verdict. Root owns activation and execution; no browser has run during preparation.

The four cases remain serial: contextual 16→24, literal 16→24, contextual 16→32, literal 16→32. Exact observe.js is unchanged. Exact observe.html is followed by one reporting-only deferred script tag. RESOURCES.json hashes actual served bodies, including this addition and report.js. The bridge polls only window.partialBaseObservations and posts after status becomes complete or incomplete. It adds no style/timing/membership reads and preserves tagged nonfinite values. Polling adds scheduling activity; no zero-observer-effect claim is made.

One localhost server serves three pinned resources. A random run ID and nonce bind one exclusive report; raw request bytes and normalized REPORT.json are retained. Four exact case names/order and sample order are required, but wrong/null timing values and acquisition errors remain valid observations. A 180-second watchdog bounds blocked ready promises/frames. If collection never finishes, no complete report is fabricated. Reference checks come from the pinned page; the receiver validates structure rather than independently recomputing them.

RESULT.json separates report_received, observation_complete, reference_checks_pass, cleanup_complete, and execution_complete. An incomplete report or failed reference calibration can accompany a successful owner lifecycle. There is no contextual PASS/FAIL gate. Inspect all four trajectories; later timing details cannot replace first-opacity observations.

Each browser gets a new owned private profile, no user.js creation, CSS feature overrides, WPT profile layer, or security-bypass flags. Chrome gets headless, first-run/default-browser suppression, private user-data-dir, and URL. Firefox gets headless, no-remote/new-instance, private profile, and URL. A launch flag alone does not establish that a relaunched Firefox retained headless mode.

At execution, Firefox executable/XUL/application.ini hashes are checked before and after. Chrome's complete saved portable entry set, root/file identities, modes, file hashes and symlink targets are checked without following directory links. The selected executable must be the pinned regular entry in that inventory. Preparation reads only saved references, not installed/portable bodies. Prior unsigned-distribution admission remains historical evidence; there is no new signature claim or chromedriver launch.

The executed owned-group cleanup helper is reused. A Firefox relaunch is admitted only when a unique main has the exact private profile and complete localhost URL/run/nonce and is its own group leader. Every other group member must be its direct plugin-container child with the exact profile. If the launcher exits before reporting, this same admission is required under the existing watchdog; a separate receipt records it. Chrome launcher exit is an incomplete-run error.

After server shutdown/join, cleanup first handles the original owned group. If a Firefox relaunch remains, two matching censuses precede SIGTERM to that exact group. Unknown members or ownership mismatches retain the profile and report failure. No analogous cross-group Chrome kill is attempted. All residual profile commands must disappear before temporary inode/owner/type and user.js absence checks permit removal. The relaunch procedure follows the prior successful root recovery, but this runner's browser integration is unexecuted. Receiver errors are checked after request threads finish.

Outputs are css-partial-base-stock-firefox-runtime-1 and css-partial-base-chrome-runtime-1. Exclusive directory creation prevents overwrite or reuse. This package does not access Git, native sources, the local experimental Firefox app, or canonical state.

Saved-only checks:

```sh
python3 -B artifacts/css-partial-base-installed-browsers-v1/check.py
node artifacts/css-partial-base-installed-browsers-v1/check_bridge.js
```

After review and root flag-only activation:

```sh
python3 -B artifacts/css-partial-base-installed-browsers-v1/run.py --browser firefox --run
python3 -B artifacts/css-partial-base-installed-browsers-v1/run.py --browser chrome --run
```

Without --run, only saved resource/reference pins are checked. Actual HTTP/browser integration, isolation and cleanup remain unexecuted. The frontend skill applies to the reporting-only adapter; this is a research collector, not a WPT runner or native test owner.
