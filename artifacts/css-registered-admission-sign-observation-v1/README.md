# Selected sign dependency observations

This browser diagnostic records 24 cases and 48 snapshots from the sealed sign-cases package. It covers number and length-or-number registrations, direct and unregistered-provider input, positive/zero/negative `sign()` operands, and fixed-font/self-font consumers. Every registration error, specified declaration, computed custom property, raw provider, font size, line height and width is retained. There is no conformance oracle for the disputed cycle behavior.

Run only after the corresponding complete, preserved WPT phase from the bound capsule, using exactly its compiled epoch and browser. The candidate requires the original observation result and compares complete rows. Any changed row is reported. A zero exit means complete preserved capture; it does not accept a native repair. Review registration errors explicitly: identical setup failures are not evidence that the cases worked.

The runner derives from the signed self-font observer. The delta changes the owned output prefix, removes the unused iframe route, and adds frozen-HEAD and six unchanged-collector-source checks before and after execution. All source/index/nested-repository, binary, application metadata, capsule/reference authentication, owned process/profile/server cleanup and externally bound epoch checks remain. The separate default profile does not import WPT preferences. Top-level user-agent text is retained but not treated as a CSS behavior comparison; query order is fixed and validated.

Invocation, with externally verified digests and absolute evidence paths:

```
python3 -I -S -B artifacts/css-registered-admission-sign-observation-v1/run.py TOOL_SHA original-1 EPOCH_PATH EPOCH_SHA WPT_ASSESSMENT WPT_SHA ABSENT_OUTPUT
python3 -I -S -B artifacts/css-registered-admission-sign-observation-v1/run.py TOOL_SHA candidate-1 EPOCH_PATH EPOCH_SHA WPT_ASSESSMENT WPT_SHA ABSENT_OUTPUT ORIGINAL_RESULT ORIGINAL_SHA
```

Outputs must be under `artifacts/css-registered-admission-sign-runtime-`. The observation process is deliberately terminated after capture; the result distinguishes that cleanup from a natural browser failure. Native sources, live test files, metadata, indexes and the epoch are never written by this runner.

The validator rejects missing, duplicated, reordered or malformed cases/snapshots and detects changes to each captured actual-value field and registration errors. These are synthetic assessment checks, not browser evidence. Independent review found no concrete blocker in the runner delta or validator; the original/candidate browser runs remain pending at preparation time. Neither this artifact nor a successful observation adds accepted-bug or formal-coverage credit.
