# Animated guaranteed-invalid publication review

## Verdict

**Accept the bounded native repair and 22-test regression fixture.** The original implementation republished a computed guaranteed-invalid custom value as CSS-wide `initial`. For a universal registration with a valid explicit initial value, these have different specified behavior. The candidate preserves the computed invalid value through animation publication and the cascade.

The normative oracle was derived before reading the proposed design or native patch. It combines universal registered computed values, explicit inheritance, variable fallback, computed-value animation, and effect composition. SOURCE-FIRST.md and authenticated primary excerpts retain that reasoning. Searchfox failed DNS resolution and webspec-index was unavailable; the retained original specification HTML and local source snapshots supplied the evidence.

## Evidence

- Original 16-test fixture: **10 FAIL / 6 PASS before**, **16 PASS after**. Failures reached the intended sampled-value assertions after registration, provider, effect-presence and progress calibration.
- Wider candidate run: **341 PASS / 2 unchanged expected FAIL**, 20 harness OK. Ten rows improve and 333 status/message pairs are unchanged. The comparison combines 16 contemporary baseline rows, 308 earlier fix-81 regression rows, and 19 historical animation calibration rows; it is not one contemporary 343-row baseline run.
- Reviewer-added controls: **6 PASS**, making the final fixture **22 PASS / 1 harness OK**. These test suppression of valid underlying declarations and lower animations, cancellation restoration, and valid empty tokens versus guaranteed-invalid fallback. The added six have candidate observations only.
- Dedicated WPT lint: **exit 0, zero problems**. Earlier sandbox-lock and unknown-command attempts are retained separately and did not run lint.
- Native review covers presence versus inner invalidity, cascade seen bookkeeping, inherited/non-inherited map removal and tombstones, shortcut handling, author parsing, ToCss skipping, and ToTyped rejection. No blocking defect was found in those paths.

## Packaging and independence

Both packaged patches contain exactly three native files and the identical final WPT. Their native hunks equal the reviewed native-only patch. Independent exact application of those hunks to authenticated upstream source snapshots reproduces the standalone package's three native files. Producer apply/reverse checks and preservation of HEAD/index are retained as producer receipts; this review did not execute Git operations.

The fixture's universal registration and direct unresolved-variable setup avoid relying on the earlier direct-inherit and non-universal keyframe-substitution repairs. This is source-path independence. Browser observations used the shared development tree; neither the isolated HEAD package nor isolated upstream package was built or run. Pending fix 81 is absent from the packaged patch, although present in the shared browser tree.

The compiled-to-landing change in properties/mod.rs was independently verified as exactly the recorded signature line wrapping and optional trailing comma restoration. The other two native files are byte-identical. The original baseline runtime omitted mod.rs from its pin dictionary; its bytes are separately authenticated from original source snapshots. Final candidate controls pin all three native files.

## Limits

This review establishes a concrete native bug, a scoped repair, browser regression evidence, and source-level packaging independence. It is not a general correctness proof of animation scheduling, dynamic registration, all enum consumers, or CSS. It provides no release-browser performance estimate. The two historical parent-mutation animation failures remain unresolved and unchanged.

## Reproduction

From the repository root:

```sh
python3 -I -S artifacts/css-animation-invalid-publication-review-v1/check.py . /private/tmp/animation-publication-runtime-review.json
python3 -I -S artifacts/css-animation-invalid-publication-review-v1/check_final.py . /private/tmp/animation-publication-final-review.json
```

These replay source hashes, raw runtime reconciliation, fixture preservation, formatter transfer and exact standalone native application. They do not launch browsers, build, or mutate native files or Git. Detailed findings are in NATIVE-REVIEW.md; final pins and evidence receipt hashes are in FINAL-REVIEW.json.
