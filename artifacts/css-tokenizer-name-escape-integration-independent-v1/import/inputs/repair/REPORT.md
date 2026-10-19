# Escaped newline after an identifier-leading hyphen

## Finding and proposed repair

`is_ident_start` in cssparser checks `has_newline_at(1)` inside its hyphen/backslash arm. Offset 1 is the backslash already selected by the inner match. The escape is valid only when offset 2 is not a newline. Change that one nested call to `has_newline_at(2)`; the outer backslash arm must remain at offset 1.

The root browser baseline has four failures and seven passes. LF, CR, CRLF and FF after `@-\\` incorrectly leave one following stylesheet rule alive where the independently derived expectation is zero. Each failing callback stops at the rule-count assertion; the baseline does not separately observe its later color assertion. The file itself finishes OK. All four input pins are unchanged across the run. `evidence/browser` retains the raw log, parsed result, console log and source/WPT/binary pins. Candidate build and paired browser acceptance remain root gates.

## Narrow proof

`lean/IdentifierStart.lean` models the complete original and corrected predicate, including EOF, both backslash arms, leading hyphen, NUL, ASCII and non-ASCII dispatch. Its independent reference follows the CSS identifier-start grammar and an explicit valid-escape pattern definition. The independently written ASCII classification is related by an arithmetic theorem, not assumed identical.

Eight kernel audits establish classifier equivalence, three original wrong-admission families with arbitrary suffixes, corrected predicate equivalence to the reference for every finite input list, the exact changed-input family, preservation elsewhere, and rejection of every newline in that family. The changed-input theorem is exact: native and corrected differ if and only if the input begins with 45, 92 and one of 10, 12 or 13. Both predicate mutants (restoring the bug; incorrectly changing the outer escape offset) fail compilation of the theorem suite. Only standard Lean axioms occur.

The complete predicates and byte helpers are retained in both source snapshots. This is a reviewed source-to-model correspondence, not a verified Rust compiler or a general Rust-to-Lean translator. The finite-list theorem uses natural-valued bytes; source admission restricts them to bytes and requires a valid UTF-8 Rust string at a code-point boundary, valid parser position and defined `usize` additions. Non-ASCII input at that boundary starts a non-ASCII code point; NUL is represented as a name-start after replacement preprocessing. CR/FF/CRLF preprocessing agrees with the modeled escape rejection. The predicate makes no state changes and allocates nothing.

The signed dispatch-v2 capsule is retained unchanged and authenticated before execution. Candidate extraction rechecks all 22 invocations and all 5,632 byte decisions. The two containing invocation-body hashes change, while every pattern, arm decision and generated Lean dispatch declaration remains identical. This is a new candidate admission record; it does not rewrite the signed source hashes.

## Packaging and vendoring

`native.patch` contains the tokenizer hunk and its `.cargo-checksum.json` entry. The checksum package field remains null. Only the `files["src/tokenizer.rs"]` value changes; its value is derived from the complete candidate bytes. Patch application and reversal are checked on copied original files. Root can combine the unchanged WPT into a three-file native/checksum/WPT commit after its build and paired test gates.

The repository pins cssparser 0.38.0 to servo/rust-cssparser revision `9f3ceddf398f5ce4ab76fdad1b42ccb6c578a926`. Cargo.toml, Cargo.lock and Mozilla's vendor script are retained. The vendor script writes compact checksum JSON; this proposal preserves that representation. A narrow local vendor repair needs the exact checksum update. Running `mach vendor rust` here would refresh the pinned package and is not part of this proposal. Upstreaming or changing the Git revision remains separate work; neither is claimed performed.

The current upstream master source retrieved through the web still contains the same nested offset 1. Its retrieval is not an immutable revision or a search of all upstream issues. GitHub issue/PR search was unavailable, so duplicate status remains unknown. No external report was filed.

## Completion boundary

This capsule is a narrow predicate repair proposal with source correspondence and a confirmed browser baseline. It does not close consume_name/consume_escape return-boundary refinement, arbitrary parser-state admission, full tokenizer correctness, stylesheet recovery verification, allocation/compiler correctness, or the broader CSS formal roadmap. The larger name/escape artifact remains separate and open. The browser recovery oracle has a static normative and actual-call trace; it is not substituted for a universal parser proof.

Remaining acceptance gates: independent review, root application/build of the exact source/checksum candidate, paired candidate WPT and relevant existing CSS Syntax regressions, and final source identity checks. The root owns those gates and commits.
