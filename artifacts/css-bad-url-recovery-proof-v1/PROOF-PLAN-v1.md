# Recovery suffix proof plan

This is a proposed companion, not an executed proof. The source bug was found
by the syntax survey and reproduced by root before any Lean work.

## Contract

Prove equality of the remaining input suffix after bad-URL recovery, including
the handoff from consume_url_end. Equality of BadUrl token classification alone
would miss the defect: both versions return that token while consuming different
declarations. Keep the consumed source slice and cursor effects observable.

Use a specification-shaped scanner over finite Unicode scalar lists and an
independent optimized scanner. The spec recognizes valid escapes, consumes up
to six hex digits plus optional whitespace, and otherwise consumes one escaped
scalar. The optimization only needs to specially skip escaped closing parentheses
and backslashes to preserve the recovery suffix. Prove that skipping other valid
escape content cannot conceal a terminator, with EOF and invalid newline escapes
explicit. Backslash parity should be a derived lemma, not the entire domain.

The handoff must retain the first non-whitespace input character unless it is a
closing parenthesis or EOF. Include counterexamples in both parity directions
and prove the candidate's composed whitespace-plus-recovery result. State how
CRLF preprocessing maps raw byte suffixes to scalar suffixes; do not silently
identify UTF-8 byte indices with Unicode positions.

## Native bridge and bounds

Compile the complete exact original/candidate tokenizer routine and required
cursor/string providers where practical. Prefer a whole tokenizer module with
its actual CowRcStr and macro dependencies over copying just the changed guard.
Pin all dependencies, feature configuration and toolchain. A separate artifact
target directory must avoid the shared browser build's Cargo cache.

Capture token kind and payload, remaining source suffix, byte position, and
line/column state. Exercise borrowed and owned URL paths, all ASCII whitespace,
CRLF, null/Unicode prefixes, valid/invalid escapes, hex lengths and whitespace
terminators, EOF, and literal close controls. Compare the original separately;
expected old mismatches are not candidate acceptance.

Lean proves the explicit scanner/model contract. Finite native differential
replay links source behavior to that contract on tested inputs; it is not a
proof of arbitrary compiled Rust execution. UTF-8 validity, parser entry state,
declaration parsing and browser rendering remain explicit provider boundaries
unless extracted and separately justified.

## Required controls and review

Mutations must catch restoring the premature advance, skipping escaped close,
losing escaped-backslash parity, treating newline as an ordinary valid escape,
and changing token/suffix bookkeeping. Require clean compilation/execution for
semantic mutations, reject diagnostics and added proof axioms/admissions, and
authenticate full-source preservation plus the checksum-only vendor change.

Retain repeatable receipts and a source-only tooling list. Root and independent
replays, scope review and native/WPT acceptance must precede final acceptance.
The companion belongs before the standalone tokenizer/checksum/WPT commit.
