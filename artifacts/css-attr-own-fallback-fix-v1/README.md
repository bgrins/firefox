# Attribute fallback taint: standalone candidate

A successful fallback returned by `attr()` is still a value produced by `attr()`. This candidate changes only the legacy `substitute_one_reference` fallback tail: after successful fallback substitution, OR its existing taint with whether the reference is `Attr`. It preserves taint already introduced inside a `var()` or `env()` fallback, leaves literal `var()` fallbacks untainted, and keeps unsuccessful substitution as `Err(())`.

The captured base is `servo/components/style/custom_properties.rs` from actual Git HEAD `e86b64866cdc5e2260ba9be08c45756fd96e21bb`. `native.patch` contains exactly that Rust modification and the new `testing/web-platform/tests/css/css-values/attr-fallback-taint.html`. Research, validation helpers, captured sources, and logs are not native commit payloads. No live source or WPT was installed; no native build, browser run, Git/index mutation, or signing was performed for this candidate.

## Oracle and coverage

The [current replacement algorithm](https://drafts.csswg.org/css-values-5/#replace-an-attr-function) returns the selected fallback as the result of the attribute substitution. The [attribute security rules](https://drafts.csswg.org/css-values-5/#attr-security) taint values produced by `attr()`; the [image-set string alternative](https://drafts.csswg.org/css-images-4/#image-set-notation) represents a URL. An attr-tainted string used there invalidates the declaration at computed-value time. The isolated background-image therefore computes to `none`.

The sealed `css-attr-own-fallback-taint-spec-review-v1` retains the detailed algorithm trace and prior-art search. It found no own-literal-fallback exemption. The independently executed System Firefox 158 probe in `css-attr-own-fallback-browser-probe-v1` recorded nine mismatches and 15 matching controls; all 24 literal image controls remained valid. That browser observation is not a source-bound execution of this candidate.

The WPT has 24 callbacks: eight cases across direct substitution, an unregistered custom property, and a registered `<string>` custom property. The three targeted fallback cases are a missing raw attribute, an invalid typed primary, and a missing typed attribute, each with a literal string fallback. Controls cover literal image strings, successful raw and typed primaries, a literal `var()` fallback, and a nested attribute fallback. Every callback independently checks literal image validity and target parsing. Only data URLs are used. Each callback owns a fresh standards-mode iframe; registration uses `CSS.registerProperty` instead of the System probe's `@property` rule, with equivalent registered syntax/default/inheritance.

Expected source-bound discrimination is original nine failures / 15 passes and candidate 24 passes. This remains an expectation until root executes both source-bound roles. This is a taint-policy correctness test, not a claim of external requests, secret disclosure, or a demonstrated broader security impact.

## Completed validation

- Genuine installed upstream WPT `check_path` and `check_file_contents`: zero findings, actual 23c337/0. A genuine Manifest v9 has one testharness page with explicit `timeout: long`.
- Inert Node registration captures 24 unique callback names; it does not execute DOM test bodies. One page ending gives 25 expected signatures per role.
- Exact forward/reverse two-file patch roundtrip with zero fuzz and no offsets: ebba18/0. Both scratch trees from staging and roundtrip were removed.
- Rustfmt using the repository's Servo configuration: 8ca5a7/0. The first check 624f4c used the default configuration and rejected pre-existing match-arm commas; its log is retained. No reformatting was applied. Initial abbreviated `git show e86b` was ambiguous (c6afb4/128); the subsequent actual full HEAD capture succeeded (11b245/0).

`SOURCE.json` identifies the exact base/candidate/test hashes. `INPUTS.json`, `MANIFEST.json`, and `ROSTER.json` support a future root-owned source-bound pair. Validation uses only owned scratch; it is not the complete repository lint suite or a native typecheck.

## Experimental continuation remains separate

The retained prototype's `invalid_primary` builds a fallback chunk, and its `Fallback` completion arm currently forwards the result without adding the outer attribute's taint. The corresponding future change must OR taint onto a successful selected fallback result when the waiting reference is `Attr`, before forwarding it to its parent or terminal result. Preserve existing nested taint for every reference kind, keep unsuccessful fallbacks unsuccessful, and avoid modifying unused fallback branches. This standalone patch does not modify or import that prototype.

Separately, the source author has identified an empty successful-value aggregate-taint loss in the experimental terminal representation. That is a different path and requires its own preservation change and tests; this fallback patch makes no claim to solve it. The live integrated experiment and its 63-case roster remain immutable.
