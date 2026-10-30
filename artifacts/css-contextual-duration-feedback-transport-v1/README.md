# Feedback observation transport

This transport-only successor overlays the measurement page from regression-plan-v2 and adds one WPT Python handler. All three callback names, their inputs, eight-sample loops, sequential reads and existing assertions are unchanged. The inserted fetch occurs after the complete sample loop and retained in-page JSON update. It awaits a successful JSON acknowledgement before the callback's existing completion assertion. No request occurs during a callback's samples. No browser, WPT HTTP server or native code was executed here.

The server handler follows the executed Round record.py pattern: owner-supplied environment selects private output, a POST carries complete observations, exclusive creation prevents overwriting an earlier record, and only a completed write is acknowledged. The extension adds allowlisted kinds, shape validation, directory/run binding and exclusive per-kind files. REFERENCES.json pins both the prior measurement package and the Round handler sources; it does not claim the extended handler was previously browser-executed.

## Owner contract

Before the feedback WPT phase, the root-owned runner creates an otherwise empty private 0700 directory, records its identity, and supplies these variables to the WPT child/server environment only:

- DURATION_FEEDBACK_RECORD_DIR: absolute directory path, owned by the server user, not a symlink.
- DURATION_FEEDBACK_RUN_ID: fresh owner identifier matching [A-Za-z0-9_-]{16,128}; secrets.token_hex() is suitable.

Serve this exact page and duration-feedback-record.py together under /css/css-animations/. The page POSTs {kind,samples}. The handler maps only these existing labels to fixed filenames:

| Kind | File | Effects per sample |
| --- | --- | --- |
| self font | self.json | 1 |
| coupled font and opacity | coupled.json | 2 |
| zero-start self font | zero-start.json | 1 |

Each output is {run_id,kind,samples}; samples has exactly eight entries. Sample keys are font, cssDuration, opacity, effects, repeatFont and repeatDuration. Effect keys are name, time, duration, progress and state. CSS strings and all recorded values are preserved. Time/progress accept numbers or null; duration additionally accepts strings. There are no finite-duration, positivity, convergence, identity, timing-value or fixed-point assertions in this transport. Non-JSON numeric tokens are rejected as protocol errors; JavaScript JSON.stringify converts nonfinite numeric observations to null, which the handler accepts. No interpretation is reconstructed from null.

The response is JSON {run_id,kind,sampleCount:8}. The page checks success, kind, count and a nonempty owner identifier; the runner must independently require the exact generated run ID in every persisted envelope. The browser does not supply paths or select output directories. Files are created with O_EXCL and mode0600 using a verified directory descriptor; duplicate submissions, existing files or symlinks do not overwrite prior evidence. A write failure has no success acknowledgement; the owner must retain/report any partial record as failure rather than retry against the same output.

After the complete phase, the owner requires exactly the three files, regular files with expected identities/modes, correct run ID/kind and eight sample shapes. It should save their hashes in FEEDBACK-RECORDS.json alongside the actual raw WPT results and unchanged-state/restoration evidence. Successful callback status without these records is not sufficient measurement evidence. An external watchdog remains necessary because JavaScript cannot interrupt a wedged synchronous style flush. This package provides no executable owner or automatic retry.

## Static validation and scope

check.py removes precisely the inserted transport block and requires equality with the sealed V2 page. It inertly registers the same three names, generates a genuine WPT manifest using the unchanged V1 capture plus this page/helper, and lints both new files. It exercises the handler directly in owned temporary directories: three successful round trips preserve differing repeated CSS values and nullable/string effect fields; 19 negative cases reject duplicates, unknown/path-like kinds, wrong counts/keys/types, wrong method, oversize/malformed/non-JSON bodies, bad run binding, relative/nonprivate/symlink output directories and an existing target symlink. Prior evidence is unchanged in every rejected case. Scratch is removed. The scratch manifest tool's Git-directory diagnostic is retained in check.log; no Git repository or index is created.

Actual static check d02f8b/0 passed. These are isolated handler calls, not a live HTTP or browser transport claim. The real owner still must confirm WPT server environment propagation and three acknowledged records. The first two observational cases and the zero-start model-derived period-two hypothesis retain all limits documented in regression-plan-v2. No numerical oracle, native patch, fixed-point claim, acceptance credit or iteration cap is introduced.
