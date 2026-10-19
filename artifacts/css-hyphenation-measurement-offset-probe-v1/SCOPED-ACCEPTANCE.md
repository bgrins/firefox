# Measurement coordinate repair

The word boundary is an absolute text-run offset. Comparing it with the length
of the old hyphen buffer mixes absolute and relative coordinates. Compare it
with the next buffer's absolute start instead, preserving rescanning after a
later chunk changes the classification of hyphenation opportunities.

## Accepted evidence

- The paired browser run fixes two failures; all eight new checks pass.
  Nineteen existing reftests pass and one expected failure is unchanged.
  Only gfxTextRun.cpp and the two browser binaries differ between runs.
- The exact source change and WPT apply/reverse at current HEAD and the original
  base. The whole file at HEAD matches the browser candidate; the historical
  base lacks an independent signed-ligature repair outside this method.
- Root's fresh relocated source replay rebuilds the complete baseline native
  harness and both candidate provider variants with UBSan. Both reproduce the
  two changes among 16 retained fixtures and preserve all 40,608 controls.
- The constructor/reachable-state guard proof passes 31 modules / 289 theorem
  reports, including ten new guard-admission lemmas. It derives the buffer
  coordinate relation from the model's storage invariants and provider lengths.
- The recorded Firefox build succeeds. Targeted lint reports zero errors and
  one ignored-WPT ESLint warning.

`ROOT-SCOPED-ACCEPTANCE-v1.json` identifies the exact receipts and patch. Keep the
source/proof companion before the two-file native/WPT commit.

## Replay

The canonical closed source capsule is
`../css-hyphenation-coordinate-companion-v3`. It contains 444 authenticated
inputs plus its manifest and freeze. From the Firefox repository root:

```
python3 -I -S -B artifacts/css-hyphenation-coordinate-companion-v3/check.py \
  --manifest-sha fb3ece607d89bb1524bcf7dc8ee5b630bed41351ea1d46972d4bb50ccbf59ec2 \
  --lean /absolute/path/to/lean-4.35.0-rc4/bin/lean \
  --output /new/output/directory
```

Pinned Xcode Clang/SDK/libc++, system ICU and Lean are external dependencies.
The root replay used a fresh relocated copy, with no generated input artifacts.
V1 failed because of inherited working directories. V2 passed the baseline and
guard replay, then failed because extraction expected consumer-relative paths.
V3 only corrects wrapper paths; native code, proof sources, fixtures and expected
outputs are unchanged. Failed receipts and historical wrappers are retained.

## Limits and remaining work

This is narrow repair acceptance, not closure of the full ownership proof.
Actual glyph reconstruction, persistent spacing-cache/query association, native
array/arithmetic and font/shaping contracts remain open or explicit premises.
The 16 native inputs are retained fixtures whose historical generator was not
preserved; they are not a fresh dictionary-admission proof. The real browser WPT
provides the concrete font/dictionary witness. No clean-base build or universal
C++ memory proof is claimed. Earlier partition and completeness counterexamples
remain valid for their frozen sources.
