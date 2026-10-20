# Fix81 independent native/test checkpoint

Source and37-case oracle approved for runtime evaluation; candidate runtime/build gate pending. Exact inputs retained in INPUTS.json; predictions independently enumerate the10 original failures and37 candidate passes. Formal gate is separate and not yet reviewed.

## Source

Full diff removes generic component/list boundary guesses and computes actual boundary classes from the single serialized CSS string. Universal values retain their exact early-return clone. Empty typed serialization leaves Nothing/Nothing. Lists naturally derive separate first/last classes. Whitespace is returned and retained in the summary; comments are skipped by next_including_whitespace. Quoted strings remain atomic. Function and all three block openers receive finalOther, because subsequent Parser calls consume the nested block and its close before returning a sibling orEOF. Balanced valid typed serialization is the source premise; this is not an arbitrary malformedCSS recovery validator. No global separator/equality/taint/payload arithmetic changes.

The initial nativev1 attempt failed compilation because the Parser destructor retained a borrow ofcss across its move. v2 explicitly dropsinput before constructing the untyped value; the sole candidate delta is this lifetime fix. This failure is retained and excluded from successful build evidence.

Cost: one additional tokenizer pass over the already-existing serialization, linear in emitted bytes with nested-block skipping. Nested block traversal uses the parser's explicit stack, whose storage grows with nesting; this is not a proved constant-memory or allocation-free operation. No performance benchmark or page-level impact is claimed. This avoids repeated serialization and exhaustive variant-specific boundary prediction.

## WPT oracle

Twentyfont cases =10inputs×direct/chained. Parentfont100px calibrates failed inheritance against target20px/25px. Each typed provider is checked before substitution, andfontFamilyserif verifies a separate identifier. Twelve margin cases =6inputs×direct/chained. The200px containing block makes10% resolve20px, andcalc(10%+1px)21px; three-valuemargin syntax assigns second value to right. Nonauto rightmargin does not become the balancingauto side. Five leading@ cases supplydelim@ through its ownvar, then concatenate with the typedvalue's tokens; function starts require a comment, numeric starts do not (extra comments permitted by the assertion).

Reject ALL five leading@ cases of expanded-v1: literal@var(...) tokenizes as an at-keyword plusblock, not a varfunction. Their failures are invalid fixture evidence. v2 corrects only the construction with--prefix:@ andvar(--prefix)var(...). v2 raw records independently match its receipt:37unique names,27PASS10FAIL. The installed landingWPT exactly equals v2. Existing v1 font/margin results are not used to establish final pairing.

Spec basis: prior independent token oracle's pinned Properties§2.7, Syntax§9 andFonts fontgrammar; Box3 marginshorthand andCSSOM resolvedvalues establish newmargin assertions. @+function differs from@+dimension/percentage according to Syntax tokenization/serialization table. This review neither requires exact comment spelling nor infers actual substitution fromCSS.supports alone.

Remaining: finalcandidate rawpair, buildreceipt, stablepins, minimal standalone patch application/source delta, frozen formal component/replay. No production/WPT edits, browser/build/Git actions performed by reviewer.
