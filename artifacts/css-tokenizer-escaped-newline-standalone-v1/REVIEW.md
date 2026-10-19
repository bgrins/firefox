# Escaped-newline standalone applicability

## Verdict

**Approved upstream-specific three-file source patch; no earlier native repair is required by this predicate change.** This is source applicability and reviewed semantic independence. No isolated-base Gecko build or browser run was performed. The accepted Lean component is unchanged and was not replayed again.

Base: `976279105b2e78b8666a959eb3f25c9176cefaf8`; exact Git tree and read-only extraction results are in BASELINE.json. The WPT is absent there. All 73 accepted capsule inputs were authenticated before use.

## Mismatch and provenance

The accepted stack original tokenizer differs from upstream. Its only difference is the earlier bad-URL recovery fix: the unquoted-URL whitespace recovery branch no longer consumes the next byte before calling consume_bad_url. The prior native commit is `83bc2bd3922697d44a602bf48902e821796a60e3` (the companion is `366b0542b5595614895a17e5e334019f0fcf5d20`). Read-only Git extraction confirms that prior native commit's tokenizer exactly equals the accepted escaped-newline original. Retained prior patch, verification and commit metadata document this provenance.

The original/checksum mismatch is real: the already sealed stack patch cannot be called directly applicable to upstream. Fresh attempted application rejects its checksum hunk. The predicate hunk itself matches. The standalone artifact preserves upstream's URL branch and recalculates only its tokenizer checksum after the escaped-newline change. It does not incorporate or duplicate the URL repair.

## Exact inventory

| Path | Change |
| --- | --- |
| third_party/rust/cssparser/src/tokenizer.rs | Only the nested hyphen/backslash lookahead changes offset 1 to 2 |
| third_party/rust/cssparser/.cargo-checksum.json | Only the tokenizer file hash changes; package and all other entries remain unchanged |
| testing/web-platform/tests/css/css-syntax/identifier-start-escaped-newline.html | Add the byte-identical accepted 11-case WPT |

`fix-upstream-v1.patch` SHA256: `1890e4836a868730cba61df19bfae2c8eb76fcb4735ef4e2ba6299cfaf36f2bb`.

Source hashes and null original for the new WPT are in IDENTITIES.json. Complete extracted upstream, original and candidate files are retained. This patch applies with zero fuzz and no offsets, yields exactly the three candidate files, and reverses to exactly the two upstream files with the WPT absent.

## Why the earlier fix is not a semantic prerequisite

The complete original is_ident_start body equals the one reviewed and modeled in the accepted capsule. The complete standalone candidate body equals that capsule's corrected predicate. The entire upstream-to-stack source difference is the retained URL recovery hunk; neither the predicate, its byte helpers nor its direct callers changed. The isolated repair does not execute that URL branch or depend on its modified return handoff. The WPT exercises at-keyword versus delimiter/qualified-rule recovery and contains no unquoted URL input. Both original and candidate body equality are enforced by the replay checker; the source delta is also restricted to the single offset replacement.

The appropriate distinction is a checksum text conflict, not a required earlier parser fix. Root may retain a standalone commit on this exact upstream base plus the stack integration commit, recording that each changes the same predicate and exact WPT while each checksum reflects its own complete tokenizer bytes. Root owns signing and ledger linkage. This review neither edits either branch nor creates a commit.

## Limits and replay

Run `python3 check.py` after authenticating FREEZE.json. It validates retained hashes, predicate transfer, the minimal source/checksum delta, exact WPT, fresh apply/reverse and expected rejection of the original stack checksum patch. It uses temporary directories and no live source, Git/index mutation, build or browser.

The prior formal/source review remains conditional on admitted parser state, UTF-8 and primitive/compiler behavior. Full name/escape correctness remains open. No runtime claim is transferred from the stack to an isolated upstream build.
