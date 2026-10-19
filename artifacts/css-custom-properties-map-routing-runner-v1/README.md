# Root-executed diagnostic runner proposal

This package has not executed a browser. It adapts the retained enumeration runner, adds exact nine-identity/harness checks, and requires a root-supplied existing-build receipt. `run.py` never builds, installs files, modifies native sources, or changes Git. Its Git commands are read-only. WPT creates ordinary generated runtime outputs when root executes it.

Root preparation:

1. Independently authenticate this package and the routing audit.
2. Verify that the completed combined build receipt binds the actual current binary to final combined map SHA `9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d` and relevant source files. Stop if another build/browser task owns the shared outputs.
3. Install the exact retained HTML at `testing/web-platform/tests/css/css-values/map-taint-equality.html`. No test is installed by this proposal.
4. Execute with a new output directory:

```sh
python3 -I -S artifacts/css-custom-properties-map-routing-runner-v1/run.py --repo /Users/bgrins/code/firefox --build-receipt /ABSOLUTE/ROOT/COMBINED-BUILD-RECEIPT.json --output /ABSOLUTE/NEW/RESULTS
```

The runner explicitly enables the existing `layout.css.properties-and-values.enabled` preference. No `layout.css.attr` preference exists in the inspected source. The directory's existing random-function preference is retained and pinned; this test does not use random functions. Actual `<string>`, `attr()` and image-set support are calibrated by per-case computed-value and literal-image prerequisites, never silently skipped.

A diagnostic run may legitimately exit WPT 1 and return FAIL rows. The runner accepts only the nine named PASS/FAIL results plus one harness OK and one suite end. Raw rows, messages, console output, hashes and source/build-receipt associations are retained before terminal validation. Expected values come from the test's normative oracle; no predicted failure count is hard-coded.

Static validation performed here: Python AST parse and exact HTML/JS identity checks only. CLI execution, browser output grammar and source-to-binary binding require root execution/review. No success is inferred from preparing this runner.
