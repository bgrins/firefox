# Independent direct removal-loop review

## Verdict

**ACCEPT the scoped source-bound mathematical component.** No substantive blocker found. The changing-vector/index join is proved rather than assumed. This acceptance does not establish complete native container/compiler/caller correctness; root owns final acceptance.

## Authentication, source and replay

Authenticated all 29 producer inputs against the externally supplied FREEZE, MANIFEST, REPORT and checker hashes before execution/import. Independently enforced a closed file/directory roster, canonical confined paths, unique JSON keys and no symlink/nonregular inputs. Relocation copied only the manifest roster plus its two seals.

Fresh isolated replay from `package/` completed exit 0. Seven modules compiled; exactly 65 distinct theorem names and axiom reports matched the inventory, restricted to standard Lean `propext`, `Quot.sound` and `Classical.choice`. This is 44 imported checkpoint results and 21 new audits, including five concrete kernel witnesses. AllOrder compiles unchanged, but its separate 55-result roster is not counted in these 65 audits. No native compilation or browser execution occurred.

Read all new loop/API/witness proofs, complete imported PublicRemoval/PublicAPI, source correspondence and validation tools. AllOrder/PublicStorage are byte-identical to the complete modules read in the preceding independent winner review; their relevant raw-delete/representation/unique-state results were checked again in this composition.

Read-only comparison confirms both current native files match the retained snapshots byte-for-byte:

| Native file | SHA-256 |
| --- | --- |
| servo/components/style/properties/declaration_block.rs | 8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a |
| servo/components/style/properties/mod.rs | 2ef96482f50b06dcf87a18abc4d1a9aa0109a9063aa71cadc53e7737022c094d |

Independently extracted all ten complete bound definitions from their correct impl owners and compared their bodies/hashes. An initial unqualified `contains` search selected the identity-set method; restricting to `impl PropertyDeclarationBlock` resolved that extraction mistake. No source mismatch or producer change was involved.

## Loop proof review

`NativeRemoval.loop` executes on raw declarations, current index and a distinct local length. It branches on `index < len` and reads `raw.declarations[index]?`. It does not receive an executable ghost suffix. Erase transforms the current raw vectors/membership, decrements local len, and retains index. Keep increments index and preserves len. The well-founded measure `len-index` decreases on both guarded recursive transitions, even for malformed states; absent read stops with explicit fault.

`split_connection` relates that independent execution to the older reference using a proof-only prefix/remainder invariant. It derives exact terminal raw storage, index and local len, fault=false, and one successful iteration per original remainder element. It is not equality obtained by assigning reference output to the result.

`invariant_safe` constructs a finite sequence of actual modeled states. Every active node carries both vector-length equations, `index < len`, a successful current declaration read and a matching importance read. Its keep/erase continuations specify the actual updated vector/index/length. `safe_head` exposes these facts, and `terminal_invariants` separately derives final representation and no fault from the execution theorem. The distinct length variable is therefore constrained by the proof at each step, not eliminated from execution.

The optional-read fault is a model of failed native-read admission. It is not native recovery behavior. Under admitted unique representation and the proven query/callback certificates it is unreachable. Given representable native len, `index < len` also supplies the mathematical facts `index+1 <= len` and `len > 0` needed for the native updates; Rust usize representation itself remains external.

## Query, singleton and history joins

| Obligation | Assessment |
| --- | --- |
| Direct query | seek scans current raw declaration IDs. seek_projection connects it to firstIndex without supplying a desired index. |
| Membership early-out | Exact representation derives singleton absence from the membership bit. Malformed/stale membership is not admitted. |
| First cached deletion | firstIndex certificate derives the current slot, bounds and selection; the complete first deletion occurs before property-kind split. |
| Singleton return | Unique IDs prove one deletion removes all matches for the singleton. It is not incorrectly sent through shorthand filtering. |
| Shorthand continuation | remove_connection calls the new loop on the already-deleted vector at the original first index and actual resulting length, then proves equality to the reference removal. |
| Callback | Same **ordered** IDs plus represented after-state and unique after-state preserve the cached index. Payloads/priorities may vary. This frame is a premise, not proved for arbitrary native callbacks. |
| Histories and prefixes | step_connection replaces the query/removal component; induction composes arbitrary finite parse/remove/clear operations and each prefix with preservation of representation and uniqueness. |

The native query and shorthand loop use compatible predicates: PropertyDeclarationId routes a shorthand to LonghandId::is_longhand_of; custom IDs do not match shorthands. Singleton selection is identity equality. The proof permits any fixed shorthand predicate, while concrete generated metadata and stable provider behavior are admitted.

The imported stale-index witness remains relevant: retaining the target somewhere does not imply that its earlier cached index is valid after removal/reordering. No proof here silently replaces the ordered-ID callback frame with membership-only preservation. Native debug assertions do not establish the frame in release builds.

## Mutation and integrity evidence

Fresh replay kernel-checks five witnesses: adjacent removals, no matches, exhausted index, incorrect index increment after deletion, and missing local-length decrement. The latter reaches an absent read at index 1 with local len 3 and actual vector length 1 after three successful iterations; its supplied fuel is five, so this fault is not fuel exhaustion.

The exact source mutation increments index on the erase recursion. The mutated module fails the original split_connection proof at the changed recursive index, with no syntax or missing-import failure. To distinguish a substantive mutant from a fragile proof script, I independently extracted that **exact mutated well-founded loop definition**, compiled it successfully, and kernel-proved it leaves `[(1,8),(2,9)]` for the adjacent-target example instead of deleting both targets. `evidence/ExactMutantWitness.lean` and its command receipt retain this check. These are Lean mutations/witnesses, not compiled Rust mutants.

Both capsule corruption guards ran freshly: changed model bytes and an added shadow module reject before replay-output creation, and the injected exit-88 module is not executed. The closed roster and isolated/no-site checks are present in the authenticated checker. Only these two corruption controls are claimed; they are not a comprehensive hostile filesystem test suite.

## Residual admissions

- Native ThinVec/SmallBitVec/set operations and iteration, identity extraction, enum/name equality, generated shorthand metadata, and fixed selection throughout a call.
- rawDelete aggregates native membership removal, bit removal and declaration removal under normal completion and no observation/interleaving inside that helper. It does not prove panic cleanup, allocation or destructors.
- Native usize widths, allocation bounds and compiler/standard-library semantics. The model proves Nat index/length arithmetic and validity under represented storage.
- Actual callback ordered-ID preservation and valid after-state; arbitrary mutation/reentrancy is not covered.
- Parse/extend and clear remain mathematical projections inherited from the checkpoint. Mixed-importance histories do not change the native per-call importance signature.
- CSSOM batching, immutable flags, changed-return values, animation constructors, payload parsing/serialization and whole-browser behavior remain outside this component.

This closes the direct changing-vector loop and its modeled query/history joins. It does not close all native/provider/observer obligations. No live native, WPT, Git, browser or build mutation occurred during review.

## Reproduction

Run `python3 -I -S -B check.py` for this independent package's integrity/evidence check. Full model replay is `python3 -I -S -B package/check.py --output NEW_EXTERNAL_DIRECTORY`, with the pinned Lean toolchain. Retained evidence is source-only and excludes generated olean files/executables.
