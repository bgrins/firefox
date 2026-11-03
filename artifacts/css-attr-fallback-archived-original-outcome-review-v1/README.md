# Archived original: attribute fallback taint outcome

The exact standalone 24-callback WPT produced **15 PASS / 9 FAIL**, with its page ending **OK**, on archived original native HEAD `e86b64866cdc5e2260ba9be08c45756fd96e21bb`, build ID `20261102193406`. This independently reproduces the targeted fallback behavior in the source-bound original application. It is not a candidate run, a fresh original build, or native-fix acceptance.

The failures are the same three own-fallback cases in each of direct, unregistered-custom and registered-string-custom substitution:

| Case | Direct | Unregistered | Registered |
| --- | --- | --- | --- |
| Missing raw attribute, literal fallback | FAIL | FAIL | FAIL |
| Invalid typed primary, literal fallback | FAIL | FAIL | FAIL |
| Missing typed attribute, literal fallback | FAIL | FAIL | FAIL |
| Literal image | PASS | PASS | PASS |
| Successful raw primary | PASS | PASS | PASS |
| Successful typed primary | PASS | PASS | PASS |
| Literal var() fallback | PASS | PASS | PASS |
| Nested attribute fallback | PASS | PASS | PASS |

Every failure reaches the final URL-taint equality assertion: it expected `none` but observed the valid data-URL image-set. Thus each failed callback first passed its standards-mode, syntax, target parsing and literal-image controls. No network-secret or broader exploit conclusion follows; the page uses only its fixed data URL.

## Independent saved-result checks

Read-only review actual 43a9ca / session 64189 / terminal 97cd22 / exit 0 verified:

- Exactly one expected page test_start, all 24 exact names once, one OK page ending, one suite_start and suite_end, in the proper order.
- Zero explicit crash events and zero ERROR/CRITICAL log events. Actual status counts and full subtest/end records match the saved assessment.
- WPT process exit 1 is retained. Runtime RESULT success means complete observation plus preservation/cleanup, not that failing tests passed. The prediction was recorded separately, not used to waive failures.
- All 8,326 current archived application files still match the snapshot's exact content hashes, sizes and permission modes: 819,801,859 bytes, no symlinks. The canonical digest equals both saved archive PRE and POST. The source-bound original build receipt hash, three source pins and raw run-info build ID join exactly.
- All 47 initially staged regular files and the exact six staged subtree maps still match; the tools symlink points to the expected harness source directory.
- CLEANUP records owned process-group absence and temporary-root removal. The exact temporary directory is independently absent now. This review did not perform a separate live process census; root's independent audit remains distinct authority.

The outer owner terminal/session was not present among the runtime records when reviewed and is not invented here. The observed WPT exit and runtime RESULT are directly authenticated. No browser, certutil, native build, owner execution, Git/index/canonical mutation, or live source edit was performed by this review.

`review.py` contains the bounded saved-stream and read-only file checks; `REFERENCES.json` pins the actual inputs. `OBSERVATIONS.json` retains exact counts and authority distinctions. Candidate validation against the standalone patch is still pending and must use its exact new source bytes; the separate active integrated pair is not candidate evidence for this fix.
