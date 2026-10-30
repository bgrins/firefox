# Stock Firefox masked-duration observation

Disabled standalone runner for the exact nine callbacks in the sealed masked suite. It launches the installed Firefox 158.0 with a fresh private profile, without WPT preference files or CSS feature overrides. This is an applicability observation, not a branch build, native acceptance, or proof that every installed-browser preference equals a published default.

Four HTML bodies and testharness.js are authenticated directly from the sealed suite; no fixture CSS, JavaScript or callback name changes. The only replaced resource is testharnessreport.js, separately pinned in policy. Runtime RESOURCES.json hashes every actual in-memory served body, including that bridge. Its reporting bridge waits for testharness completion, then sends all callback statuses/messages/stacks, the harness ending, user agent and three CSS.supports results to a nonce-bound localhost receiver. It does not add timing/style reads to the fixture sequence. After acknowledgement, it navigates to the next exact page. Each completed page has an exclusive JSON file; the original submitted JSON bytes are also retained. Successful callbacks retain their verdict, not extra unobserved numeric snapshots. Failure messages retain the fixture's own diagnostic values.

The server binds only 127.0.0.1 on an ephemeral port and serves a fixed in-memory resource map. Reports require its exact Host/Origin, random run ID and secret path nonce, bounded body size, expected next page, exact callback order/names, status schema and Firefox version. No directory listing, arbitrary file path or cross-origin reporting is supported. UA/version and CSS.supports are observations, not proof of feature completeness. An unexpected UA is an admission failure whose original request bytes remain available.

The installed executable, XUL and application.ini are pinned and rechecked before and after execution. The captured application.ini declares version 158.0 / BuildID 20261007201254 / mozilla-release source stamp eb9a6e3a736802c8e080a76c44dc81f409d99d54; its header says that file is not used directly. Actual UA reporting therefore remains required. This is not a whole installed-bundle or compiler-input attestation. No signature/security-policy alteration is performed.

The runner creates an owned 0700 temporary root/profile and starts a separate process session using --headless --no-remote --new-instance --profile. It does not reuse the user's profile, write user.js, copy test metadata/prefs, use geckodriver, launch mach/wptrunner, or set MOZ feature environment variables. HOME is inherited unchanged; TMPDIR points to the owned temporary root. Browser-generated profile defaults are allowed. Site/enterprise/install policy behavior is not disabled. The existing reviewed process-group termination helper is reused. Cleanup additionally checks for commands naming the private profile and its retained directory identity before removal; a cleanup discrepancy retains the temporary directory and fails the wrapper. It never kills other Firefox processes merely because they use the same installed binary.

The 240-second external watchdog bounds all four pages. Request threads have five-second connection timeouts and are joined at server shutdown; late receiver errors still fail final wrapper completion. Partial/missing pages and non-PASS status codes remain explicit. Complete ordinary FAIL results do not fail the wrapper: exit 0 means all reports were collected, binary pins preserved and owned cleanup completed, not that the tests passed. RESULT and ASSESSMENT separately retain failures, other statuses, harness endings, all_callbacks_pass and all_endings_ok. suite_pass requires both callback and harness success; a harness error cannot become a suite PASS merely because all callbacks passed. No expectation metadata or source-policy assumption reclassifies a failure. No browser has been launched in preparing this package.

## Review and execution

Pure checks (no browser, listening socket or live branch guard):

```sh
python3 -I -S -B artifacts/css-stock-firefox-masked-nine-v1/check.py
```

After root reviews the sealed package and changes only POLICY.execution_enabled to true, preserve the disabled preimages and reseal, then run:

```sh
python3 -I -S -B artifacts/css-stock-firefox-masked-nine-v1/run.py --run
```

The fixed output path is artifacts/css-stock-firefox-masked-nine-runtime-1 and must be absent. Running without --run only authenticates saved fixture/helper pins. No native source, Git, index, canonical epoch, local-build application or existing sealed package is modified.

Preparation followed the Firefox frontend skill and read performance guidance. New bridge checks cover syntax and completion-only transport with unchanged failing messages/false CSS.supports, plus strict receiver shape/nonce/origin/order/duplicate controls and partial collection. The four fixture pages already have genuine manifest/lint validation in their immutable source package; this standalone runner does not load WPT metadata or claim a new WPT harness execution. Full real HTTP/browser integration remains for root's actual run.
