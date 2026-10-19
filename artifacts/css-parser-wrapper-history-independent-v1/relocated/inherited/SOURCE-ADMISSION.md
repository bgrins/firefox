# Native/model admission ledger

## Frozen source and complete bindings

`SOURCE-PINS.json` pins complete current `parser.rs` and `tokenizer.rs`; `SOURCE-BINDINGS.json` preserves 70 complete functions, records and implementation blocks, regenerated directly by `native/bindings.py`. Searchfox discovery and the narrow fallback after a DNS failure are recorded in `discovery`. The parser includes the accepted depth-limit cleanup repair; the tokenizer includes current identifier/numeric/bad-URL repairs. This capsule adds no repair.

`next_including_whitespace_and_comments` performs pending cleanup, EOF/delimiter admission, a position-key comparison, either end-state replay or actual tokenization/cache replacement, and returns the cache token. These phases map to `PublicNext`, `PublicCleanup`, and `PublicFetch`. `state`/`reset` map to saved cursor capture/restore; native reset changes no cache or observer fields. `SeenStatus::see_function`, enable and query bind `track`, `begin` and `query`.

`next_token_unchecked` maps to `ByteLex.selected/family/other`. Minus numeric/CDC precedence is retained. Name-start, escaped/NUL/non-ASCII names and URL lookahead use the inherited actual provider models. Comment bodies use `CommentScan`; annotations use `CommentDirectives`. `consume_until_end_of_block` supplies the typed delimiter stack: raw tokenization does not replace the public token cache. The common stack-transition helper is a shared native-shaped primitive between the two mathematical machines, not a separately proved CSS parser grammar.

## What is derived

No cached-token-equals-fresh premise is required at constructor entry. `coherent` follows from population and is preserved by raw cleanup/hits/save/reset; a matching key yields equality. The independent cursor/token reference ignores the cache. The annotation reference only remembers the key, and derives which source comments actually execute instead of equating token replay with an observer write.

Per-provider strict progress derives complete cleanup with byte-length fuel. Per-provider bounds derive a legal final byte range. Concrete Function relevance follows decoded names and independent ASCII matching. Non-relevant cache entry follows an actual returned token; Colon is a specialization. Arbitrary admitted epoch histories then derive query results through the existing event theorem.

## Explicit native premises

1. **Immutable same-source input and saved states.** Rust input is borrowed `&str`. Resets in this model use states captured from that same parser instance. The total mathematical out-of-range saved-index no-op is convenience only; native replay requires an existing saved index. Forged/cross-source states are not admitted.
2. **Sentinel.** Native construction stores a dummy Semicolon at `usize::MAX`, whereas the model uses `None`. Input length/positions must stay below that impossible cache key. This is not a claim that the Rust cache has Option layout.
3. **Projection.** Cursor means byte position plus pending block. Native cached end state also stores packed line and UTF-16 column fields. Those fields are not projected or proved canonical by this component. Existing URL native-state lemmas remain separate, and full metadata cannot be inferred from equal projected token tuples.
4. **Remaining providers.** `Family` distinguishes whitespace, string, numeric, hash, at-keyword and punctuation consumption. They return non-Function tokens and no function/comment observer writes on these dispatch branches, as the complete bodies show; exact counts, progress, bounds and legal UTF-8 endpoints are still provider contracts in the universal byte join. The finite driver does not supply arbitrary observed native counts. It rejects unsupported families and uses only ASCII whitespace runs and the one-byte semicolon where an opaque provider is reached.
5. **Canonical codec and boundaries.** The input and saved/read positions are valid native UTF-8 boundaries. The accepted name/escape and URL models retain their explicit shared codec/library assumptions. Mathematical byte lists alone do not prove Rust `str` slicing safety or allocation correctness.
6. **Normal return/machine domain.** usize arithmetic, lengths/capacity, packed metadata headroom, allocation success/panic behavior, standard library, compiler and Rust memory/borrow execution are not proved by list/Nat models. The source replay compiles complete algorithms, not a formal Rust semantics.
7. **Enable phases.** Each theorem's complete epoch begins with no relevant cached Function. Later epochs require that predicate explicitly; safe cold/Colon entry is derived. Native supports arbitrary enable/query interleaving, but such histories can fail the ideal logical observation contract, as the retained witnesses show.
8. **Observer contract.** Exact native writes are proved against a separate key-sensitive execution reference. This does not assert ideal comment replay, source-map publication, speculative parsing rollback or a normative sourceURL behavior.

## Not yet composed

The whitespace/comment-skipping public wrappers, callback-based nested/parse-until/try-parse histories and their depth/stop restoration, full metadata, exact other-family payloads/counts and production declaration caller entry protocols remain separate obligations. The current finite stop fixture sets the real delimiter field around the primary operation; it does not execute/prove the whole outer callback protocol.

The independent logical reference shares provider output and typed delimiter transition, but has no cached value or native tracking mode. Independent Function matching is separately proved. The annotation reference necessarily shares the specified native key-hit policy, whose known discrepancy is preserved rather than declared correct against CSS publication semantics.
