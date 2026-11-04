# Local rollback regression controls

Prepared without browser execution or builds. This separate lane preserves the four historical controls and their exact resource bytes. Current live fixture bytes match the archived inputs; no live WPT, metadata or Git state was changed.

| Page | Observation required |
|---|---|
| `revert-rule-basic.html` | Four named callbacks PASS; harness OK |
| `revert-rule-custom-property.html` | One named callback PASS; harness OK |
| `revert-rule-cycle.tentative.html` | Two exact named historical failures; harness OK |
| `inline-style-revert-layer-crash.html` | Crashtest PASS; no callbacks or reference image |

`EXPECTED.json` contains exactly seven callback names. `POLICY.json` retains the historical event rows, failure messages and raw-log hash. The copied cycle metadata has exactly two FAIL entries:

- `Cycle between revert-rule !important and revert-layer resolves to unset instead of lower layers`
- `Multi-layer chain cycle with revert-rule !important resolves to unset instead of lower layers`

Both historically stopped at the first color assertion: expected green, observed red. The runner compares those exact failure messages too. A different failure, unexpected pass, missing callback, duplicate, new callback or failed crashtest cannot count as unchanged. The cycle callbacks do not establish results for their later assertions, which are not reached after the color failures. These expectations retain an unresolved specification issue; they do not redefine normative behavior.

Only `/resources/testharness.js` and `/resources/testharnessreport.js` are resource dependencies. The crashtest has none. `staged/wptrunner.ini` and both manifests are isolated; the private Mozilla manifest is empty. The historical Linux/Wayland crash timeout metadata is not copied: this local lane requires PASS. Unrelated directory preferences and allowances are not copied. `layout.css.revert-rule.enabled=true` is set explicitly for all four pages.

The interface matches the 80-callback runner:

```python
run(root: Path, output: Path, pins: dict, cancelled: Callable[[], bool]) -> dict
active_processes() -> tuple[int, ...]
```

Use the same fresh pins object as the corresponding 80-callback run: `execution_enabled: true`, `source_role: baseline|candidate`, relative `binary`, 40-character `build_revision` and `harness_revision`, and a `files` SHA256 map. Required entries are the executable, sibling XUL, application's `Contents/Resources/application.ini`, and all three paths in `SOURCE-ROLES.json`. The unchanged stylist hash keeps C separate. Source-to-binary provenance remains the owner’s responsibility.

Import under `python3 -I -S -B`, without optimization. CLI execution requires `--pins`, a fresh `--output` under artifacts, and `--execute`. Each run uses one headless process and a 180-second external deadline. Explicit cancellation, owned-group cleanup, temporary-directory identity, preserved source/application hashes and HEAD/index checks are inherited from the prepared 80-callback runner. Only staging/raw parsing and process cleanup helpers are imported; no old signing, restoration or build authority is used.

Assessment additionally checks the advertised suite roster, `suite_start.run_info.browser_build_id` against the pinned application's BuildID, and run-info revision against the pinned harness revision. It rejects abort events, nonzero/missing child process exit codes, assertion counts outside their expected range, harness errors and incomplete lifecycle. Raw events, full stdout/stderr, diagnostic event evidence, process identity, policy and cleanup remain in the output directory.

`complete_observation` records complete, preserved execution. `controls_unchanged` additionally requires the exact historical outcomes and failure messages. `all_pass` will be false for an unchanged cycle result. With the two explicit metadata expectations, an unchanged run should exit zero. A new failure or unexpected cycle pass is retained as a deviation, never silently accepted. `native_fix_acceptance` remains false; root owns the baseline/candidate comparison and review.

`CHECK.json` records browser-free manifest/source classification, exact name registration and negative assessment checks. `FILES.json` pins the package. No runtime observation is claimed by preparation.
