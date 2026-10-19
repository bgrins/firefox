# Font matching repair designs

Two independently applicable proposals, frozen 2026-10-18:

- [A: lexicographic selection](DESIGN-A.md), five native paths plus a proposed 26-subtest WPT. Covers shared/unshared family and fallback consumers, presentation ranking, float narrowing, ties and early exits.
- [B: 11-degree oblique search](DESIGN-B.md), one native path plus a proposed 38-subtest WPT. Keeps unspecified oblique at 14 degrees and the oblique-only policy unchanged.

Neither patch has been applied to the shared checkout. New WPTs, native compilation, browser regressions, performance, Lean theorems and executable semantic mutation gates remain future work requiring design acceptance. Prior reproduced defects are described in the unchanged `css-font-matching-independent-v1` artifact; copying its report here is provenance, not a new run.

`check.py` authenticates snapshots, applies each proposal to the pinned original sources in temporary directories, checks both composition orders, and checks the authored WPT winner tables against a separate rational successive-filter oracle. That oracle is limited to the proposed tables; it is not a complete CSS style model and does not execute C++.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-font-matching-design-v1/verify.py
```

Add `--live` to compare native originals and inherited origin files to their live source paths. The immutable check uses only files inside this artifact and Python plus the system `patch` utility; there are no imports from another artifact. `prepare.py` and `prepare_wpt.py` are retained construction provenance, not frozen replay entry points. Do not rerun them over the frozen directory.

Full source/proof closure proposed for implementation: complete affected functions, two score constructors, shared score type, all five consumer loops, both zero exits, fixed-point types/conversions, ordered range types, face range attributes, simple-family construction, descriptor transfer and Unicode/load/presentation providers. Preserve actual Gecko provider semantics or state each adapter assumption explicitly. Source-only replay packaging must list every transitive script/source/data input; historical receipts should not be required by that replay command.

## Separate lead

The complete helper read exposed normal-request negative-oblique versus italic ordering: current native scores prefer negative oblique, while the current explicit spec sequence prefers italic first. This is a static lead only, not an accepted third bug. It requires a separate calibrated-face runtime/spec review and must not be silently folded into A, B, or a claim of full StyleDistance verification.

## Existing-test obligations

`evidence/survey/WPT-METADATA-v1.json` retains eleven inspected tests, seven metadata files and four absent metadata files. None was run for these designs. Preserve actual baseline outcomes for matching priority/range tests, weight search direction, italic-oblique fallback, oblique-only last-resort behavior, variable-font matching, parsing and descriptor updates. Bug 2033377 and bug 2019181 describe separate known outcomes; absence of metadata is not an executed pass. Ahem descriptor ranges here do not exercise variable font interpolation.

## Provenance

`ORIGINS-v1.json` records copied source hashes and paths. `original/` holds all proposal inputs. The frozen survey supplies primary CSS Fonts/Font Loading snapshots, CSSWG resolutions, native/provider snapshots, existing WPT/metadata and known-issue evidence. Fresh Searchfox caller inventories are in `evidence/searchfox-*.txt`; sandbox DNS failure was retried successfully with read-only network escalation. The current primary CSS Fonts 4 draft was checked again on 2026-10-18 and identifies itself as the 16 October 2026 editor's draft.

`CHECK-RESULT-v1.json` records the executed design checks. `FREEZE.json` and `verify.py` close all replay inputs. The native proposals are reviewable drafts, not a Gecko-formatted/build-validated landing claim.
