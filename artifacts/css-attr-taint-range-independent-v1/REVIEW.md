# Independent endpoint range review

## Verdict

**Accept the one-expression source proposal and its bounded interval proof component.** No blocking source, mathematical or final seven-case oracle issue was found. Candidate browser/build acceptance remains root-owned and is not inferred from this review. The separate animation finding is outside scope.

The correction uses `max(start) < min(end)`, retaining the existing any-over-taint-ranges loop. It performs only machine comparisons/selections: no new addition, subtraction, indexing, string slicing or allocation. For correctly located byte spans, it removes old false positives from touching/empty intervals while preserving every genuinely shared byte. It does not change computed-value taint flags or substitute resolution policy.

## Normative and source chain

Current CSS Values 5 attr security requires URL taint rejection, including taint propagated by an entire arbitrary substitution. It also explicitly permits a literal URL near a tainted non-URL argument. Applying that distinction to image-set's separate URL and resolution is the relevant spec inference. CSS Images 4 defines the image reference and optional resolution as separate option parts. Neither rule requires the URL to become tainted merely because the following resolution begins at its exclusive end.

Complete producer/caller sources retained in source/ were inspected after Searchfox discovery. `VariableValue::push` skips empty CSS; otherwise it inserts any token separator before recording start, appends bytes, and records end. Thus ordinary taint ranges cover actual appended bytes and exclude inserted comments. `new_fully_tainted` can produce [0,0). The whole-reference optimization in `do_substitute_chunk` records start and substitution length; the public range-recording path through `substitute_internal` supplies start0. Recursive fallback and unresolved-variable recursion pass no range accumulator. This bounds the suspicious nonzero-start arithmetic rather than treating it as repaired by an overlap change.

`Substitution::into_value` retains whole-substitution taint, including typed computation via a fully tainted region. The patch leaves that logic intact. These manual source facts are not a universal proof of all selected substitution/offset histories or empty-substitution semantics.

The two callers of `CssUrl::parse_from_string` are `CssUrl::parse_with_cors_mode` and `ImageSetItem::parse`. Each brackets successful URL/string parsing with source-position observations. Retained cssparser helpers distinguish unquoted URL, quoted string and quoted url() delegation. Even an empty decoded string has a nonempty raw token span. The image-set consumer queries only the URL/string span before resolution parsing. Leading skipped whitespace can widen that span; this patch does not prove normalization or resolve all whitespace-taint false positives.

## Mathematical review

Read all 14 Lean theorem statements and proofs. Independent interval membership is `start ≤ byte ∧ byte < finish`; the optimized predicate uses max/min. `overlaps_iff_shared_byte` derives equivalence by constructing the maximum start as witness and by proving bounds in the reverse direction. It does not assume the desired shared-byte result. Inverted intervals require no special premise because they contain no byte. Empty, touching, separated and nonempty-contained cases follow explicitly. Finite-list blocking is equivalent to membership in at least one taint region, and concatenation/translation laws preserve the intended semantics.

The natural-number translation theorem has no machine-overflow claim. Native min/max itself adds no arithmetic; interpreting existing usize coordinates as naturals is a simple but explicitly external representation/compiler admission. The proof does not establish SmallVec memory safety, native producers, token parser span correctness, actual CSS grammar or the whole browser pipeline.

## Fresh replay and independent mutation

Externally supplied producer FREEZE/MANIFEST/checker hashes were authenticated before executing any producer code. A copy containing only the ten manifest inputs plus both seals was replayed with Python -I -S. The final checker enforces closed input files/directories, unique JSON keys, no source symlinks, safe input names and fresh resolved output containment. Pinned Lean executable/library identities and the actual resolved Rust compiler/version were checked. Rust standard libraries, linker, runtime and compiler correctness remain explicit external trusted dependencies.

All 14 exact theorem reports pass with only standard allowed axioms. The complete extracted original and candidate methods compile using Vec storage and a byte-membership oracle. Across the unchanged 441 interval pairs, original has exactly 146 mismatches and candidate zero. All five machine-boundary candidate outputs match the expected vector; the original reports all true. This is finite native evidence beside the universal mathematical proof, not a verified translation.

An independent compiled strict-pairwise mutation (`start < other.end && end > other.start`) on the same extracted candidate/driver produces 40 mismatches while agreeing on the five machine-boundary examples. It demonstrates why endpoint strictness alone misses empty interior intervals. The Lean strict-pairwise empty witness independently captures that distinction. No finite corpus expansion was used.

Six independent guards reject modified proof source, unlisted file, missing manifest, symlink input, duplicate JSON key and an output alias containing `..` that resolves inside the capsule. Each rejects without creating output. These checks test integrity behavior, not adversarial compiler safety. Full logs, generated Rust source, command records and CHECK.json are retained under receipts/. Only completed owned generated outputs were removed after retaining them.

## Exact WPT and evidence

Final test hash: `6b29bcb18f02123f74ff715bf3873943b902d6209b99edc946ac45632247a32a`. The retained root seven-case baseline has two failures, five passes and harness OK. Both failures occur at the final image equality assertion after typed-resolution and syntax/serialization prerequisites. Original five-case evidence is left unchanged in its original capsule.

The final test has no optional-precondition exit. Typed attr resolution is calibrated against a distinct registration initial value; literal string/resolution adjacency is calibrated as supported; expected image serialization comes from the same document's literal reference. The two positive cases cover touching string and URL-function source spans. Separated and literal cases are controls. Direct attr URL and whole custom-property substitution must remain rejected. The later tainted-URL case ensures the candidate cannot pass merely by ceasing range checks after admitting the first untainted option; its baseline pass alone does not isolate which old range rejected the declaration, so the candidate rerun is essential.

No string/URL comparison depends on loading the data GIF. The test measures computed declarations, not network behavior or resource selection performance. CSS-values directory metadata enables random(); no test-specific metadata was found. That absence is not pass evidence. The appropriate regression gate includes existing attr-security coverage and root's final seven-case candidate rerun. This review does not require a broader unrelated matrix.

## Limits

Known prior partial-taint work is bug 1997583; this is a narrow endpoint follow-up, not a novelty claim. Root's exact source and browser pairing must still establish candidate behavior. No isolated-upstream browser result, full substitution refinement, quantified performance claim, security severity or unrelated animation repair is included.
