# Independent escaped-newline capsule review

## Verdict

**APPROVED_NARROW_FORMAL_SOURCE_COMPONENT.** No blocker found for the proposed predicate correction and its stated source/specification correspondence. Native application, build, candidate browser and regression acceptance remain root gates. Full name/escape parsing, caller-state reachability and whole lexer correctness remain open. This verdict does not supersede the separate broader proof scope.

The producer FREEZE is 6881694a18d5877b096c5daa107e0e091c6ebf450aba234832d3daf856fabb5e and its MANIFEST is f92c56cbf00c8f8e9b6adbc5d9edb7bac6895e2f12c6002eaa82d9349a28e176. All 73 entries were authenticated before execution. The complete package is retained under capsule/. Independent review considered the definitions, all proofs, checker, exact source bodies and callers, patch, checksum, WPT and raw baseline; acceptance is not based on hashes or replay alone.

## Proof substance and independence

The native and corrected models faithfully differ only in the offset used after an initial hyphen and backslash. The reference branches on the grammatical first-character cases and defines validEscape using explicit rejected list patterns. It does not call native, corrected, newlineAt or nativeAscii. specStart uses a separate arithmetic proposition. ascii_classification proves the relationship between the two classifications. This is a substantive independent reference at the predicate level, not equality of two aliases or an assumed equivalence.

corrected_reference quantifies over every finite List Nat without a correctness premise. exact_change characterizes disagreement with the old predicate exactly as the three-byte prefix [45,92,c], with c equal to LF, FF or CR. unchanged_outside follows from that characterization. Three bad_admission theorems quantify over arbitrary tails; fixed_rejects handles arbitrary tails and every recognized newline. EOF, lone backslash, missing second/third byte, two hyphens and non-ASCII branches are present. Five examples are supplementary finite checks, not additional universal results.

Eight printed theorem audits were checked afresh. An auxiliary escape_shape theorem is also compiled and its dependencies are covered transitively by corrected_reference. Only propext, Classical.choice and Quot.sound occur in successful audited proofs. Neither source nor successful logs contain a proof hole. The eight retained dispatch audits are a prior component, not eight additional new predicate theorems.

## Source, representation and caller limits

Complete original/candidate tokenizer files establish the sole body change: the nested backslash arm of is_ident_start reads has_newline_at(2); the outer backslash arm still reads offset 1. The guard checks, byte_at, has_newline_at and is_ascii correspondence match the Lean model. The predicate borrows an immutable parser and neither advances it nor allocates.

List Nat is a mathematical representation. Native admission requires byte-valued elements, a valid Rust UTF-8 string, a code-point boundary and valid position, and defined usize additions. Reading non-ASCII leading bytes as ident-start code points and treating NUL/CR/FF consistently with preprocessing is a reviewed mapping, not a separately proved UTF-8/preprocessing refinement. The proof does not admit arbitrary byte offsets or prove every caller always reaches a valid boundary. Rust compiler, primitive arithmetic/indexing and Lean distribution remain trusted tooling.

The at-sign caller advances over @ and selects AtKeyword only if the predicate succeeds. The unchanged consume_name newline check explains why the old false admission produces the short hyphen keyword. StyleSheetParser::next distinguishes that token from a delimiter and resets for a qualified rule otherwise; parse_at_rule admits semicolon as a terminator, whereas top-level parse_qualified_rule uses the curly-block delimiter. These bodies are retained and reviewed. Final selector rejection and CSSOM/style effects are outside the Lean theorem. Hash/IDHash classification, the hyphen token branch and numeric dimension suffix also use the predicate; the exact-change theorem concerns its Boolean result, not blanket preservation of their complete tokens or downstream behavior.

Candidate dispatch extraction preserves all 22 invocation patterns and 5,632 byte decisions. Two enclosing invocation hashes change. The unchanged dispatch theorem governs arm selection; it does not prove arbitrary arm bodies. Manual exact-source correspondence is openly retained rather than represented as a verified Rust-to-Lean translator.

## Specification and diagnostic oracle

Fresh CSS Syntax ED inspection on 2026-10-19 (draft dated 2026-10-16) confirms the narrow oracle: after a leading hyphen, the second and third code points determine escape validity; a following newline rejects it. CR, FF and CRLF normalize to LF. The at-sign therefore becomes a delimiter. Stylesheet parsing takes the qualified-rule path, whose prelude consumes through the following block; the invalid selector is discarded. The buggy at-keyword path instead ends at the semicolon, leaving the following rule. Double hyphen and hex-escaped newline controls are valid distinctions. Verdict: **REACHED**. Sources: [identifier start and valid escape](https://drafts.csswg.org/css-syntax-3/#would-start-an-identifier), [preprocessing](https://drafts.csswg.org/css-syntax-3/#input-preprocessing), [stylesheet parsing](https://drafts.csswg.org/css-syntax-3/#consume-a-stylesheets-contents), [qualified rules](https://drafts.csswg.org/css-syntax-3/#consume-a-qualified-rule).

The WPT sets stylesheet text from JS, preserving the intended CR/FF cases for CSS processing. Four failing rows cover LF/CR/CRLF/FF; seven controls cover double hyphen, ordinary keyword, hex escape and delimiter recovery. Independent raw audit checks all 11 distinct names/statuses, the exact test identity, one OK test_end and suite_end, original tokenizer and WPT pins, and all four stable before/after pins. Failure messages are the rule-count assertion; the later target-color assertion was not reached for those four rows. Baseline binary hashes are receipts, not a new independently verified build provenance claim.

## Mutations, replay and package

A fresh copy under this review directory replayed from relocated paths with no checkout reads, Rust build or browser. The pinned Lean executable is /Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean, SHA256 d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf. Fresh output and all command logs are retained under replay/. Generated .olean files were removed after recording success; replays must compile again.

Restoring the bad inner offset fails decide on concrete newline propositions and the universal theorems. Moving the outer offset fails semantic goals in corrected_reference and exact_change. Independent definitions-only variants with explicit contradictory-to-the-spec witnesses both compile successfully, demonstrating valid syntax and actual semantic changes. Failed mutant logs show Lean's diagnostic sorryAx placeholders; those failed runs are not accepted theorem artifacts.

Two fresh tamper checks reject before Lean: an unhashed proof edit fails manifest authentication; an extra outer-offset source edit with locally recomputed manifest/freeze fails the checker's exact-one-change test. Recomputed manifests intentionally bypass only checksum checking to test the semantic source guard; they are not valid substitutes for the externally pinned producer FREEZE.

Patch application and reversal reproduce complete candidate/original bytes. Only files["src/tokenizer.rs"] changes in the parsed vendor checksum object; package remains null, and the value equals the full candidate file hash. The proposal preserves compact JSON. Cargo/source revision metadata is retained; no vendor refresh, upstreaming or novelty claim is accepted here.

Remaining gates are the producer's stated gates. No additional scope restriction was introduced to make the proof pass.
