# Empty-mask composition: SVG connection

## Scope

This companion separates three kinds of evidence:

1. Kernel-checked Lean theorems over exact rational alpha and arbitrary finite layer lists.
2. Finite source-extracted native execution using explicit providers for rendering and resource outcomes.
3. Prior browser/native review, identified in PROVENANCE-v2.json but not rerun by this package.

The reusable algebra is independent of SVG. The native connection in this package is only for SVG area-empty classification and multilayer dispatch. The separately identified CSS image zero-size path is not connected here.

## Mathematics

`Mask.lean` defines source-over, source-out, source-in and xor alpha equations using Lean's exact Rat. Thirty-six named theorems cover empty-source no-op/clear laws, nonzero counterexamples to skipping a clear, equivalence of the optimized per-layer operation and arbitrary finite folds, substitution under any finite prefix/suffix, prefix erasure after clear, later-layer recovery, bottom-operator override, distinct failure outcomes and optional output initialization. The identities hold for arbitrary Rat values; physical alpha in [0,1] is a subset. No claim of interval-preservation or floating-point/raster equivalence is made.

`empty_in_arbitrary_stack`, `noop_in_arbitrary_stack`, `clear_erases_prefix` and `later_layer_recovers` quantify over arbitrary lists. They do not merely enumerate bounded examples. The model treats resource failures according to the existing native skip behavior; this is an implementation-preservation contract, not a claim that every historical failure policy is normatively correct.

The checker prints every theorem's axiom dependencies, disallows custom `axiom`, `sorry`, `admit` and `unsafe` declarations, and rejects sorryAx/Lean.ofReduceBool dependency reports. Ordinary kernel/library axioms such as propositional extensionality are reported, not hidden. Executable Lean fixture values are additional finite code evaluation, separate from theorem checking.

## Native source boundary

`bridge.py` authenticates complete original/candidate source files, then extracts without edits:

- complete SVGMaskFrame::GetMaskForMaskedFrame;
- complete PaintMaskSurface;
- the MaskParams definition/constructor and exact method declaration;
- GetGFXCompositeMode from nsCSSRendering.h.

Original source comes from the original-build snapshot retained by root. Candidate source is the reviewed formatted native patch. Extraction authenticates enclosing complete files, preventing unnoticed adjacent source drift. The generated production snippets are verbatim. The source-only package also retains its providers and executable fixtures so reviewers can inspect what is abstracted.

`adapter-prefix.cpp` supplies resource outcomes, drawing interfaces, style providers, geometry and child painting. It is not a copy of Gecko's full renderer. Reference validity, actual mask-area calculation, allocation/IsValid, child pixels, luminance conversion, snapshot success, SVG transforms, real clip stacks, SVG observers, frame lifetimes, image-resource dispatch and backend behavior are provider assumptions. Child input is zero or one white-mask contributor with an exact dyadic alpha; it does not model general child graphics, blend operations or color conversion. Matrix/rectangle traces preserve command arguments and restoration, but do not implement real transformed rasterization. The real API's clip/offset behavior is supported by the independent native/WPT review, not proved by this adapter.

`adapter-suffix.cpp` exercises the callee directly with present/absent output pointers and both prior bool values, and exercises complete caller loops. The callee state matrix covers reference rejection (including a simultaneously empty area), successful empty area, allocation null, invalid allocated target, snapshot/luminance failure and success. Alpha, luminance and match-source are included, with mask type, linearRGB setting, child absence/presence and opacity controls. Empty area precedes allocation; reference rejection precedes empty area.

Caller fixtures cover all four operators, the ignored bottom operator, arbitrary initial destination values, empty/failed middle layers and subsequent surface layers. Target origins include positive, zero and negative coordinates; initial transforms include nonidentity positive/negative translations. The exact source issues GetRect, identity, clear and restoration commands; the trace oracle checks those arguments/order. All caller fixtures select SVG masks. The complete CSS image branch is compiled but its provider is opaque and its runtime semantics are excluded.

Native finite arithmetic uses exactly representable dyadic double inputs and short stacks. Its 4,320 fixtures per variant and 4,320 Lean values are compared with an independent Python Fraction oracle. This supports the observed native paths within those inputs; it does not establish arbitrary floating-point equivalence. Undefined-behavior and implicit-truncation sanitizers are enabled for capsule execution. Provider allocations intentionally live for the short process; this is not a native ownership or leak proof.

## Negative controls and replay

Native semantic mutations must compile and execute normally, then fail the expected values or operation traces. They remove classification/initialization/clearing, conflate failure with empty area, swap operators/bottom behavior, lose target origin/transform restoration, stop later composition, or alter the source operator mapping. A compiler error does not count as detecting a semantic mutant.

Lean semantic mutations change the mathematical operation, failure behavior or bottom override and must be rejected by proof checking. Separate diagnostic controls exercise missing provider API/imports, prohibited admissions and source identity failures. Failed development/preflight attempts are preserved separately and are not counted as successful acceptance.

Run:

```
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-empty-mask-composition-proof-v2/check.py --out /private/tmp/empty-mask-replay-UNIQUE
```

The output directory must not already exist. The default runs all proofs, examples, original/candidate native extraction and mutation controls. `--skip-mutations` is available only for development and produces empty mutation lists; it is not a full acceptance receipt.

`REPLAY-INPUTS-v2.json` pins semantic replay inputs. `tooling-paths-v2.txt` lists the source-only companion files; generated binaries, logs, fixture exports and preflight directories are excluded from that list. The selected xcrun clang++ path, resolved executable hash, explicit SDK and SDKSettings hash are recorded. Preserving the clang++ driver basename is necessary for automatic C++ library linking. Lean binary/version is pinned too. This is not a hermetic compiler/SDK/Lean standard-library distribution.

## Limits and provenance

The browser fix's independent review accepted two 80-cell baseline/paired reftests and the added 16-cell partial-alpha three-layer transform/clip equivalence test. This package cites that review as historical provenance only. It makes no new claim about release performance, all GPU/backends, external-resource timing, arbitrary SVG documents, singular transforms, mixed image stacks or all CSS masking. The mathematical layer model can be reused for an image-path fix only after that path receives its own source binding, tests and review.

## Version 2 correction

Independent review rejected the v1 native capsule: its direct callee fixture passed a temporary Matrix to MaskParams, which stores a const reference. The temporary expired before the call. Matching values and the earlier UBSan run did not make that execution valid. V1 remains historical rejected evidence; v2 replaces it for native acceptance.

The v2 fixture declares Matrix userSpace before MaskParams and keeps it alive through the callee invocation. A separate compiler diagnostic annotates the extracted constructor's matrix argument with clang::lifetimebound: the named-matrix variant must compile, while restoring the exact old temporary fixture must fail with a dangling-temporary diagnostic. This annotation is limited to diagnostic copies; the ordinary native snippets remain verbatim. It is not a general ownership proof. AddressSanitizer could not start even for an empty program outside the sandbox, so its timeouts are recorded only as an infrastructure limitation, not successful lifetime detection.

Independent review also found that the missing-initialization mutant made the native caller read an uninitialized bool on failure paths. V2 runs that mutant only over the 2,304 direct callee fixtures, where the harness initializes the bool to both prior values. Every other semantic mutant uses all 4,320 fixtures. The receipt records each mutation's selected input count and mismatch count; compiler diagnostics do not count as semantic mismatches. The mathematical model and native source snapshots remain unchanged.
