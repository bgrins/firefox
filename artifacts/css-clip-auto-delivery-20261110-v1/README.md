# Standalone clip-auto delivery

`delivery.patch` contains exactly five files, pinned to `0dcfe7c2e7a8cd9924894449dd1d97d3c604d79c`. It is ready for root to apply after the preceding research commit. No live source, test or Git state was changed while preparing this capsule.

| File | Delivered change |
| --- | --- |
| servo/components/style/properties/helpers/animated_properties.mako.rs | Let matching auto rectangle components participate in ordinary CSS Add/Accumulate. |
| servo/ports/geckolib/glue.rs | Preserve existing SMIL auto-rectangle rejection through explicit AddForSMIL/AccumulateForSMIL exports. |
| dom/smil/SMILCSSValueType.cpp | Call the renamed SMIL-only exports; preserve zero finalization and wrapper ordering. |
| testing/web-platform/tests/web-animations/animation-model/keyframe-effects/clip-auto-composition.html | Exact approved nine-case WPT, unchanged from the runtime candidate. |
| testing/web-platform/meta/web-animations/animation-model/keyframe-effects/effect-value-iteration-composite-operation.html.ini | Remove only the mixed-clip expected-failure stanza. |

The removed metadata is exactly:

```ini
  [iteration composition of incompatible clip rects (accumulation skipped at 0%, allowed at 50%)]
    expected: FAIL
```

The adjacent blank separator is removed with that stanza. The existing calc-size/align-content failures and Android fission timeout expectation remain byte-identical. No SVG diagnostic, model, proof, wrapper or research document enters this standalone delivery patch.

Suggested subject: `Fix additive animation of clip rectangles with auto components`.

## Review and validation

The three native candidates are byte-identical to the reviewed, built candidate. The C++ aCount continuation is deliberately unchanged: rerunning the installed repository clang-format with the real source filename produces exactly these bytes. FORMAT.json records the formatter and check; no manual alignment override is needed. The nine-case WPT is the already-approved/linted fixture. Source applicability is checked against pinned Git objects, not a transient live build tree.

Root's completed optimized candidate run reports the four intended CSS FAIL→PASS improvements (three new cases and the existing clip case), unchanged other callbacks and twelve unchanged SVG observations. Native compilation succeeded and the runtime wrapper restored source/app/extras and removed its backups. RUNTIME-RECEIPTS.json binds those receipts; the independent [runtime review](../css-clip-auto-runtime-review-20261110-v1/REPORT.md) also replayed the raw callback comparison with assertion and harness records kept distinct. Debug was not run; the source-specific [gate reassessment](../css-clip-auto-candidate-review-20261110-v1/GATE-REASSESSMENT.md) explains why the bounded optimized gate is sufficient here. The separate missing-pseudo CSSOM debug requirement is unaffected.

`python3 check.py --check-git` validates the four existing source files, new-test absence at the basis, five exposure-context sources and complete five-file forward/reverse scratch patch replay. It also verifies that the metadata delta is precisely the one stanza. Root should rerun the final test/metadata lint checks on the concrete delivery before signing; this capsule does not mutate the live tree to do so.

## Exposure and relative priority

Recommend catalogue **#171, tier C**: a narrow visual/computed-style arithmetic error involving the deprecated clip property and matching auto rectangle components under additive effect or iteration composition. The four passing regression callbacks describe one shared native root cause, not four separate bugs. No memory-safety or security impact was established.

Do **not** describe iteration composition as preference-gated based on this checkout. Pinned KeyframeEffect.webidl exposes KeyframeEffect on Window, with iterationComposite/composite options and attributes carrying no Pref guard. BaseKeyframeTypes exposes add/accumulate choices. KeyframeEffectParamsFromUnion copies both options directly; their setters apply them without a preference check. The clip longhand entry has no enabled-pref restriction. The bounded StaticPrefList lookup found no matching animation-composition gate. These source facts support normal web-content reachability in this pinned implementation; they do not establish behavior or support in any particular released Firefox version.

CSS Masking calls clip deprecated in [Appendix A](https://drafts.csswg.org/css-masking-1/#clip-property); the previously captured primary-source section is retained as clip-appendix.md. Narrow feature scope, rather than an unsupported preference assumption, justifies the relative tier. No new release-browser measurement was performed for this delivery plan.

After the standalone fix is accepted and committed, catalogue #171 should increase the recorded total from169 to170 entries, counting held #160 and excluding #120. That accounting is separate from a claim that every entry is a landed fix. Root owns the catalogue update and commit hash; this capsule does not increment the count before delivery.
