# Branch probes for two attribute cycle leads

Prepared for HEAD 87445004c1ae44d9c1e2873b91f01414cf75cbb2. Browser execution is pending the parent's explicit go after shared GTests. No branch result is claimed.

raw/ and used/ contain byte-identical copies of the sealed release probes and validators. EXACT-COPIES.json records their origin and digest. REFERENCES.json pins the original manifests, reports and spec traces. The 13 cases per probe therefore compare the same inputs and expected values against the local build.

run_branch.py launches only objdir-full.noindex/dist/Nightly.app via LaunchServices, with a new owned profile, -headless and -no-remote, serving the selected page from an ephemeral loopback port. PINS.json fixes the executable, XUL, application/platform metadata and three relevant native sources by hash, resolved path and size. It checks those pins and HEAD before launch and again afterward, alongside the source bundle and original audit references. A changed build/source/HEAD requires a fresh versioned preparation; do not edit this sealed bundle.

Run one probe at a time, only after the parent releases the browser. Replace MANIFEST_SHA with FILES.json's externally recorded SHA256. Output paths must be absent and outside this sealed directory:

```sh
python3 -I -S -B artifacts/css-attr-cycle-branch-probes-v1/run_branch.py MANIFEST_SHA raw /Users/bgrins/code/firefox/artifacts/css-attr-raw-branch-observation-v1
python3 -I -S -B artifacts/css-attr-cycle-branch-probes-v1/run_branch.py MANIFEST_SHA used /Users/bgrins/code/firefox/artifacts/css-attr-used-branch-observation-v1
```

Capture the actual tool session terminal exit separately. Exit 0 means one valid result, unchanged pins/HEAD and passing calibration controls; predicted-spec differences are recorded, not treated as execution failure. Inspect RESULT.json and SUMMARY.json before attributing a branch failure. Known release counts are raw: five differences/eight controls; used: seven differences/six controls. No new accepted fix count follows automatically.

Cleanup rechecks the exact executable/profile command before terminating owned browser parents, reaps its LaunchServices process, closes the server and removes the profile only without cleanup errors. The evidence covers matched parent processes, not an independent process-group inventory or every browser child's exit. On cleanup error, retain the profile and inspect owned processes. It never kills by application name or touches a user profile.

wpt/ contains two standalone testharness candidates, intended eventually for testing/web-platform/tests/css/css-values/. Neither is installed there or run yet. Each reuses the exact release case table, with parse assertions and computed-value assertions. The used-fallback candidate additionally checks both mutual-cycle participants. The raw candidate conflicts with one existing WPT expectation: preserve the old oracle until that conflict is adjudicated.

The separate repair proposals define narrow semantic changes and regression gates; they are not compiled patches. No native source, live WPT, index, HEAD, ledger or canonical Lean was changed. The original positive traces use complete captured current primary specifications; webspec-index remained unavailable, and no exhaustive graph claim is made.
