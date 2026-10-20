# Terminal whitespace raw spans

## Result and exact scope

A new component proves the terminal outer-whitespace byte extent and retained prefix for arbitrary finite modeled token lists. It does not prove tokenizer translation or general serialization correctness. All37 named theorem statements are audited; five compiled Lean semantic mutants discriminate extent/reset/metadata errors. Ten complete source bindings and full modules tie this component to the final escaped-whitespace candidate8f166d5cbd25d298a34d820e148c8967d3b0b0fc009a371831d4e4be336548d7. Runtime/browser acceptance is separately recorded in css-variable-escaped-whitespace-review-v1; this capsule performs no browser or native build.

## Independent reference and source-shaped execution

`scan` follows the native per-token assignments: preserve first class, replace last, replace last-non-whitespace only on a non-whitespace token, and overwrite trailing length with the current whitespace payload length or zero. `splitRev` independently partitions the complete list from the right into retained tokens and the whole terminal whitespace run; `bytes` concatenates their raw byte payloads. The reference does not use the scanner's length or metadata.

`partition` and `splitRev_white` prove the split's reconstruction and whitespace classification for arbitrary lists. `splitRev_coalesced` derives that the removed run has at most one token under explicit adjacent-whitespace coalescing; `removed_extent` joins its aggregate raw byte length to the scanner result. `exact_prefix`, `trim_bound`, and `preserved_token_bytes` establish precise removal, bounds, and preservation of every preceding token byte. Non-whitespace payloads may end with space/tab bytes: excluding these would hide the defect. A kernel counterexample demonstrates failure without coalescing.

`scan_first/last/nonwhite` hold for arbitrary initial state. `metadata_last` derives the corrected final class using nonempty raw-token payloads; `initial_ready` derives a non-whitespace start after the current constructor's initial-token skip. `stored_observations` joins retained bytes with first/last *outer-span* classes. For blocks this is the source's opener class, not the flattened closing-token class. No separator-table or retokenization adequacy theorem is asserted.

`leading_overlap` proves saturating trim after an arbitrary leading byte drop equals the same drop from the retained prefix, including all-whitespace overlap in older standalone variants. It does not justify which leading bytes may be removed or repair their origin metadata. `finish_partition` distinguishes identity EOF treatment from an explicitly admitted repair whose terminal outer token is non-whitespace; the latter has zero trim length. `retained_slice` preserves every bounded reference slice inside the retained prefix. The theorem does not assume native reference endpoints already satisfy that bound; deriving all those endpoints belongs to the origin/provider composition.

## Source, predecessors and admissions

The current candidate includes preceding leading-origin and last-token-metadata fixes. The escaped-whitespace standalone packages omit those fixes and prove only their own source applicability elsewhere. `before-custom_properties.rs` predates exact-length trimming; `before-metadata-custom_properties.rs` additionally predates corrected last metadata. Old ASCII-trim and old last-metadata kernel witnesses are distinct. No native-source binding is silently transferred between versions.

The accepted registered-token-boundary proof inspired the accumulator/reference pattern, but is not imported or counted here: it omits comments and includes block closing classes. Here Kind copies the complete non-Nothing serialization class inventory; comments map to DelimSlash and blocks to their outer token class. Exact classifier correspondence remains a source admission. The origin agent confirmed compatibility: maximal initial raw CSS whitespace, comments retained, recursive completed-tree reference offsets, EOF repair separately admitted. That agent's frozen source predates both trailing fixes.

Native admissions remain explicit:

- Actual public parser events form a finite, nonempty, coalesced outer-token partition of the original UTF-8 source. Whitespace payloads equal raw source spans (including CRLF); non-whitespace spans include complete token/block bytes. No tokenizer/codec/cache/error-history translation proof is supplied.
- Constructor initial-token skipping, nested parser consumption and EOF completion establish the named InitialReady/EOFReady/provider facts. The source shows these mechanisms; hashes and full-body bindings are not proofs of them. EOF dropCount is bounded and native is only zero/one, while the model allows arbitrary bounded counts.
- Native class projection has no Nothing-emitting token; source Kind mapping preserves every non-Nothing enum class. Block opener summaries require a separate separator adequacy argument. Positive raw lengths, usize capacity, UTF-8 slicing, reference-bound derivation, allocation/compiler/stdlib/OS remain external.
- No universal substitution, typed conversion, fallback eligibility or used-dependency proof. Native fallback discards the additional tuple fields and retains whitespace unchanged.

A backslash delimiter followed by newline is intentionally retained as a residual witness: trimming removes its newline and can affect a subsequent parse. Thus correct token-extent measurement does not imply preservation of complete serialized token semantics. No false global closure is inferred.

## Counterexamples and validation

Kernel examples cover escaped-content preservation versus old byte trim, old last metadata, raw two-byte CRLF, comment/block reset, standalone empty overlap, noncoalesced input, EOF closing and the residual delimiter case. Compiled semantic mutants alter raw trim, omit metadata correction, retain stale length across non-whitespace tokens, collapse whitespace extent to one byte, or use an inner-block length. Every mutant must compile and then fail a named value comparison; infrastructure failure is not success. These are model-operation mutations, not native Rust mutation runs. Source/axiom integrity controls and canonical/relocated replay receipts are separate and add no theorem assumptions or browser coverage.
