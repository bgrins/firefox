# Portable Chrome for Testing fallback

The host reports `arm64` (fd2ce8/0). The official channel API fetched at 2026-10-30T07:16:02.820Z lists Stable **156.0.8078.80**, revision 1706539, with matching mac-arm64 Chrome and ChromeDriver. HEAD-only requests returned 200 for both archives (469d74/0):

| Asset | Official URL | Compressed bytes |
| --- | --- | --- |
| Chrome | [chrome-mac-arm64.zip](https://storage.googleapis.com/chrome-for-testing-public/156.0.8078.80/mac-arm64/chrome-mac-arm64.zip) | 195,027,080 |
| ChromeDriver | [chromedriver-mac-arm64.zip](https://storage.googleapis.com/chrome-for-testing-public/156.0.8078.80/mac-arm64/chromedriver-mac-arm64.zip) | 9,342,472 |

Total compressed size is 204,369,552 bytes; expanded size was not measured. `DOWNLOAD-METADATA.json` retains headers, generation identifiers and transport MD5 values. The saved API contains no SHA-256 field; MD5 and a locally recorded download hash are not publisher signature verification. The [official API documentation](https://github.com/GoogleChromeLabs/chrome-for-testing#json-api-endpoints) defines the channel feed; [Chrome's documentation](https://developer.chrome.com/docs/automation-and-testing/chrome-for-testing) describes versioned, non-auto-updating testing binaries. Pin this version for an experiment rather than silently resolving a later Stable version.

No browser or driver archive was downloaded, extracted or launched. Only version JSON, HTTP headers and upstream text sources were retrieved. No package, profile, browser setting, native source, Git or canonical state changed. Safari's prior session admission failure remains unrelated to CSS behavior.

## Future owned download and signature admission

Root can prepare a new private temporary directory, download the two pinned URLs into it, compare sizes and transport digests, record SHA-256 hashes, inspect archive paths, and extract within that directory. Reject absolute or escaping archive entries; preserve internal app/framework symlinks required by signed bundles. Do not copy into /Applications. The expected executables are `chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing` and `chromedriver-mac-arm64/chromedriver`, matching Google's [Chrome](https://raw.githubusercontent.com/puppeteer/puppeteer/main/packages/browsers/src/browser-data/chrome.ts) and [driver](https://raw.githubusercontent.com/puppeteer/puppeteer/main/packages/browsers/src/browser-data/chromedriver.ts) package-path implementations.

Before executing either downloaded binary, record and validate its actual signature and publisher identity. The following are verification commands, not executed here:

```sh
codesign --verify --deep --strict --verbose=2 "$cft_app"
codesign --display --verbose=4 "$cft_app"
spctl --assess --type execute --verbose=4 "$cft_app"
codesign --verify --strict --verbose=2 "$cft_driver"
codesign --display --verbose=4 "$cft_driver"
spctl --assess --type execute --verbose=4 "$cft_driver"
```

Require successful integrity checks, acceptable Apple policy assessment, and an authenticated Google publisher identity; retain the actual certificate/team/designated-requirement outputs. This plan does not claim that the current archives have already passed, or that the app and command-line driver have identical signing/notarization arrangements. If a binary is unsigned, ad hoc signed or rejected, stop for explicit review of that finding. Do not remove quarantine, re-sign, disable Gatekeeper, or substitute a system Chrome. Apple's [code-signing guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Procedures/Procedures.html) distinguishes integrity verification from local execution-policy assessment. Only after admission should version commands run and be required to match 156.0.8078.80.

## Existing WPT route without installations

Use the existing Python environment and vendored WPT core directly. The inspected upstream Mach non-Gecko path explicitly installs pip requirements and redirects/creates product metadata; ordinary `wpt run` setup can also install components such as MojoJS. Those frontends are unsuitable for an installation-free experiment without further controls. The core `wptrunner.wptrunner.main()` parses arguments and runs the selected product without those frontend setup paths. `WPT-SOURCES.json` pins the inspected upstream bodies; exact local harness compatibility and existing dependency availability still require a read-only admission before execution. No dependency installation is proposed.

A minimal future launcher can add the repository's `testing/web-platform/tests/tools` directory to `sys.path`, import its `localpaths`, then invoke `wptrunner.wptrunner.main()` and return its exit status. Use the existing `/Users/bgrins/venvs/firefox/bin/python`, no new virtual environment and no pip. An import failure is an infrastructure blocker, not permission to install dependencies. A command template, after that launcher and private config exist, is:

```sh
/Users/bgrins/venvs/firefox/bin/python -B "$cft_runner" \
  --product=chrome --binary="$cft_binary" --webdriver-binary="$cft_driver" \
  --browser-version=156.0.8078.80 --headless --processes=1 \
  --no-enable-experimental --no-manifest-update --no-manifest-download \
  --config="$cft_config" --log-raw="$cft_output/raw.jsonl" \
  --binary-arg="--user-data-dir=$cft_profile" \
  --include=/css/css-animations/animation-duration-same-element-dependency.tentative.html
```

`cft_profile`, TMPDIR, outputs, server configuration and record directory must be fresh owned paths; do not point at a user's Chrome profile or attach to a pre-existing browser. [ChromeDriver's official capability documentation](https://developer.chrome.com/docs/chromedriver/capabilities) supports an explicit executable and isolated user-data directory. The inspected Chrome WPT backend provides .test host resolution, so this plan requires no /etc/hosts edit. It otherwise has testing defaults: explicitly disable its optional experimental-web-platform feature flags and retain actual browser arguments/capabilities. This is a WPT-controlled Chrome observation, not a claim of untouched interactive defaults. Keep browser sandboxing enabled.

Create a fresh private WPT config using the already executed single-page setup pattern, exact six sealed fixture/resource bytes and genuine manifest from PLAN.json, explicit test inclusion, and private metadata with no Firefox preference/expectation files. Retain the same-element receiver and its `DURATION_PROGRESS_RECORD_DIR`/`DURATION_PROGRESS_RUN_ID` environment contract, private 0700 record directory and two exclusive records. Use the existing server certificate/config facilities in owned paths; do not trust a new system CA. A root-owned process group/watchdog must contain server, driver and Chrome, capture raw/command/version/profile identities and stop only that group before cleanup. This document is a runnable recipe for a future owner, not an activated owner or a guarantee of successful dependency admission.

## Result boundary

Run the exact two callbacks, preserve their original assertions and both complete records, and separately report CSS expression support/calibration failures. Do not force experimental CSS flags to turn an unsupported Stable expression into a behavior result. Successful automation admission says nothing about animation timing. The acyclic same-element assertion has a still-qualified timing-source interpretation; the stepped self-dependent callback has no endpoint oracle. Compare actual timing/style/identity records with the frozen Firefox results without turning Chrome PASS/FAIL into a normative cycle policy. No cross-engine result exists yet.

The official [WPT documentation](https://web-platform-tests.org/running-tests/from-local-system.html#via-the-command-line) describes Chrome execution and machine-readable output. This plan bypasses installation-capable wrappers while retaining that core executor. `PLAN.json` remains disabled; actual downloads, signatures, harness admission and execution belong to a later reviewed root-owned operation.

Initial sandbox-only metadata/source requests encountered DNS errors (1a647a/cb097a); read-only escalated requests succeeded. All downloaded content in this package is text metadata/source, not executable browser assets.
