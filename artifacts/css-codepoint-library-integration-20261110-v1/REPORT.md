# Code-point preprocessing library integration

The reviewed finite code-point preprocessing model is integrated into the
standalone `artifacts/css-spec-lean` library. Its scalar input API is unchanged.
The integration adds four modules, 27 audited theorem declarations, 21 ordered
executable observations and a separately scoped coverage feature. No native code,
browser state, shared build directory or Git index/history was changed by this
agent. The parent owns review and commits.

## Canonical changes

- `CssSemantics/CssCodePointInput.lean`: executable preprocessing and independent
  point/list relations over finite `List (Fin 0x110000)` input, including surrogates.
- `CssSemantics/CssCodePointInputLaws.lean`: correspondence, uniqueness, normalized
  output, nonexpansion, surrogate replacement and numeric-admission boundaries.
- `CssSemantics/CssCodePointInputRefinement.lean`: refinement to the existing
  `CssInput`, ordinary-scalar preservation and idempotence under re-embedding.
- `CssSemantics/CssCodePointInputExamples.lean`: 21 named observations and a
  kernel-checked theorem that they pass.
- `CssSemantics.lean`, `tests/Audit.lean`, `tests/RunExamples.lean`, `check.py`:
  normal full-check registration, including the exact executable result vector.
- `coverage.json`, `research/coverage-map.md`, `research/codepoint-input.md`,
  `README.md`: source pins, accepted domain, evidence scope and remaining boundaries.

The canonical source and examples for the old scalar API are byte-identical to
library base `162b20fb7c53a0ab89b20875a965baee98fb66bb` (`COMPATIBILITY.json`).
The static declaration/coverage validation body was moved unchanged into
`validate_coverage`. The normal full checker still invokes it. New
`--coverage-only` exposes those same registration checks without building Lean;
it never creates or refreshes a full verification receipt.

The copied proofs retain the reviewed model's namespace `CodePointInput`; module
filenames follow the surrounding `CssSemantics.Css…` convention. The earlier
capsule `css-codepoint-preprocessing-20261110-v1` remains unchanged.

## Validation

The accepted scoped run is `optimized-verification/report.json` and
`optimized-replay.log`. A preceding ordinary-Python pass is retained in
`final-verification`. Each successful run:

- Compiles fresh copies of exactly six modules: `CssInput`, `CssInputExamples`,
  `CssCodePointInput`, `CssCodePointInputLaws`, `CssCodePointInputRefinement`, and
  `CssCodePointInputExamples`. Imports use only these source outputs and the pinned
  Lean 4.35.0-rc4 toolchain, with no canonical `.lake` artifacts.
- Audits 27 new declarations and the 15 declarations originating in the two copied
  scalar modules. Only the standard allowed axioms are admitted. The exact names
  and axiom sets appear in `scoped_axioms`.
- Compares 21 new and 24 prior scalar observations against their ordered vectors
  in canonical `check.py`, and checks aggregator/runner/audit registrations.
- Runs the same global static coverage/audit registration check under normal and
  optimized Python: 11,867 declarations. This is registration coverage, not a
  claim that 11,867 proofs were rebuilt by this scoped run.
- Rejects five metadata controls: missing audit, duplicate audit, unknown module,
  unknown theorem and unknown specification. These exercise the extracted
  canonical validator in a small valid fixture before perturbing it.
- Typechecks two executable mutations (drop surrogate replacement; retain the LF
  after CRLF), then rejects their unchanged correspondence proofs and concrete
  witnesses. Each witness must produce the single expected `decide`-proved-false
  diagnostic; an unrelated error or warning cannot satisfy that control.
- Hashes all global registration inputs before and after the run, and removes its
  temporary build directories. `inputs.json` binds the exact source inventory.

`EXISTING-OUTPUT-CONTROL.json` records rejection of an already existing output
directory before any checking starts. The checker cannot overwrite a prior
success receipt with a failed rerun. Python optimization does not disable the
explicit rejection guards.

The initial scoped attempt in `verification`/`replay.log` failed because its
namespace-wide scalar audit selection included two later theorems declared in
uncopied modules. The repaired harness selects declarations actually originating
in the copied scalar files and verifies their global audit registration. The
failure is retained; no model proof was changed to resolve it.

No full-library build, browser comparison or native build was run. Historical
whole-library/browser acceptance counts and receipts are not refreshed here.

## Reproduction

From the Firefox checkout, choose an output directory that does not yet exist:

```sh
python3 artifacts/css-codepoint-library-integration-20261110-v1/replay.py \
  --library artifacts/css-spec-lean \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out /private/tmp/css-codepoint-library-independent
```

The script requires the standalone library's source checkout for its complete
global registration scan. Only the six listed modules are copied and compiled;
no prebuilt library outputs are required. `SOURCE-ONLY.json` names the replay
scripts, compiled source set and full static-input manifest. The library itself
is independently usable: `python3 check.py` remains its complete proof/example
check, and `python3 check.py --coverage-only` is its static registration check.
Neither canonical documentation nor source depends on this parent checkout.

## Specification and trust boundaries

The source mapping is manual. The original reviewed capsule used the CSS Syntax
3 [input-preprocessing clauses](https://drafts.csswg.org/css-syntax-3/#input-preprocessing),
from [revision c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs),
SHA-256 `4a4a5a3994bda10a56885e66776169d0e05d5a7515b0def4e8859c20e3fd4afc`,
and the code-point/surrogate ranges in
[Infra c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a](https://github.com/whatwg/infra/blob/c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a/infra.bs),
SHA-256 `687e65669b9d85c2147a139513fe319097cf84af1005f5c9d7cb3d2ade0c1aed`.
These immutable primary links and hashes are also recorded inside the standalone
library. Source provenance is not a proof of faithful interpretation.

The admitted domain is finite lists of code points U+0000..U+10FFFF. Results are
scalar-only `List Char`. Byte decoding, encoding detection, BOM decoding policy,
WebIDL/DOMString/UTF-16 conversion, live streams and chunk-boundary processing
remain outside the model. A supplied surrogate pair is two code points here, not
two code units awaiting conversion. Numeric callers should use `ofNat?` or
`filterValues`; direct numeric `Fin` literals can wrap. The output normalization
and refinement theorems do not establish a general Firefox/Stylo refinement.

## Next decision

This module closes the scalar-only preprocessing coverage gap without extending
the DSL or changing existing tokenizer entry points. A separate pending-CR
streaming adapter would be the next narrow input-layer theorem if streaming is
needed. A WebIDL/UTF-16 boundary requires a distinct domain and conversion
contract; it should not be inferred from this code-point model. No broader
library change is required to accept this integration.
