# Generic document profiles

This module integrates the accepted flat-definition document reader and its
proofs into the opt-in `CssDerivation` library. It does not change existing scalar,
input, fixed escape-reader APIs, or CSS feature coverage.

## Public modules

| Module | Purpose |
| --- | --- |
| `CssDerivation.FirstOrder.Weakening`, `WeakeningLaws` | Append unused context tails; preserve typed erasure and evaluation, including fold binders. |
| `CssDerivation.Codec.Document.Profile` | Caller-supplied signatures, independent schema relations, generic document reader and escape wrapper. |
| `CssDerivation.Codec.Document.KeyLaws`, `DefinitionLaws` | Exact keys, definition-list iff, ordered names and uniqueness. |
| `CssDerivation.Codec.Document.Laws` | Accepted-document soundness and all-JSON equality with the existing escape reader. |
| `CssDerivation.Codec.Document.AliasLaws` | Actual definition normalization and selected canonical-use evaluation without ambient capture. |
| `CssDerivation.Examples.GenericEscapeDocument` | Preserve the old escaped-code-point fixture relation for every scalar input. |

Only module import paths change in transferred Lean files. Existing declaration
namespaces, including historical `CssDerivation.DocumentDesign`, remain intact.
Renaming that namespace would be a separate API/refactoring change. The fixed
`CssDerivation.Codec.Json.Document` source and API are preserved byte-for-byte.
The new escape wrapper's all-JSON equivalence is retained as a theorem.

`Tests.DocumentInputs`, `Tests.DocumentCases`, `Tests.DocumentBoundary`, and
`Tools.DocumentRunner` are outside the public facade closure. The runner reads
actual files and executes the decoded generic-reader result; it does not import
a generated escape reference. The four boundary theorems in `DocumentBoundary`
are transferred independent-review results, not new author proofs. Their source
and report attribution are pinned in `TRANSPORT.json` and `origin/REVIEW-REPORT.md`.
One proves a concrete counterexample to the unclaimed document converse.

## Reproduction

```sh
lake build CssDerivation
python3 document_check.py --lean /path/to/lean/bin/lean --out /new/report/path
lake env lean --run CssDerivation/Tools/DocumentRunner.lean next research/derivation/document/fixtures/next.json abc
```

`document_check.py` authenticates 45 accepted inputs, reverses exact import-line
relocation, and runs the unchanged accepted harness in a fresh temporary source
tree. It separately compiles relocated modules and the four review proofs,
checks the exact 160-theorem axiom inventory (156 accepted plus four review),
runs the five actual files, and builds the public Lake target. The accepted four
semantic mutants and three provenance controls run on exactly restored paths;
positive compilation/audits/runtime checks separately validate relocation.

The existing `derivation_check.py` remains a separate first-order/JSON milestone
gate with its original 143-theorem audit. Its necessary integration adjustment
collects and authenticates the current facade dependencies through `FACADE.json`.
Missing/changed dependencies, unsupported import syntax, and excess registry
entries are checked by separate controls. Those are registration controls, not
new formal semantic proofs.

The main `check.py`, default `CssSemantics` target, and `coverage.json` retain their
CSS accounting. Root integration should execute the actual default build after
applying the patch; source-only tooling checks do not claim that unchanged large
CSS target was rebuilt. No native-library link check is claimed.

## Limits

The caller supplies trusted signature names/input/result types. Definitions are
flat and alias-free; cycles and forward references are rejected. Source maps are
inert object-valued metadata. `ExactKeys` is a key-list permutation relation;
`Field` retains shared Lean map lookup. Arbitrary raw objects need not be ordered
maps, and enumeration is not silently identified with successful lookup.

Definition admission has a full iff. The whole-document relation has soundness
only: normalized erasure loses scope guards required by a converse. Selected alias
semantics covers canonical `nodeJson "use" [name]` under arbitrary admitted
definitions and ambient tails; it is not whole-program alias semantics or an
all-raw-layout use-node theorem. JSON text parsing, duplicate text-key handling,
numeric lexical forms, and CSS prose interpretation remain outside the proofs.
`origin/MAPPING.md` retains the original claim boundaries and historical source
names; resolve those names through `TRANSPORT.json`.
