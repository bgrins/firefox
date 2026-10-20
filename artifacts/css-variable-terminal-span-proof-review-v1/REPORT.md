# Independent terminal-span review

Verdict: mathematical/source-scope review positive; final checker acceptance withheld pending immutable v2. The v1 unsafe-invocation guard runs after imports, and a local json.py executes before rejection. This is an import-order integrity defect, not a Lean mathematical failure. Native patch and browser gates remain separate.

## Authentication and replay

Externally supplied producer FREEZE and MANIFEST hashes were verified before executing its checker. All 17 manifest inputs were independently hashed and copied into an otherwise empty capsule. The relocated producer replay passed 37 exact theorem audits, ten source bindings and five executable Lean model mutations. These are model mutations, not native Rust mutations.

I read all Span/Witnesses/Mutants definitions, their proofs, the complete source-binding texts, full relevant source functions and both retained source deltas. The independent recheck additionally compares the complete 24 non-Nothing source serialization classes with the model's Kind inventory. Four targeted guards reject optimized Python, twice-optimized Python, changed proof source and an added shadow olean before output creation. Supported invocation is explicitly `python3 -I -S`; external seal authentication is still required. A subsequent unsafe-mode shadow challenge demonstrates that rejecting before output is weaker than rejecting before imported code: see UNSAFE-SHADOW.json. The checker requires a v2 guard-order correction.

`Challenges.lean` adds 23 independent kernel checks: escaped SP/HT with and without true trailing whitespace, hexadecimal-escape terminators, multiple escaped spaces, raw CRLF, comment reset, complete and EOF-open blocks, block opener class, old leading-trim overlap, UTF-8 payload bytes, fallback metadata retention, and counterexamples to missing coalescing/nonempty/EOF premises. The last theorem independently connects the current constructor's actual saturating-subtraction change guard to the model's positive-trailing-length metadata guard.

## Substantive findings

1. **The reference is distinct from the scanner.** The scanner overwrites trailing length on each outer token. The independent reference splits the reversed full token list. Equality is proved under adjacent-whitespace coalescing. The supplied noncoalesced counterexample demonstrates that this premise matters; it is not silently inferred from arbitrary lists.
2. **Escaped whitespace remains in its non-whitespace token.** Non-whitespace raw payloads may end with space/tab bytes. `exact_prefix` removes the raw payload of the final whitespace token only. Hexadecimal escape terminator whitespace is similarly preserved when it belongs to the identifier token. Actual source `consume_whitespace` returns a raw input slice; `consume_newline` advances over both CRLF bytes. No normalized-one-byte assumption is used.
3. **Comments and outer blocks reset the terminal count.** Source assignments occur before recursive block processing and use the outer token class. The nested result does not replace the enclosing scan's summary. The model correctly uses DelimSlash for comments and Function/OpenParen/Other as appropriate for outer blocks. It makes no claim that those opener summaries equal the flattened closing class or are universally sufficient for separators.
4. **Metadata correction is bounded correctly.** For the current constructor, `trim_bound` makes actual shortening equivalent to positive terminal whitespace extent; the independent guard theorem confirms this arithmetic connection. Positive raw token payloads are necessary for `metadata_last`. InitialReady excludes a retained initial whitespace class after current initial-token normalization. For older standalone code that already dropped a leading prefix, `leading_overlap` proves bytes only. In the all-whitespace overlap case the native correction branch need not match abstract lastMetadata; the producer does not claim standalone metadata equivalence there.
5. **EOF compatibility is conditional and visible.** EOFReady requires a non-whitespace final outer token when repair changes the input; then trailing count is zero. I tested quote-backslash deletion, comment completion and open-block completion. An intentionally invalid EOF provider with a final whitespace token makes the closer disappear, confirming that the premise cannot be dropped. Choosing valid EOF repair and proving native reference endpoints remain bounded are outside this component.
6. **Fallback and residual behavior remain separate.** The native fallback stores first/last and discards the added summaries, so no trimming is introduced inside fallback chunks. The backslash-delimiter/newline witness still loses its newline. That residual prevents promoting this proof to general retokenization, serialized-token equivalence, or complete CSS correctness.

## Source/version boundary

The final source hash is `8f166d5cbd25d298a34d820e148c8967d3b0b0fc009a371831d4e4be336548d7`. The preceding metadata candidate and the pre-metadata e3c5 origin candidate are distinct retained full files. The source diffs contain the expected additional summary fields, per-token assignments, constructor use and fallback tuple discards. No changed source hash is presented as proof of translation.

The ten bindings retain complete function bodies; one includes an adjacent documentation comment as well. Their byte spans/hashes agree with the full retained source. Kind's none state represents Nothing; actual non-Nothing classifier correspondence and raw outer-span construction remain source admissions. UTF-8 token boundaries, machine capacities, allocation/compiler/runtime, parser cache/error behavior and native invocation composition are not mechanized here.

## Conclusion and replay

No mathematical blocking issue was found for the claimed component. Checker acceptance is blocked by the reproduced pre-guard shadow import in UNSAFE-SHADOW.json. Producer v2 must move the explicit mode guard immediately after builtin sys and add a negative control. The mathematical component establishes a useful conditional terminal-byte/outer-class invariant for the two repairs. It cannot close the origin component's tokenizer/EOF providers, the source-to-Lean translation, or the outstanding backslash-newline serialization question.

Run this review from its retained authenticated capsule:

```
python3 -I -S recheck.py --output /absolute/absent/external-directory
```

The review checker authenticates the externally pinned producer, replays its source-only Lean checks, kernel-checks the independent challenges and verifies the class inventory. The review's own files must be authenticated against the separately handed-off FILES/FREEZE hashes.
