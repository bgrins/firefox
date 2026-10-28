# Counter rollback landing payload

Use the exact ordinary v3 page for the standalone landing payload, alongside the unchanged registered20 page. Keep ordinary v4 as a stronger experimental preservation page on this branch. No running or sealed fixture was modified by this review.

The ordinary v3 successful number line-height control asserts the specified random key equals explicit `ua-line-height-1`. This directly checks the parser contract before the independent line-height computation bug. Ordinary v4 additionally reads the reference computed value, requires it to be at least 10px, and compares target and reference computed values. That positive reference assertion requires fix141: before that fix, both contextual number values can incorrectly compute to zero. Merely retaining computed equality without the positive reference assertion would introduce a vacuous zero-equals-zero control, so it is not a stronger counter-specific replacement.

CHECK.json establishes that removing exactly those three lines and restoring the specified-only test name reproduces the sealed v3 page byte for byte. The other25 callbacks remain unchanged. The landing page therefore still has26 tests, and registered20 remains20:46 target tests in total.

## Concrete payload

Preserve the exact four-source native v4 patch (parser.rs, properties/shorthands.rs, properties_and_values/value.rs, values/specified/calc.rs), with these two standalone test files:

- `testing/web-platform/tests/css/css-values/random-typed-parse-rollback.html`: exact ordinary v3 body.
- `testing/web-platform/tests/css/css-values/registered-random-alternative-indices.tentative.html`: exact registered20 body, relocated from its artifact API-directory origin without changing its content.

Both belong under css-values so the existing directory random-feature metadata applies. The API-directory origin did not inherit that setting. Preserve the actual captured metadata/pref scope in validation rather than treating random support as a universal default or adding a silent unsupported-feature skip. The six-path native-plus-tests payload does not include font.rs, the two line-height141 pages, or any held provider prototype.

## Other prerequisite checks

The remaining line-height callbacks use Length-valued random inputs and fixed lengths. They follow the existing Length conversion path, rather than the contextual Number mapper repaired by141. Registered tests use scalar/list Number custom values and opacity references; they do not compute number-valued line-height. Their literals, fixed/named/property keys, rejected alternatives and trailing-entirely rejection remain unchanged. No relative units, contextual initial values, typed-attribute provider logic or CSS-wide scheduling is introduced.

The ordinary opacity/filter/border-image/gradient/rotate callbacks compare deterministic specified keys and same-key computed values. Grid callbacks use fixed pixel track ranges and the five explicit longhand comparisons; they do not use contextual repeat/subgrid counts or held integer/easing work. No additional unnecessary prerequisite was identified in these two pages during this bounded inspection. The implementation changes only parser-side transaction boundaries and does not call the accepted line-height mapper.

This is a source-and-assertion dependency audit, not a proof that the four-source patch compiles or all46 tests pass on an arbitrary historical/upstream revision. Existing random syntax/cache-key support and the relevant parser APIs remain necessary platform prerequisites. Do not claim clean-upstream cherry-pick validation from branch-only execution.

## Evidence and next validation

The running paired experiment uses ordinary v4. If it passes, its stronger number control entails the retained v3 specified-key assertion; the other25 ordinary callbacks and registered20 are identical. Record this as a justified assertion projection, not an execution of the exact landing bytes. Final promotion should install and run the exact two landing pages, with unchanged native source and appropriate existing regressions. No additional native build is needed solely for this test-body selection if the native/binary evidence remains valid. The current experiment is still live; this report assumes no outcome.

The independent additional-caller audit received bounded clearance668010/078e78 after its seal; b83ff1 was an overly specific lookup failure, not a finding. That review does not establish parser-family closure. Neither this payload recommendation nor the source audit allocates a new fix ID or claims acceptance.
