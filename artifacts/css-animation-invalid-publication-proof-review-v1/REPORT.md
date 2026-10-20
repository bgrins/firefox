# Independent animated-invalid publication proof review

## Verdict

**Accept v2 as a bounded formal companion to the separately reviewed native repair.** No mathematical or source-mapping blocker remains in the stated scope. This is not a verified translation of Stylo or a proof of the browser's animation scheduler.

V1 executable acceptance was withheld after the producer found that its initial Python `assert` guard disappeared under optimization. V2 replaces that guard with explicit conditional rejection. I authenticated both versions and checked that only the checker guard and report changed, plus the added transfer receipt: all 46 other original inputs, including every Lean and native source, are byte-identical. V1's successful correct-mode replay is retained as historical evidence only.

## Fresh replay and independent challenges

- Authenticated v2 FREEZE, MANIFEST, checker and report against the separately supplied hashes; all **49 manifest inputs** match.
- A fresh manifest-only copy at a separate temporary path passed the complete checker: **81 theorem axiom audits (42 new, 39 imported)**, **29 source bindings**, five compiled Lean semantic mutants, and three compiled Rust semantic mutants in debug and release. All expected mutant rejections occurred at the intended assertions.
- **14 independently written Lean theorems** compile against v2. They establish counterexamples when removing gate admission, reset seeding, payload preservation, stable routing, comparator soundness, map readiness, or roster uniqueness. Positive controls establish that invalid publication does not depend on codec preservation, inherited Initial does not need reset seeding, and a foreign suffix can change cycle state without changing the winning invalid name.
- **11 independent rejection controls** pass. Optimized `-O` and `-OO`, missing isolation/site flags, altered producer helper, injected compiled artifact, extra empty directory, symlinked source, duplicate freeze key, output inside the source, and symlink-aliased internal output all fail for the expected reason without creating output. The optimized cases contain a helper dispatch sentinel; the flag guard rejects before that helper can run.
- All **29 complete retained source slices** match their authenticated byte ranges and independently close at the matching body brace. This check is for the inspected snapshots; it is not a general Rust parser. The three landing source pins match my earlier sealed native/browser review.

## What the proofs establish

| Area | Supported result | Required boundary |
| --- | --- | --- |
| Presence and identity | Inner invalidity emits a named invalid declaration; outer absence emits no declaration. | A selected endpoint and publication admission are supplied. |
| Winner guards | Invalidity wins only after both priority gates and an unseen name. | Native gate construction is not derived. |
| Lower-priority suffix | An admitted invalid winner remains invalid through any finite modeled suffix, including revert and foreign names. | One stable environment and the native foreign-name frame contract; not arbitrary deferred side effects. |
| Named map routing | The selected partition receives removal; the opposite partition is preserved. | Stable registration routing and partition ownership. |
| COW removal | The imported lookup result joins to routed functional removal; tombstones mask ancestors. | Heap/Arc/IndexMap representation remains an imported admission. |
| Comparator | None/None specialization is sound for arbitrary payloads; Some/Some payload equality is unnecessary for removal. | Specialization is restricted to new value None. Extracted native comparator execution is finite, not translation verification. |
| Initial | Original publication disagrees with invalidity iff the initial provider is non-GIV. | Fresh name and reset initial seeding. Tagged observations distinguish coincidentally equal fallback outputs. |
| Valid payloads | Conversion roundtrip and publication preserve the chosen payload abstraction. | Explicit `PayloadPreserved`; serialized equality is insufficient. |
| Empty values | Valid empty tokens and invalidity serialize equally but have different fallback behavior. | Serialization and fallback are contracts, not a proof of CSSOM or parser implementation. |

The model's `cycles` field covers the GIV step's reference/cycle effect. It does not claim that arbitrary suffixes preserve the global cycle flag; the independent foreign-reference example changes it. Normalized Initial and noninvalid branches are explicitly mapped at the selected-value projection, not full native context equality.

The extracted Rust test executes complete retained `from_computed`, `to_declaration`, and comparator bodies. Its valid-value codec and payload representation are synthetic. It does not execute the complete cascade, derive generation, real typed conversion, or Firefox. The historical original conversion is expected to produce Initial and is not counted as repaired.

## Relation to the actual bug

The component addresses the conversion and recascade distinction that caused the independently reproduced browser failures. Its native pins match that accepted repair. The separately sealed native review supplies the source-first normative oracle and browser observations. This formal companion does not establish a new bug count, release-browser impact, or whole-animation correctness.

Remaining admissions include endpoint selection, identity/segment/timing, effect stack and cancellation, priority construction, noninvalid providers, foreign-name and deferred-substitution frames, registration stability, representation and machine limits, observation implementation, compiler/runtime, and source-to-model correspondence. Root/pseudo/SMIL, typed-GIV policy and serialize/reparse preservation are excluded. The report accurately states these limits.

## Reproduction and cleanup

`replay_review.py` reproduces a fresh v2 manifest-only checker run, the independent boundary theorems, and all integrity controls into a new external directory:

```sh
python3 -I -S artifacts/css-animation-invalid-publication-proof-review-v1/replay_review.py --source artifacts/css-animation-invalid-publication-proof-v2 --output /private/tmp/new-publication-proof-review
```

The pinned Lean and Rust toolchains must remain available. This command generates only disposable proof/test outputs, with no native/WPT/Git mutation or Firefox build. Retained original review runs are in accepted-v2 and historical-v1. Owned temporary compiler outputs and copied capsules were removed after terminal results and log retention; CLEANUP.json records the removal. The source capsules were not modified.
