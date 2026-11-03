# Isolated archived-original fallback-taint WPT runner

This disabled preparation runs only the sealed standalone 24-case `attr-fallback-taint.html` against the retained original application `/private/tmp/css-original-e86-browser-1wxwyapk/Nightly.app`. Its native source role is original HEAD e86b64866cdc5e2260ba9be08c45756fd96e21bb, build ID 20261102193406, as recorded by `css-original-e86-browser-snapshot-v1`. It is neither a fresh build nor the current integrated candidate.

## Isolation

`run.py` imports the executed pair's exact `wpt.prepare_inputs` helper, then replaces its live-object-directory run-info and preferences references with owned copies. It invokes the installed WPT virtualenv's Python directly through a short `entry.py` bootstrap and the genuine `wptrunner.main`. It does not invoke Mach, resolve a current build binary, build/update a virtualenv, install fonts, update/download manifests, or access Git/index/canonical state. The retained `mach_commands.py`/`mach_commands_base.py` source trace confirms that normal Mach setup supplies mutable dist defaults; this runner avoids that setup entirely.

Staged tests, both manifests, metadata, server config, run-info, preferences, certificates and specialpowers are under the new runtime directory. `mozinfo.json`, profile defaults, certificate files and specialpowers were copied into this preparation and pinned. Browser and certutil paths both point into the archived application. The existing repository WPT tools directory is read through the same tools symlink as the established pair runner; Python bytecode writes are disabled. No dynamic dist/stackfix/symbol/GMP path is supplied. All server protocol ports are `auto`, and DNS/WebTransport are disabled for this ordinary HTTP testharness page. The CLI explicitly disables single-test pause and browser preloading.

A fresh owned `/private/tmp/css-attr-fallback-original-*` directory supplies TMPDIR/TMP/TEMP for WPT's temporary profile and server work. The harness starts in a new process group. Existing executed `process_control.terminate` terminates/reaps only that group and requires its absence; the exact temporary directory identity is rechecked before cleanup. The archived application is retained, not removed. Runtime artifacts and raw PASS/FAIL events are retained.

Before and after execution, `archive()` rehashes all 8,326 application files, compares exact path set, sizes and modes with the snapshot, rejects symlinks, and authenticates the original build receipt. Input/support/helper pins are rechecked, and all initially staged regular files plus the tools-symlink target must remain unchanged. Verification failures remain in RESULT. An incomplete/crashed test is not accepted as a complete observation. No all-branch current-state snapshot or fabricated research receipt is used.

## Results and expected discrimination

The assessor requires all 24 exact unique callback names, the single correct page ending with OK, and one suite start/end. PASS and FAIL are retained individually. A prediction of 15 PASS / 9 FAIL is recorded separately and never gates observation completeness; 24 PASS is also accepted as a complete observation. TIMEOUT, CRASH, duplicates, wrong names/pages and missing endings remain failures. A WPT process exit of 1 is allowed only with complete PASS/FAIL observations and successful preservation/cleanup. No native-fix acceptance is asserted.

## Preparation validation

Actual 00f4ef/0 stages the inputs in owned scratch, validates the real WPT parser/argument path without starting a server or browser, checks two synthetic complete streams and seven incomplete/wrong/duplicate streams, and proves the disabled gate rejects before archive reads. Scratch was removed. Actual 0c34f1/0 imported the genuine WPT entry and printed help. No application binary, certutil, native build, live WPT, or browser was executed by these checks. The archived application itself is authenticated by root's recorded snapshot and will be revalidated by root's eventual --run.

REFERENCES pins the fixture/manifest/roster, original snapshot and manifest, staging/control helpers, copied support, and inspected WPT/Mach entry sources. The direct-entry import path uses the existing installed WPT virtualenv and vendored Python modules; this is the same local harness environment, not a claim to package every Python dependency hermetically.

## Root-only execution

POLICY execution_enabled is false. Root may preserve the disabled preimage, review/reseal activation changing only that boolean, and invoke:

```
python3 -I -S -B artifacts/css-attr-fallback-archived-original-runner-v1/run.py --run > artifacts/css-attr-fallback-archived-original-root-run-v1.log 2>&1
```

The fixed new runtime is `artifacts/css-attr-fallback-archived-original-runtime-v1`; exclusive creation refuses reuse. No execution or result is implied by this preparation. The active integrated pair and all its source, fixtures, application, metadata and owners remain untouched.
