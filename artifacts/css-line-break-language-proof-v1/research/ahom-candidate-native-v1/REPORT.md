# Independent Ahom UTF-16 candidate replay

## Result and identity

Pinned root candidate line.rs SHA a511212ad35e22fa96ae107063c5107fd9c2eb3cdd173a1f28e3307306bd11a4, obtained from css-ahom-lf-partition-probe-v1/native-candidate-v1. No live native source is used. Original SHA 08351143911687809801ab86c1c806bca963450c39e6eb6c89872e5ed928d28e. All source outside the complete Utf16 LineBreakType implementation is byte-identical; a checked five-replacement description binds the complete delta. The actual RuleBreakType::char_len definition is retained and checked.

The fresh original source replay reproduces both frozen diagnostics. The repaired ICU source is built offline in a separate generated source tree with only line.rs and its derived Cargo checksum changed. Original and candidate dependencies, native definitions, callbacks, sink identities, locale manager/loading and provider adapters remain identical. No root build/browser/Git operation is performed here.

## Fixed corpus results

- All six existing ICU fixtures agree between UTF8 and UTF16 scalar positions for Normal and BreakAll after repair. Every UTF8 output and every previously agreeing UTF16 control is unchanged. The exhaustive existing SA-domain enumeration is unchanged.
- The five existing complete Gecko provider queries agree with the independently indexed ICU results. Original output matches retained exact evidence.
- Both original and language-candidate complete nsLineBreaker executables retain all 1,284 existing stream traces byte-for-byte under the repaired ICU provider.
- The existing six LF fixtures run under both complete breakers. Every BMP trace is unchanged. Ahom whole/after-LF becomes 0101001; before-LF becomes 0101111. Thus second-CJK offset 6 is restored, while differences at LF offset 4 and initial boundary offset 5 remain explicit. Callback folding independently reproduces final glyph storage; exact provider requests are unchanged. All calls succeed.

No matrix was expanded. Three direct provider requests used by the already retained kernel witness are queried freshly against the candidate actual Gecko provider: 1101, 11, 1101111.

## Formal bridge

Utf16Repair.lean contains 11 standard-axiom theorems: positive width, encoded length, BMP preservation, supplementary scalar reconstruction and surrogate-unit bounds, arbitrary-run length, recursive seek coordinates, arbitrary prefix boundary reachability, strict scalar progress, and concrete Ahom coordinates. Valid Unicode scalar admission is required for the encoding interpretation; the total helper outside that domain is not the Rust replacement-character behavior.

The adapted full streaming witness compiles with all 15 original model modules and 80 theorem reports. Only provider answers and consequent exact target claims change. Its generated driver matches independently queried native provider answers and both complete native final vectors. The candidate theorem asserts the second-CJK opportunity in both partitions, not equality of every raw bit.

These are universal pure encoding/coordinate lemmas plus a kernel-checked full-model witness and bounded complete-native correspondence. They are not a proof of Rust std::char encoding, the compiler, C++ heap/lifetimes, every segmentation provider answer, all CSS behavior, or unconditional LF locality. In particular, provider offsets must be monotone, in range and scalar-aligned; the narrow repair does not validate arbitrary malformed provider offsets. Actual SA admission excludes invalid surrogate values; unpaired-surrogate replacement is not asserted to preserve arbitrary UTF16 inputs.

## Source-only reproduction

Run `python3 check.py --manifest-sha <MANIFEST SHA256> --replay` from this capsule. All source dependencies authenticate before helper execution. Reproduction rebuilds original offline Rust/ICU/native providers and complete breakers, builds corrected ICU separately, relinks complete native variants, runs the fixed evidence and both Lean gates. Generated objects are excluded; tool identities and system SDK assumptions are checked by the retained parent source checker. `check.py` without `--replay` authenticates and verifies the exact source delta.

## Review boundaries

See the separate ahom-lf-adjudication-v1 research capsule for current primary spec trace, upstream #8144 structural duplication, #8143 cache optimization distinction and browser oracle review. The root paired browser/build gate remains separate. This supplement does not alter frozen language/ownership baselines or silently revise any failed original formal obligation.
