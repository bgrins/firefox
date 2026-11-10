# Root review and independent replay

Root read the first-order syntax, direct interpreter, lowering, universal theorem, escape bridge, reusable programs and JSON emitter. Expr and Stmt carry typed data rather than arbitrary function payloads. The lowering theorem quantifies over all typed statements, environments and initial states, preserving input and error state as well as the result.

The shared expression evaluator remains a real boundary. The retained multiplication-as-addition control correctly leaves lowering correctness intact while failing the separate CSS escape bridge and witness. The report also distinguishes the actual Python JSON emitter from a proved typed codec. No general English-to-Lean or native correctness claim follows.

An independent replay copied exactly the 22 hash-pinned source entries into a fresh temporary directory. That includes the older generated escape reference as source, but excludes the new first-order generated output, compiled modules and prior results. Regeneration, universal proof, escape correspondence, examples and all twelve controls passed. ROOT-REPLAY.json/log and root-replay-logs retain the execution; the temporary tree was removed and the source hashes remained unchanged.

Root separately checked all seven CLAUSES.json byte ranges against the pinned source and resolved every AST pointer. The mappings remain manually chosen interpretation links, not semantic proofs.
