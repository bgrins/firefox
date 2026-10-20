# Source correspondence and provider contracts

## Constructor

`VariableValue::parse` receives a valid parser over UTF-8 text at an absolute offset. The parser is not holding an unconsumed opener from an enclosing `next()` operation. The initial lookahead either consumes one maximal CSS WhiteSpace token or restores tokenizer position and pending-block state; the parser's enclosing stop delimiter is retained, not saved/restored by ParserState. A fixed observer epoch spans lookahead and replay. The full cssparser source is compiled in the witness. The general byte-to-token transition is admitted.

The initial WhiteSpace token covers exactly raw HT, LF, CR, FF and SPACE bytes, including two-byte CRLF. Comments are not whitespace tokens. VT, NBSP and whitespace bytes inside a non-whitespace escaped token are not removed by this step. Normalization.lean formalizes this partition; the native corpus tests representative cases rather than proving the tokenizer's Unicode classification.

## Constructed syntax

Literal fragments and block wrappers are lists of Unicode scalar characters. Byte length is the sum of Lean Char.utf8Size. A recognized reference has positive header length, and a fallback-bearing reference ends in one ASCII `)`. Its header includes the raw bytes skipped before fallback content, including any skipped whitespace/comments. Provider admission maps actual successful parsing to this syntax, preserving nesting and raw contents. Layout, relative positions, ordered outer spans and fallback identity are then derived, not assumed.

The flat reference inventory includes descendants for the universal boundary theorem. `outerSpans` deliberately excludes a reference's nested fallback records from its parent's traversal while keeping references inside ordinary functions/blocks. `FallbackAt` records the actual nested body; the occurrence theorem connects every fallback record to such a body. The native full parser and reference records are checked in finite cases.

Native fallback traversal keeps offsets in the original source. The model's recursive body presentation uses a local origin. ExactFragment, byteSlice and scan_embedding prove textual embedding and the entire scan in original coordinates after prefix-byte rebasing; a full compiler translation of the native references container is not supplied.

## EOF and suffix

The selected completed syntax must correspond to actual EOF repair: appended closing delimiters and, where required, deletion of the terminal quoted backslash. Repair.lean proves common-origin normalization commutes with these operations and proves the adjusted byte-length identity. It does not derive which operation the tokenizer selects. No desired arbitrary final endpoint is supplied as a theorem premise; the completed reference syntax fixes the closing byte. Matching actual EOF parser state to that syntax remains an explicit source admission.

Trimming an outer trailing whitespace suffix is admitted to preserve the constructed reference boundaries. This is not a claim of general serialization equivalence: separately reproduced trailing metadata and escaped-space problems demonstrate why that stronger claim would be false. The origin repair snapshot predates both trailing fixes.

## Substitution and publication

`ReplacementReading` uses decompositions of the actual source into clean/removed pieces and supplied replacements; it does not obtain expected source text from the byte-slicing evaluator. `scanPieces` selects the provider in source order and reads by constructed offsets. The provider returns either failure or arbitrary UTF-8 text plus a provenance bit. Names, DOM values, namespaces, registration and environment resolution are outside the universal component. Provider stability and successful result validity are admitted.

Inserted separator decisions are explicit booleans supplied by the token-class provider; range theorems hold for either decision. The native witness compiles actual TokenSerializationType and VariableValue::push, but does not universally prove class metadata or all separator choices. Source-shaped prefix/replacement/suffix appends are modeled for successful allocation and length checks. `checkedAppend` proves safety of its successful branch separately. The abstract failure result publishes no output; it does not prove equivalence of all intermediate provider calls under allocation or length failure.

The direct whole-reference shortcut is modeled separately, including empty tainted output. The outer collector starts at zero. Nested fallback calls omit a range collector and return aggregate taint; they do not place original nonzero source offsets into the newly serialized output. The independent oracle wraps selected fallback output as one replacement accordingly. The native AttrTaintedRange and AttrTaint implementations are extracted completely. Range safety is not URL rejection or exfiltration noninterference.

## Native adapters

Rust strings/slices, usize arithmetic, memory allocation, compiler and standard library are trusted. The Lean natural-number model requires representable source/output lengths and no machine arithmetic overflow. SmallVec/bitflags/cssparser are compiled from retained sources. Atom, Name, Prefix and Namespace are represented as String; namespace lookup is deliberately unavailable. AttributeType has a restricted facade; actual outer typed-attribute conversion is established only by the root's separate browser gate. ComputedValue aliases the same VariableValue storage in the harness. URL data, stylist, context and property identity are inert admitted providers. The two synthetic name resolutions are explicit and do not claim production lookup semantics.

`substitute_one_reference` is intentionally partial extraction: exact function signature plus native missing-provider/fallback tail, with the preceding native lookup branches replaced by the two declared providers. All other recorded complete items retain their complete source bodies. Actual constructor callers are copied for source inspection; they are not silently represented by compiled stubs.

## Mutation interpretation

Four native variants compile and run. The oracle verifies the exact named counterexamples and full candidate rows. Kernel witnesses separately exhibit late-origin overflow, lost initial opener, retained comment loss, and byte/character mismatch in the abstract domain. The cache lemma is same-epoch Boolean observation idempotence only. It does not establish arbitrary cache provenance, metadata histories, or epoch-reset correctness.
