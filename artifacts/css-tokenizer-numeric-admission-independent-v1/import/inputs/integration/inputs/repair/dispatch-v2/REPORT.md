# Resolved tokenizer admission: optimized byte dispatch

## Result

A concrete intermediate proof now ties the optimized byte-dispatch algorithm to **all 22 actual source invocations**: 19 tokenizer invocations and three serializer invocations. No discrepancy was found in their current patterns. The proof is about the procedural macro's table construction and source-selected arms, not an algebra over supplied CSS token lists. It removes the conditional assumption that these current optimized byte patterns choose the same arm as the unoptimized scanner harness, subject to the explicit Rust macro/compiler representation boundary below.

`ByteDispatch.lean` models `parse_pat_to_table`'s per-byte `get_or_insert` and `match_byte`'s forward arm enumeration. For any finite arm list, initial table, starting ID and byte, the completed table retains an existing entry or selects the first matching arm. Fresh-table equivalence, prior-entry preservation and selected-ID bounds follow. At most 256 arms prevents u8 case-ID truncation. Inclusive range coverage matches the actual proc macro's lo..hi loop followed by its explicit hi entry.

`extract.py` reads complete retained Rust sources, discovers actual macro invocations, records full invocation/body hashes, and strictly parses byte literals, inclusive ranges, OR patterns and wildcard/binding patterns. Unsupported patterns and a second named binding in the same invocation are rejected. An independent textual matcher classifies original pattern text directly by byte-string comparisons rather than using the lowered numeric ranges. Its byte-literal decoder is separately written from the explicit Rust escape grammar; it does not reuse the AST path’s Python literal evaluator. Its 5,632 byte decisions must agree with the constructed tables. Generated Lean then kernel-checks each exact current table and instantiates the universal construction theorem. The source inventory includes nested invocations and rejects missing/extra invocations against the audited count.

At most one named binding occurs per invocation. No arm guards or exclusive ranges occur in the bound 22 invocations. Named wildcard bindings occur and match the source macro's single evaluation/binding branch. The macro copies arm bodies unchanged; token semantics inside those bodies remain separate obligations.

## General macro boundaries

The actual macro does not inspect `syn::Arm::guard`, and handles a range's hi endpoint inclusively without inspecting `RangeLimits`. Hypothetical `b'a' if false => ...` and `b'a'..b'c' => ...` therefore do not have the same semantics as ordinary Rust match. Named kernel witnesses retain both distinctions. They are not current tokenizer counterexamples and are not reported as a browser bug. Future source changes using them must fail this admission rather than inherit its approval.

The extractor is a narrow source reader, not a verified Rust parser. Two independent pattern interpretations, exact complete source hashes, explicit supported grammar and kernel-checked tables reduce shared lowering risk; they do not prove syn parsing, quote emission, Rust compilation or machine memory semantics. `first` uses ordinary mathematical byte range predicates; the table construction theorem does not supply correctness of tokenizer output, unit classification or arbitrary-substitution recognition.

## Restart/progress audit

See `ADMISSION.md` for the complete provider ledger. Fresh parser state suppresses public block skipping and cached-token reuse. Source inspection finds token classification dependent on remaining input bytes and relative cursor, while line/column/source directives are observation state. Critical obligations remain: native helper progress under real entry conditions; UTF-8 return boundaries despite temporary interior-byte positions; owned escape-buffer validity; numeric/name/URL composition; and defined native arithmetic.

The general claim that every helper consumes a byte is false (quoted URL lookahead deliberately does not advance). The general claim that `advance` always preserves a scalar boundary is false. The valid scanner proof must reason about full token return, inherited prefix progress and actual caller predicates. Similarly the substitution push size guard is not a proven global bound on every persisted string.

This capsule does not extend the selected-output model's completion claim or assert universal native tokenizer admission. No native compile/build/browser/WPT/Git work was performed. Parent scanner/browser evidence remains separate and immutable.

## Reproduction

Authenticate FREEZE.json against the handoff digest. Run `python3 check.py --lean /absolute/path/to/pinned/lean --output /new/output/directory` from this directory (or supply its path from another cwd). The checker authenticates all source inputs before helper execution, regenerates the independent source classification and generated Lean, compiles both modules in the output directory, audits theorem dependencies and checks two semantic table mutants are rejected. It requires Python 3 and the pinned Lean distribution; no network or Rust toolchain is required.

The next useful step is complete source-bound name/escape return-boundary refinement, not additional finite token-list counts. `ADMISSION.md` states the exact component sequence and remaining source/compiler assumptions.

## Version 2 correction

See DELTA.md for the independent reviewer’s two-binding admission counterexample, retained version 1 evidence, the new rejection gate, and corrected UTF-8 source offsets. The proof and original Rust source are unchanged.
