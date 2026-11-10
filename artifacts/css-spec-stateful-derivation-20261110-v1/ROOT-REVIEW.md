# Independent review and replay

Root reviewed the typed interpreter, generated program, source recognizer, bridge, examples, and the pre-existing Escaped/HexRun/Terminator definitions. The relation is inductively specified; the generated implementation imports only StatefulIR. The proof preserves the complete result rather than comparing a projection. The caller and preprocessing boundaries are explicit.

The recognizer is specialized to one reviewed algorithm shape. Its full-body match and extracted parameters are useful provenance, but do not establish general prose translation. Dependency-definition metadata is stripped generically; only algorithm metadata has exact refusal checks. Both formal models could share an interpretation error. These limitations are correctly disclosed in REPORT.md.

An independent execution copied exactly the 15 hash-checked entries in SOURCE-ONLY.json into an owned temporary directory. It copied no generated code, prior result or compiled module. Running check.py there regenerated the implementation and rebuilt the reference modules, proved the bridge, passed all 18 examples and reproduced all 12 controls, including seven type-correct semantic mutations. The frozen number-parser interface was rejected without output.

ROOT-REPLAY.json records the actual command, source allowlist, subprocess outcomes and successful scratch removal. ROOT-REPLAY.log and root-replay-logs retain the outputs. The reviewed source bytes remained unchanged. This is independent replay of this experiment, not independent authorship of the reference semantics or a general compiler-correctness proof.
