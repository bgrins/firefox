# Typed number documents

This opt-in tooling module connects an actual JSON parser document to the accepted
consume-number model and its exact decimal relation. It preserves the existing
statement-document APIs and does not add normative CSS coverage.

`CssDerivation.Parser` contains the seven existing ParserIR combinators and their
transactional backend. `CssDerivation.Codec.Parser` supplies an independent
actual-Json grammar, typed reader, encoder and versioned alias-free envelope.
The reader and envelope have soundness and completeness theorems; lowering
preserves successful values and complete input/error state. Failed parsing
restores the original state and remains distinct from failed document decoding.

The actual-file runner executes the parser returned by the decoder. The fixed
ordinary-Lean `NumberTransfer.project` computes significand, decimal scale,
lexical type and explicit sign afterward. **The numeric projection itself is not
serialized or newly lowered.** Matching `NumberShape` checks types, not CSS
behavior. Only the pinned number document is connected to `NumericResult`; the
changed valid file deliberately exhibits different parsing behavior.

```sh
lake build CssDerivation
python3 -B number_check.py --lean /path/to/lean/bin/lean --out /new/report/path
lake env lean --run CssDerivation/Tools/NumberRunner.lean research/derivation/number/origin/number.json
```

The CLI prints the fixed boundary corpus with both incoming error states. Exact
integer components are decimal strings, avoiding accidental JSON-consumer float
rounding. `changed-number.json` provides changed-valid-program evidence. Empty
and invalid-prefix observations are total-model tests, not CSS conformance
claims without the `StartsNumber` caller premise.

`TRANSPORT.json` binds the exact accepted 62-input capsule, import-only module
relocation and separately credited independent review boundary proofs. Installed
Lean bodies and declaration namespaces are unchanged. `origin/PRESERVED.json`
retains all 49 earlier provenance mappings. Shared canonical modules are reused;
there are no duplicate scalar, input or number-semantics implementations.

The installed checker authenticates transport, restores the exact accepted source
layout and runs its 325-audit harness, then compiles/audits the relocated layout
and the transferred review proofs. Both actual documents are executed again from
the installed paths. The public facade and opt-in Lake target are built in a
fresh source-only tree. CLI/test `main` declarations remain outside the facade
closure. `COMPATIBILITY.json` separately pins earlier checker APIs and inputs.
This inventory overlaps prior milestones and does not measure additional CSS
feature coverage. Temporary compiled outputs are removed.

See `origin/MAPPING.md` for exact theorem scopes and historical source names,
resolved by `TRANSPORT.json`. JSON text parsing, duplicate-key collapse,
serialization, quotation implementation, source-map meaning and hand-mapped CSS
prose remain boundaries. Aliases and definition/profile orchestration are not
supported in this envelope. No native float, Gecko, byte-decoding, DOMString or
memory-safety refinement is claimed.
