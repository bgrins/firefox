# DOMString input integration

The accepted DOMString code-unit adapter is integrated into the standalone CSS
library as a twelve-path patch against
`06893e4890871614f763dc8c955100852ebdd5ac`. The agent prepared this without index changes; root subsequently replayed and signed it as 0127c4f42c620cdaba4f9b92cca93ca95df2d913.
Existing scalar and code-point APIs remain byte-identical; `.DS_Store` is the
preserved preexisting untracked file. Native/browser sources and build directories
were not touched.

## Changes

- Four new modules: `CssDomStringInput`, `CssDomStringInputLaws`,
  `CssDomStringScalarChoice`, and `CssDomStringInputExamples` under `CssSemantics`.
  The accepted bodies change only their import paths and executable observation
  names, which receive a `DOMString` prefix. Namespaces and semantics are retained.
- Normal aggregate imports, all 28 named theorem audits, and all 34 ordered
  observations are registered in the existing full checker. The three anonymous
  kernel examples are retained. `check.py` gains only expected observation rows;
  its validation behavior is unchanged.
- A separately scoped coverage feature, three additional immutable source pins
  (WebIDL, ECMAScript, CSSOM), a standalone contract and current coverage/README
  entries. Existing CSS Syntax and Infra source identities are reused.

`LIBRARY-CHANGES.json` is the exact twelve-path hash inventory.
`integration.patch` includes both tracked edits and the five new files.
`COMPATIBILITY.json` records unchanged existing input sources and the limited
transformation from the reviewed research module bodies.

## Validation

Both direct canonical-source replay (`verification`) and exact patch
reconstruction (`patch-verification`) passed under optimized Python:

| Check | Result |
| --- | --- |
| Fresh dependency-closure builds | Ten modules; no canonical `.lake` outputs used |
| Axiom audit | 70 declarations: 28 new, 27 existing code-point and 15 existing scalar |
| Ordered observations | 79: 34 new, 21 code-point, 24 scalar |
| Global static declaration/audit/coverage validation | 11,895 registered declarations, normal and optimized Python |
| Metadata controls | Missing audit, duplicate audit, unknown module/theorem/specification all rejected |
| Executable-only controls | Early surrogate replacement and lost suffix unit typecheck, then fail unchanged correspondence and exact semantic witnesses |
| Shared-vocabulary control | Wrong leading-surrogate bound still permits correspondence against the jointly altered vocabulary; independent minimum-pair witness rejects it |
| Exact patch reconstruction | Applied without index use to an archive of the committed base; every changed/new path matches its recorded hash |

Only the allowed standard axioms are admitted. Semantic witnesses must produce
the single intended `decide`-proved-false diagnostic; arbitrary errors or warnings
cannot satisfy those controls. The global static registration check is not a
whole-library proof rebuild. No full-library proof receipt or native/browser gate
is refreshed by this integration.

The temporary compiled objects and archived source checkout are removed after
successful replay. Full source-input hash vectors bind the global registration
scan in each receipt, while `compiled_modules` names the smaller proof closure.
The reconstructed source vector matches the direct replay vector.

## Reproduction

From the parent checkout, using a fresh output directory:

```sh
python3 artifacts/css-domstring-library-integration-20261110-v1/patch_replay.py \
  --library artifacts/css-spec-lean \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out /private/tmp/css-domstring-library-independent
```

This reads the committed base with `git archive`, applies the complete patch in
an owned temporary source directory, checks the twelve exact path hashes, and
runs the focused proof/example and global registration checks. It neither stages
the patch nor changes either repository's history. The historical base must be
present in the supplied standalone repository. No browser, network or dependency
installation is needed. `replay.py` can also check an already reconstructed
source tree directly with the same `--library`, `--lean` and fresh `--out` flags.

The standalone library retains its independent `python3 check.py` full-check
entry point and `python3 check.py --coverage-only` registration check; its source
and documentation have no parent Firefox path dependency.

## Retained boundaries

The domain is finite lists of 16-bit code units. Valid adjacent surrogate pairs
combine; unmatched surrogates survive until CSS preprocessing replaces them.
The independent relations check exact output, original suffix, one/two-unit
consumption, complete finite decoding and composition with CSS filtering.

The scalar-choice theorem equates final filtered output after prior surrogate
replacement. It does not prove equality of entire DOMString/USVString APIs,
exceptions, source storage, serialization, indexing or re-encoding. CSSOMString
permits an implementation choice; `replace`/`replaceSync` explicitly take
USVString. The documented `insertRule` DOMString route remains conditional on
that type choice, successful conversion and pre-parse guards.

The specification mapping remains manually reviewed. Byte decoding, endianness,
BOM policy, JavaScript coercion, arbitrary-index/returned-metadata wrappers,
UTF-16 re-encoding, streaming/chunk boundaries and browser refinement are not
added. `JavaScriptLength` states the language's bound separately; numeric unit
admission does not enforce it. The shared-predicate mutation control explicitly
demonstrates the remaining vocabulary assumption.

No broader library change was necessary. Re-encoding/round-trip work remains a
separate possible follow-up after this accepted-model integration.
