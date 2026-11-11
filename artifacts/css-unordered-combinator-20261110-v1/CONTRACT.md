# Proposed contract before proof implementation

Primary basis: CSS Values4 source f43d8bfcfdfd073cdf6d87f626a6831e1507dc8a (latest file-specific revision observed2026-11-11UTC); exact combinator, multiplier and pattern sections are pinned. The rendered current Editor’s Draft agrees on the reviewed rules. webspec-index0.14 refused its readonly cache; its diagnostics are retained, and public primary GitHub source plus rendered draft were used without changing the host tool/cache. Version0.15 is available, but no update was made.

## Supported first contract

An unordered group has at least two indexed component occurrences. A match chooses a nonempty subset of those occurrences, uses each chosen occurrence at most once, puts the chosen components in any order, and concatenates one complete match from each chosen component. Components remain contiguous chunks. Equal component texts still have distinct occurrence identities; this is not keyword deduplication.

The first public decoder/interpreter will reject an unordered node if ANY complete child grammar is nullable. It will not silently discard an empty child match or count an empty optional match as present. This is a supported-domain restriction, NOT a claim that CSS rejects nullable operands: CSS Values explicitly lists `A? || B? || C?` as the zero-or-more pattern. Optional subexpressions within a required, nonnullable child remain possible (for example `a? b || c`). Full nullable-operand semantics is deferred.

Grouping is significant: `a || b || c` is one n-ary group and admits `b a c`; `a || [b || c]` has a nested component and must reject that interleaving. Do not implement a flat chain as binary association or flatten explicit brackets. Precedence is juxtaposition above `&&` above `||` above `|`; this revision adds only `||`, so `&&` continues to cause an explicit refusal. `?` remains a multiplier on the preceding component/group.

The formal interface can lower the validated operator to the existing finite keyword/alt/seq/optional Grammar, reusing its established run/Matches laws. A structurally recursive ordered-subset enumerator (no arbitrary fuel) should correspond to an independent relation selecting distinct component occurrences. A semantic theorem connects operator matching and exact input/remainder to the lowered grammar. The opt-in postfix opcode carries arity; decoding requires arity≥2, enough stack operands and nonnullable complete children. An old-op embedding/compatibility law preserves the previous interpreter. This avoids changing the historical AST, parser or proof files.

## First property and oracle

Use the already frozen CSS Text3 source e2a76bde01e77f714a8f22e9866d8c636b482a6f. Its text-transform Value is `none | [capitalize | uppercase | lowercase ] || full-width || full-size-kana`. Parse it as `none | (caseChoice || full-width || full-size-kana)`. The three component groups are nonnullable. The independent expected normalized-token language has 38 sequences: singleton none, five non-none singletons,14 two-component permutations,18 three-component permutations. This oracle is recorded before any new recognizer implementation. It must reject combined none, two case choices, repeated full-width/kana, empty input and trailing tokens.

Display remains outside this slice: its list-item production uses unsupported `&&`, and typed productions/other absent contexts must be refused rather than approximated. No display-conformance claim follows from supporting its outer `||`.

## Planned controls and limits

Preserve historical extractor bytes and all old accepted fixtures/results. New support is opt-in; the old text-transform double-bar refusal remains recorded. Controls cover malformed arity, unknown op, repeated index selection, empty selection, missing permutations, wrong precedence, bracket-flattening, nullable operands, unsupported `&&`, source/anchor drift and exact remainder consumption. Each claimed semantic mutation must compile and be contradicted by an unchanged law or checked witness.

All inputs are normalized keyword tokens, not raw CSS; escaping/case-folding, implicit CSS-wide values, variable substitution and text-transform’s rendering semantics remain outside. The kernel will establish properties of a chosen operator model and data program, not correspondence to CSS prose, Python source extraction or the raw JSON text parser.
