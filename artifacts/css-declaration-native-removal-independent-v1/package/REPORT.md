# Direct declaration removal-loop component

## Result

The source-shaped Lean removal loop is now connected universally to the accepted public-storage reference. It models the actual changing raw declaration vector, importance vector and membership set, a numeric index, and a distinct mutable local length. It does not execute by consuming a supplied ghost suffix. Under the existing unique-ID and exact-representation premises, the proof derives normal termination, no absent read, matching declaration/importance read bounds at every iteration, same-index continuation after deletion, and exact final storage. The direct query and singleton/shorthand paths compose into arbitrary parser-priority/remove/clear histories and every prefix.

This closes the changing-vector/index loop join identified in the earlier public-storage review. It is a source-bound mathematical model component, not a machine-checked Rust/compiler/container proof. No new native defect, browser run, native build, WPT modification or Git change is claimed.

## Authenticated dependency and API review

Parent attested the current 44-result CHECKPOINT SHA-256 `2667921b7a4804190b0af210bb88aaa9e5990de8a4ef7f828d88be1ab59ad2f3` and replay SHA-256 `5e0662187e3efcac16483b4c1730833bfb678e5157221ea2f06d34c76807e9e6`, against HEAD bb029748eaa6, introduced by 82f7308ddbb5. Four copied Lean files match every checkpoint source hash. PUBLIC-API-REVIEW.md records review of the nine added source joins: membership early-out, unique singleton deletion, same-ID callback frame, queried removal and API histories. The earlier 35-result review remains unchanged.

## New proof chain

- `NativeRemoval.loop` uses direct optional reads of current declaration payloads. When keeping an entry it increments index; when deleting it decrements local length and leaves index unchanged. The measure len-index decreases under either guarded transition, including on malformed states. An absent read returns an explicit fault only to expose failed source admission; native Rust would not take such a recovery branch.
- `split_connection` proves exact equality of the complete terminal result to the old removeLoop result under its prefix invariant. It derives final index and local length as kept-prefix length plus surviving suffix length, fault=false, and exactly one successful iteration per initial suffix element.
- `Safe` and `invariant_safe` provide a finite derivation of all current-vector transitions. Each active node includes separate valid declaration and importance reads, both vector lengths equal to local len, and index < len. Keep/erase constructors state the exact next indices and lengths. `safe_head`, `terminal_invariants`, and explicit transition/measure lemmas expose those consequences.
- `NativeRemovalAPI.seek` scans raw declaration IDs directly. `seek_projection` and `query_connection` establish correspondence to PublicAPI's reference query, including the membership early-out. `remove_connection` performs the first direct read/deletion and splits singleton versus shorthand; it replaces the shorthand execution with the new numeric loop. `queried_refinement`, `history_refinement` and `every_prefix` derive the original API contracts through this loop. `callback_refinement` retains, rather than proves, the same ordered-ID frame condition across the native callback.

The full replay compiles seven modules and audits an exact roster of 65 theorems: 44 copied checkpoint results and 21 new results. AllOrder is compiled unchanged; its earlier 55 theorem inventory is not counted again as newly audited results here. Only the standard Lean foundations propext, Quot.sound and Classical.choice are allowed. No sorry, custom axiom, admit or native_decide is accepted.

## Controls and mutations

Five kernel-checked witnesses cover consecutive target deletions, no matches, an already exhausted index, a wrong increment after deletion, and a missing local-length decrement. The wrong-increment model leaves a shifted adjacent target. The missing-decrement model reaches index 1 with local length 3 but vector length 1 and therefore an absent read; this occurs before its explicit fault-model fuel is exhausted. These witnesses are not a universal native mutant theorem or a broad finite corpus.

The replay also compiles an exact source mutation of NativeRemoval's deletion recursion that increments the index. It preserves syntactic validity and termination, but the original refinement proof is rejected with a semantic proof error. This is one mutated Lean-module rejection plus the successful kernel witnesses, not compiled native Rust mutation coverage.

## Native boundary and remaining obligations

SOURCE-CORRESPONDENCE.md maps ten complete native definitions to the model. SOURCE-BINDINGS.json authenticates their exact bodies. The native removal/query file matches the earlier retained public-operation source at capture. The actual helper clears membership before deleting importance and declaration slots; the modeled rawDelete is its normal-return aggregate. The optional-read fault is never reached under the proved invariant and must not be described as native error handling.

Native usize representability remains an input premise. Given it, the proved index < len guard supplies the arithmetic facts needed for index+1 and len-1; this capsule does not formalize Rust's integer representation or the allocator. ThinVec, SmallBitVec, identity-set operations, iterators, enum/name identity extraction, metadata predicates, compiler correctness and absence of observation/interleaving inside deletion remain admitted. The concrete source-to-model mapping is audited, not generated by a verified translator.

The combined history now uses the direct source-shaped query/removal loop. Its parse/extend and clear components remain the previously accepted mathematical projections. It does not model CSSOM update batching, changed-return values, immutable flags, animation constructors, payload parsing, exception/panic cleanup, or arbitrary mutable callback histories. Callback readiness still requires represented after-state and the same ordered IDs. No stale cached index is made safe merely because a matching declaration survives elsewhere.

## Reproduction and packaging

Authenticate externally supplied MANIFEST/FREEZE/checker pins. Run `python3 -I -S check.py --output /absolute/fresh/output`. The checker authenticates the complete file and directory set, dependency pins and complete source bindings before executing the replay helper. Replay uses the pinned Lean binary and an output-only LEAN_PATH, with Python/Lean overrides cleared. Exact audit names and standard axioms are checked, as is the semantic mutation rejection. Two retained tamper controls reject changed model bytes and an added shadow module before creating replay output.

The initial development failures were proof-script simplification and well-founded-function reduction issues, not discovered native faults. The final source-only replay and separately relocated manifest-only replay are the release gates. Retained receipts record their actual results; no claim rests on a development run. Commit the manifest roster and two seals only. Generated executables, .olean files and temporary replay trees remain external.
