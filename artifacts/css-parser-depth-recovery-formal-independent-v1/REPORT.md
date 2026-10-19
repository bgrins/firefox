# Independent depth-recovery formal review

## Recommendation

Accept the scoped recovery formal component and its source bridge for the exact one-call repair. No blocking proof or source-mapping issue was found. This closes the proposed token-level cleanup/limit-branch component; it does not close full cssparser, tokenizer, metadata, allocation, or Gecko caller verification.

The final browser capsule's complete original/candidate parser files equal the proof capsule's complete files byte for byte. The final candidate SHA-256 is 2ac2c7f820ff5095c705446ff8a0f31507affe08e68bf6cc3735d5fb5bc38788. Vendor checksum snapshots also match those exact parser hashes. Final browser/WPT adjudication belongs to the separate root/reviewer gate; this report does not substitute proof replay for it.

## Authentication and fresh replay

All 176 producer inputs were authenticated against the externally supplied FREEZE, MANIFEST and checker pins before execution. A new source-only copy was made in /private/tmp/depth-formal-independent-v1/capsule, excluding development-build and all old products. The complete replay returned zero:

- One Lean module, exactly 21 theorem names, each with only standard axioms. This run used propext and Quot.sound; no sorry, custom axiom, admit, or native_decide is used.
- Full original/candidate cssparser and vendored dependencies compiled from source, with 24 retained observations per variant exactly reproduced.
- Both compiled native mutants failed semantic assertions: omission leaks blue, and fixed-parenthesis cleanup stops at the wrong position for a square child.
- Both changed Lean definitions fail meaningful unchanged contracts. Omitting cleanup leaves unsolved limit_recovery/limit_eof_recovery goals and a false concrete repaired witness. Popping a mismatched closer fails leaf_advance and the mismatch witness. These are semantic failures, not syntax/import failures.
- Proposed script syntax check passed. No browser or Gecko build was run by this reviewer.

The independent checker validates the exact insertion location, four complete native definition spans, theorem inventory and axiom log, native delta rows, checksum association, and semantic mutation receipts. It does not import producer helpers before authentication. All logs are retained under evidence/.

## Complete proof reading and independence

Recovery.advance and run are a flat stack algorithm, with the top at the list head. Body is a separate tree-shaped grammar: atom and mismatched-close leaves, recursively complete child bodies, and a continuation. Its constructors do not call run or assert the desired suffix. AtEOF describes complete prefixes followed by an unfinished child chain. This is an independent structural reference for the selected token domain, rather than equality to a duplicated execution result.

The induction in grammar_cleanup handles arbitrary surrounding stacks and tails. A complete child consumes its own matching closer before the parent resumes. body_prefix preserves the active stack across complete internal components, and eof_cleanup derives exhaustion for unfinished content. remaining_suffix, remaining_length and active_progress hold for arbitrary finite token lists, including lists outside Body. The exact-suffix theorem is conditional on Body; the capsule does not prove that every raw CSS input is admitted by that grammar.

rejected takes the pending kind, clears pending, and runs cleanup. rejectAtLimit adds the unchanged guard and error result. noOpener is a model marker for an inadmissible API call; the real function panics when no opener is pending. rejection_preserves_context preserves depth, limit and the modeled stop context. It does not preserve cursor or observers, which necessarily advance. limit_zero_not_rejected only establishes branch selection with disabled limit; it is not a resource bound for unrestricted recursive callbacks.

limit_recovery and limit_eof_recovery compose the independent grammar with the rejection branch. parent_after_rejection proves the child-then-parent suffix result under separately supplied child and parent grammars. The old and repaired closed witnesses differ without assuming the desired final vector. Atoms 1/2 represent retained inner content in that witness; a mapping from those atoms to published CSS declarations is source/browser evidence, not a theorem embedded in the atom names.

## Native bridge audit

The complete parse_nested_block, consume_until_end_of_block, pending-state getter, closing-kind mapping, relevant token/cache entry points, native witness, and build/check scripts were read. The one added call is precisely after take_at_start_of and before returning TooManyNestedBlocks. No depth increment, stop assignment, or callback occurs on this branch. The normal branch, limit value, error kind and helper remain unchanged.

The native iterative helper starts with the rejected kind, takes each newly tokenized pending opener, pushes it, and otherwise pops only a matching closing kind. Returning immediately after the last pop justifies the nonempty-stack access on the next iteration. The source vector is bottom-first, whereas Lean is top-first; their correspondence is the reversal relation described by inspection. A pending opener is cleared on every token iteration, including an opener at physical EOF. The helper ignores stop_before as intended and bypasses cached public-token replay through next_unchecked.

The actual full crate is compiled, rather than a replacement parser facade. The native property callback is nevertheless reduced: its recursive calc shape and error propagation model the relevant Gecko path but do not compile all CalcNode/generated-property machinery. Byte-to-token classification and progress, strings/comments as inert atoms, native stack allocation, valid input boundaries, integer representation, and compiler/library execution remain admitted. Native packed line metadata can change while skipping; normal metadata arithmetic completion remains a requirement. Source reset/cache observer discrepancies remain recorded unchanged and are not repaired by this call.

The native fixed observations change in six rows: declaration visibility at depth 76, cleanup suffixes at depths 76/77, caught paren/square error suffixes, and EOF. A curly row has identical final publication even though its intermediate child position is asserted by the driver; unchanged final JSON is not evidence of an unexercised child assertion. All other 18 rows retain their exact outputs, including independent cache/observer counterexamples and depth-restoration/disabled-limit controls. These are finite checks, not a universal native theorem.

Optional fast_match_byte/fast_match_color and serde/malloc features are disabled in the source replay. Python, pinned Rust/Lean/Node tools and standard libraries remain trusted. The source mapping has not established an automatic Rust-to-Lean translation or all-feature compiler theorem.

## Relationship to other reviews and evidence

The earlier native/spec review supplies a detailed independent declaration/function delimiter trace and a separate 126-case source challenge. I read that report, but do not count its cases as this fresh replay. The formal reference preserves the same rule: rejected inner content remains owned by its block until the matching closer or EOF. It does not require successful parsing of depth-76 calc values or raise the implementation limit.

The final root pair record reports 1 FAIL/21 PASS to 22 PASS, with 46 other outcomes unchanged. This report authenticates copied source/checksum bindings and records that summary as context; the final browser reviewer owns raw outcome and test oracle acceptance. The producer's depth-limit-padding-recovery.html is an earlier proposal, not the final declaration-recovery-nesting-limit.html. Both identities remain distinct. No broad malformed-CSS, performance, memory-safety, or all-caller claim is inferred.

STRING-HELPER-TRANSFER.json separately records that all 25 complete bodies used by the accepted string-provider capsule remain byte-identical across this parser update, and CowRcStr is unchanged. The whole parser.rs hash changes. Historical WPT metadata snapshots in that string capsule remain context, not current metadata assertions.

## Packaging and remaining obligations

PRODUCER-COMMIT-FILES.txt contains precisely the 176 manifest inputs plus MANIFEST.json and FREEZE.json, 178 files. REVIEW-COMMIT-FILES.txt lists this review closure. Stage these exact rosters; do not recursively include development-build, temporary native executables, .rlib, .olean, or caches. This companion is separate from the final three-file parser/checksum/WPT repair, whose packaging belongs to root.

The scoped formal gate is satisfied. Remaining broad obligations are lexical/token projection and progress from arbitrary admitted input, native representation/metadata/heap execution, public token-cache/reset histories, and full Gecko caller/evaluator composition. They remain open rather than being replaced by the 24-case bridge. No extra finite matrix is needed for this scoped acceptance recommendation.
