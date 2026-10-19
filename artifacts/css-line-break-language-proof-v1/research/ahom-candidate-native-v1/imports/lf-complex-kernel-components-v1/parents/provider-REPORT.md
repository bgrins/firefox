# Mixed Thai/Ahom complex-cache encoding counterexample

## Result and limits

The exact pinned ICU provider returns different scalar boundaries for the same well-formed text encoded as UTF-8 and UTF-16. For U+0E01 U+11700 U+0E01, UTF-8 boundaries map to scalar offsets [0,1,2,3]; UTF-16 maps to [0,1,3]. Its raw UTF-16 offsets are [0,1,4], omitting the boundary at offset 3. Three of six normal fixtures diverge. All six BreakAll controls agree; BMP-unknown replacement and Ahom-only normal controls agree.

The complete pinned Gecko ComputeBreakPositions/cache/options extraction returns 1100 for default Auto, an identical cache-hit call, and explicit Normal. BreakAll returns 1101; BMP-unknown replacement returns 111. Scalar comparison derives offsets from independently encoded input, not literal desired output. UTF-8 is a consistency comparator, not a complete CSS linguistic oracle. No browser run, platform font result or normative CSS conformance claim is made.

## Cause and provider admission

The pinned actual Baked trie assigns SA to 758 scalar values, including 52 above U+FFFF in Ahom. Therefore the UTF-16 complex handler's stated BMP assumption cannot be admitted universally. It casts each decoded scalar to u16 and its initial seek increments by 1. The complex query becomes [0E01,1700,0E01], with slice-provider boundaries [1,2,3]. At the first boundary, the saved relative cache is [1,2]. The generic next-call cache loop uses original UTF-16 character widths: Ahom advances 2 units, overshooting target 1; the loop reaches EOF and clears the cache. The missing Thai boundary follows this unit mismatch. Complete source and actual provider data support this trace. The Lean witness checks the cast and cache arithmetic, not LSTM linguistic accuracy.

Gecko normal/Auto calls the default ICU auto segmenter; explicit Normal uses the LSTM constructor. Both reach segment16 without a BMP restriction. The witness is in the successful uint32/int32 domain. Thai at the first cache probe enables caching; repeated computation preserves the vector. nsLineBreaker can buffer the uninterrupted UTF-16 word and dispatch through the same provider. Full caller/browser publication has not been executed specifically for this witness.

The checker authenticates the imported bridge before helpers execute, builds vendored ICU offline, rebuilds both Rust diagnostics and the complete Gecko provider with UBSan, and audits the Lean witness. System ICU4C script lookup and standard Gecko container facades remain explicit. The driver differs from the early immutable bridge only by an extra sentinel allocation and accepting empty input; these five fixtures are nonempty. Its exact diff is retained. The bridge's incomplete-boundary description remains. This diagnostic does not complete the original language or added LF scopes.

## Bounded prior-art check

A search on 2026-10-19 found no exact Ahom issue, which is not proof of novelty. The [complex-cache allocation refactor, commit fb5e25f](https://chromium.googlesource.com/external/github.com/unicode-org/icu4x/+/fb5e25f59bb1addb8da87d592ecb810923383257%5E%21/) changes cache representation and still describes a BMP complex run. A later [borrowed-slice refactor, commit a9cbb9c](https://chromium.googlesource.com/external/github.com/unicode-org/icu4x/+/a9cbb9cda7cc0b1e832ace6a0f633fc6a3f3726d%5E%21/) is a possible upstream fix dependency because it avoids reconstructing the query. It has not been built against these inputs. Cached current-main views were older and still contained the cast; they cannot establish current upstream status. [ICU4X issue 8381](https://github.com/unicode-org/icu4x/issues/8381) discusses newer engines generally, not this exact counterexample. Duplicate/update/backport adjudication remains open.

## Next gate

Root can independently confirm the provider outputs, then run a calibrated browser probe with the mixed string, reversed script order, BMP replacement, Ahom-only and BreakAll controls. Measure scalar glyph positions and intrinsic size using explicit glyph coverage; fallback widths must be calibrated. A geometry difference alone should not choose a normative Thai/Ahom word boundary. An upstream encoding-equivalence test and source correction/update may be the clearest contract. Any repair is separate from the language-only patch.

The cache theorems retain explicit aligned/bounded provider premises. This witness refutes unqualified instantiation for all complex UTF-16 inputs. It is not filtered out, and no final language/consumer acceptance follows.
