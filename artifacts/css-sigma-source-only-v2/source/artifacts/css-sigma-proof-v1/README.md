# Final sigma verification

## Claims and replay

`Sigma.lean` proves greedy nearest-context classification for arbitrary finite lists, including overlapping Cased/Case_Ignorable properties. It proves masked projection, all-unmasked reduction, independence from masked code point properties, and indexed context-slice correctness. The slice theorem assumes complete context and correct coordinates. It does not prove frame construction, skip maps, UTF-16 encoding, ICU, or output arrays.

Run `python3 artifacts/css-sigma-proof-v1/check.py --live --output PATH` from this checkout; PATH must not exist. Omit `--live` to check the frozen candidate independently of later native edits. The default authenticates the frozen input manifest, compiles Lean with strict diagnostic/axiom auditing, runs negative controls, and compiles the extracted native helper. `--development` bypasses frozen source authentication and cannot support final acceptance. The bridge requires this checkout's built ICU `ucase.o` and exported headers; a different build requires explicit re-preparation and review of its identities.

## Native bridge

The exact integrated helper and call expression are extracted from `native-candidate.cpp`. C++ uses the actual Gecko UTF-16 primitives, actual 32-bit index arithmetic, and the actual compiled ICU case-property backend (`ucase.o`). All 1,114,112 backend property answers are compared with pinned Unicode 17 Cased/Case_Ignorable data. The public ICU dispatch to that backend is source-reviewed, not linked through the public API here. String/style containers are transparent bounds-checked adapters, not Gecko implementations. The helper is compiled with active assertions. Scalar-reference comparisons are finite evidence, not a C++ or LLVM formal proof.

The scalar oracle independently filters ignorable properties and selects the nearest remaining predecessor/successor. Masked scalars project to uncased nonignorable barriers. The corpus covers every code point in each context direction, all supplementary code points with each individual mask bit, short paired contexts and all their scalar masks, extraction slices, long contexts, and isolated surrogate robustness. Synthetic mismatched pair masks test the stronger OR rule; normal editor construction gives both units the same mask. Lone surrogates have neither property in the exhaustively checked backend.

The C++ extraction checks the exact input-selection call, but does not execute the entire TransformString loop. The Lean slice theorem requires the caller's source index to address the corresponding sigma in the complete run. The native loop advances both input indices per UTF-16 unit and the helper asserts sigma/style-length correspondence; correct frame construction and skip-map coordinates remain source-reviewed and browser-tested premises. No cross-run CSS casing conformance claim is made. Native string-length limits and index bounds are reviewed manually; corpus lengths do not exhaust uint32 lengths.

## Preservation

The token-preservation check compares the entire native file before and after while permitting only the new helper/include, the exact replacement sigma branch, and removal of pending sigmaIndex state. Irish predecessor state, other locale branches, output expansion/deletion and bookkeeping tokens must remain identical. Whitespace and comments are ignored by this check. It is a change-scope check, not proof that unchanged code is correct. The helper is read-only; both sigma outputs remain one UTF-16 unit.

## Preparation history

`HANDOFF-v1.json` records the intermediate pre-integration state. The initial warning-control fixture did not emit a warning and the control suite rejected that fixture. The corrected fixture emits an unused-simp warning. `lean-development-v2` passed 16 theorem audits, eight semantic mutations and six diagnostic controls. `helper-development-v1` passed 18,523,178 finite native decisions before integration; later final replay receipts supersede development outputs. No production fix was discovered by these proofs: the accepted browser witnesses preceded this companion.
