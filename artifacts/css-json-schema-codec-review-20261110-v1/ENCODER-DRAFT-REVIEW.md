# Encoder and schema-law interface review

The proposed `readExprData_spec` and `readStmtData_spec` state an iff between actual Json decoding and the independently constructed grammar relation. Completeness is a substantive additional guarantee beyond the subtype's immediate soundness; it can detect silently dropping an accepted layout or tag. The proof implementations are still being compiled by the author, so this note reviews interfaces and source intent, not successful proof checking.

`nodeJson` emits a two-entry args/op map with correct ordering and cached sizes. Typed encoders preserve all primitive tags, variable indices, operand order and scan budget. The canonical image contains no aliases; quantification over arbitrary alias environments in encode/decode roundtrip is therefore appropriate. Character encoding uses the scalar value and the Char validity invariant.

`expression_json_roundtrip`/`statement_json_roundtrip` compose schema completeness with the existing constructor-data roundtrips. `accepted_expression_schema`/`accepted_statement_schema` expose an actual Json grammar witness plus exact normalized typed erasure, preserving the predecessor's operation/index fidelity while making the formerly unproved Json adapter explicit. These theorem statements are useful and non-tautological. No additional source mismatch found in this draft.

The scope remains the AST node adapter and supplied alias interpretation. Top-level document fields, fixed definition validation, provenance content, text parsing and file acquisition are not universally covered by these statements. The final runner must execute this adapter rather than retain the old foldJson path. No final acceptance pending compiled proofs, harness and actual-file replay.
