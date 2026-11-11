# First-order derivation tooling

This opt-in research library transports the accepted first-order escape pipeline,
typed-data codec, and actual JSON-value schema codec. It is tooling for expressing
and checking manually interpreted algorithms; it does not mechanically derive CSS
semantics from prose or add CSS feature coverage.

## Modules and contracts

| Module | Contract |
| --- | --- |
| `CssDerivation.Backend` | Stateful effect interpreter over scalar input, remainder, and error flag. |
| `CssDerivation.FirstOrder`, `Lowering` | Typed de Bruijn syntax, executable semantics, and lowering preserving complete value/state. |
| `CssDerivation.Codec.Data`, `DataLaws` | Typed constructor roundtrips and accepted normalized-erasure guards. |
| `CssDerivation.Codec.Json.Schema`, `Reader`, `SchemaLaws` | Independent actual-`Lean.Json` schema, executable reader, soundness and completeness. |
| `CssDerivation.Codec.Json.Encoder`, `EncoderLaws`, `TypedSchemaLaws` | Canonical JSON-value typed roundtrips and alias-free accepted-schema correspondence. |
| `CssDerivation.Codec.Json.Document` | Checked fixed legacy escape-document adapter using the new reader. |
| `CssDerivation.Examples.*` | Preserved escape algorithms, literal fixture, and correspondence to existing `CssSemantics.CssEscape`. |
| `CssDerivation.Tools.*`, `Tests.JsonCases` | Actual-file runners, parser observations, and kernel boundary cases. |

Module paths are relocated, but declaration namespaces and theorem names are
preserved. `TRANSPORT.json` records original and installed hashes, the complete
module map, and the signed source checkpoint. Only import lines change.
`CssSemantics.CssInput` and `CssSemantics.CssEscape` are reused byte-for-byte from
the existing library. No duplicated scalar/input implementations are installed.

`Codec.LegacyJson` remains because the accepted schema and document adapter use
its alias type and field helpers. Its older AST fold is not the execution route:
`Document` calls the new `Reader`. Retaining this labeled dependency avoids a
semantic refactor during transport; splitting the helpers can be a later change.
The backend/tree/reference artifacts remain proof references, while `Tools.Runner`
imports only `Document` and executes the decoded real-file program.

## Reproduction

```sh
lake build CssDerivation
python3 derivation_check.py --lean /path/to/lean/bin/lean --out /new/report/path
lake env lean --run CssDerivation/Tools/Runner.lean research/derivation/origin/escape.json '41!'
```

The default `lake build` and main `check.py` still select CSS semantics.
`derivation_check.py` authenticates every installed source, reverses only the
module-import relocation, and requires exact equality to the accepted source
manifest. In fresh temporary trees it runs the unchanged accepted semantic
harness, compiles the relocated modules, audits the exact same 143 theorem names
and axiom sets, runs all three actual-file paths, and builds the opt-in Lake
facade. Temporary compiled output is removed; commands and reports are retained.
The semantic mutations run on the exactly restored accepted layout; relocated
positive compilation/audits/runners separately check the module transport.

`origin/` retains only source provenance, the exact input document, expected
results, and the accepted checker/replay scripts. It does not duplicate Lean
modules. Its old `MAPPING.md` uses historical capsule-relative source names;
resolve those through `TRANSPORT.json`. Invoke the installed root checker, not
the archived checker directly (the latter expects the reconstructed old layout).

## Boundaries

The JSON schema is an internal research format, not CSS grammar. The universal
codec theorems cover JSON values. Text parsing, serialization, quoted-fixture
construction, duplicate text keys, and numeric lexical spelling remain outside
the proofs; actual-file execution supplies finite observations only. The parser
collapses duplicate text keys before schema checking. Raw JSON map schemas
explicitly admit the four two-field layouts and arbitrary cached sizes without
assuming map validity. Canonical encoding uses a valid ordered two-field map.

Aliases are first-match inputs to the generic schema. The fixed document adapter
checks the four alias definitions with empty aliases and singleton contexts, then
checks the program; universal top-level document orchestration and alias weakening
are not claimed. Accepted raw JSON need not re-encode to the identical layout,
cached size, numeric representation, or alias spelling.

`origin/CLAUSES.json` preserves the reviewed normative excerpt provenance, and
`origin/MAPPING.md` gives the original interpretation boundary. Specification
interpretation and caller assumptions remain manually reviewed. No browser,
Stylo/native refinement, new CSS coverage, ParserIR number extension, bytes,
CSSOM coercion, or new DOMString theorem is implied by this tooling integration.

## Generic document profiles

The [document module](document/README.md) adds caller-supplied profiles while
preserving the fixed `Codec.Json.Document` API. Its checker has a separate theorem
inventory and transferred review credit. Neither checker adds normative CSS
coverage. Both build the same public `CssDerivation` facade.

`FACADE.json` pins the exact local dependency closure of that facade. The checker
collects supported single-module import lines, authenticates every dependency,
and rejects missing, changed, unregistered, cyclic, or unsupported imports.
The parser is deliberately restricted to the current source import style; it is
not a general Lean parser. External imports are limited to Lean/Init/Std. Additional
facade modules are copied and compiled, but the original 143-theorem audit and
semantic-control inventory stay unchanged. Document-specific audits are reported
by `document_check.py`. CLI and test modules are excluded from facade closure.
