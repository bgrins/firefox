# Independent name and escape component review

## Verdict

Accept the sealed component as a conditional model result for its original source snapshot. The fresh independent replay passes. No false theorem or mismatched modeled branch was found in the nine modules and 21 retained native definitions reviewed. This is not acceptance of complete native tokenizer refinement, unsafe UTF-8 construction, or the current repaired caller.

The independent reference is substantive for name classification, maximal hex-prefix selection, six-digit arithmetic, scalar replacement and optional whitespace. Output bytes, consumed length and remainder are universally equal in the model. The model also proves fast-prefix fusion, bounded consumption, returned cursor markers, complete-unit suffix preservation and original identifier guard progress. These are useful contracts rather than finite test counts.

## Evidence

The imported manifest and all 77 entries were authenticated before any helper execution. A clean relocated replay produced nine modules, 48 standard-axiom reports, 21 exact complete native bindings, four rejected semantic mutants, and the embedded dispatch replay of 22 invocations and 5,632 byte decisions. Only propext, Classical.choice and Quot.sound occur in the audited theorem dependencies. The pinned Lean executable is checked; its surrounding installation, kernel and standard library remain trusted tooling. No native compilation or browser execution was performed in this review.

The four rejected mutations independently exercise continuation-byte acceptance, NUL replacement, CRLF consumption and the six-digit limit. The codec diagnostic deliberately changes the shared ASCII encoder from n to n+1; all nine modules still compile. This is an expected demonstration of the explicit shared-primitive boundary, not a newly discovered Firefox defect. Both initial and repeatable diagnostic commands are retained.

## Source and semantic review

`HexPrefix` compares arithmetic classification and recursion with a literal digit table and maximal-prefix selection. Its six-digit bound fits u32. `Escape` separately compares scalar validity and optional-whitespace handling, including raw CRLF consuming two bytes. Its `encode`, first-byte width calculation and nonhex byte copy are shared between the native-shaped and semantic sides: Rust chars/len_utf8/encode_utf8/from_u32 equivalence is assumed, not proved.

`Name` models the borrowed loop, transition to owned storage, ordinary-byte copying, NUL replacement and invalid-escape termination. Native allocation occurs before discovering a backslash-newline stop, so an owned result with zero consumption is faithfully represented. `SemanticName.project` discards the ownership bit. The universal semantic theorem therefore covers bytes/count/remainder, not an independent ownership semantics. Concrete ownership witnesses and source review do not change that boundary.

The byte model permits temporary positions inside UTF-8 sequences. The retained two-byte witness demonstrates why each fast prefix cannot be assumed to end at a scalar boundary. Returned marker and complete-unit lemmas repair that reasoning at the proper boundary. The structural `Boundary.Unit` predicate is weaker than valid Rust UTF-8: it admits some invalid leading-byte shapes. Its suffix theorem is useful but is not a proof of String::from_utf8_unchecked safety or output UTF-8 validity. Valid initial Rust str, decoder/encoder behavior, valid slicing positions, allocation success and compiler behavior remain native admissions.

The complete copied advance/slicing/escape helpers were inspected. Mathematical bounds do not alone establish defined usize lookahead additions. Metadata exclusion also does not remove normal-completion requirements: ParserState::advance_line_number performs ordinary u32 addition of count shifted by two. Escape whitespace can reach this update. Native execution needs metadata headroom or an explicit normal-return premise. The embedded dispatch admission ledger already records this headroom; it is inherited here. No new overflow bug or runtime failure is claimed.

## Original guard and current-source integration

The sealed tokenizer SHA is 9e46cbb4fc239301dc786cb76b3355b6d8c1ea2d19f845f142db8a6bca020b4f. Its original is_ident_start incorrectly checks offset one after hyphen-backslash, admitting a following newline. The theorem original_ident_progress remains true: consume_name consumes the hyphen before stopping at the invalid escape. Progress does not establish correct token classification.

The current offset-two repair is not bound by this original-source capsule. A separately sealed corrected-approval-to-original-approval theorem, composed with original_ident_progress/boundary and exact current source binding, is required. The producer is preparing this additive transfer; it is not imported or accepted by this review. Original capsules remain unchanged.

## Spec cross-check

CSS Syntax Level 3, consulted 2026-10-19 (draft dated 2026-10-16), supports six hex digits, optional filtered whitespace, invalid-scalar replacement, and name consumption independent of identifier-start validation. Identifier-start after hyphen must check the following two code points for a valid escape. Input preprocessing and the raw-byte/code-point bridge remain explicit admissions.

Primary sections: [preprocessing](https://drafts.csswg.org/css-syntax-3/#input-preprocessing), [escape](https://drafts.csswg.org/css-syntax-3/#consume-escaped-code-point), [name](https://drafts.csswg.org/css-syntax-3/#consume-name), [identifier start](https://drafts.csswg.org/css-syntax-3/#would-start-an-identifier). This review records a live reading, not an archived normative HTML snapshot or independently authenticated anchor inventory.

## Remaining scope

Whole-tokenizer dispatch semantics, numeric/URL/block token semantics, native codec and unsafe-string refinement, independent allocation/ownership semantics, line/column metadata, machine arithmetic, heap/compiler correctness and repaired-source caller composition remain outside this acceptance. The theorem statements and declared boundaries support the narrower component; they cannot close those obligations.
