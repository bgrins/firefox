# Registered syntax alternative random-index rollback

This is an uncompiled two-file native proposal. It restores the entry random counter only when a complete registered syntax alternative fails. The successful alternative keeps every increment, including all successful list members. No live source was changed; no browser observation or accepted fix is claimed. The source-only lead and sealed15-case probe remain in css-registered-random-index-audit-v2.

## Native boundary

Parser::parse in properties_and_values/value.rs already wraps each alternative in cssparser::Parser::try_parse and parse_entirely. The former restores input state; the new PropertyDeclarationContext::with_random_index_rollback wraps that same result and restores the counter on Err. This includes failure after a component successfully parses but leaves trailing tokens. Restoring the saved counter rather than zero also preserves any prior successfully parsed functions if the helper is later used in a nested context.

The helper is deliberately named for its one state field. It does not roll back all ParserContext effects, claim panic-unwind restoration, reset between successful list members, retry after a successful alternative, or change grammar admission/independence checks. Existing successful values and output_multiplier are published only after the alternative returns Ok. Component::unpremultiplied preserves the original Number component and its multiplier; it only expands premultiplied data-type aliases, so Number+ still parses successive members inside one alternative. Failed temporary values are dropped under the same preexisting Rust ownership path.

## External state audit

| State | Behavior at this boundary |
| --- | --- |
| PropertyDeclarationContext.random_count | Cell mutated by MathFunction::Random before later type rejection; restored on Err. |
| PropertyDeclarationContext.property_id | Fixed by surrounding with_property_declaration; shared callbacks cannot replace it. Scope entry/exit still reset the count. |
| error_reporter | Explicitly None in this registered-value ParserContext. |
| use_counters | Explicitly None here; no telemetry rollback attempted. |
| origin, mode, quirks, nesting_context | Fixed configuration exposed through shared context. |
| namespaces | Fresh default Cow; shared context exposes no mutable access. |
| attr_tainted_regions | Owned SmallVec-backed AttrTaint; range queries borrow it, mutation requires mutable access. Preserved unchanged. |
| url_data | Borrowed reference-counted URL metadata. Nested values may allocate/clone/drop URL or atom resources. No resource-management rollback or global purity claim. |
| temporary value vector | Local to parse_value, returned only on successful whole alternative; failed vectors do not partially extend output. |

Searchfox discovery located context/taint/URL types before exact local capture. Both native base files match the sealed predecessor byte-for-byte. Context-source captures bind actual checkout definitions; custom_properties.rs includes the current unrelated provider prototype, and no change to that file is proposed.

This is a narrow restoration boundary, not an exhaustive transaction for every nested parser. A successful outer alternative can still contain a failed internal speculative parse; those sites are outside this correction. Other ParserContext callers and their telemetry/error behavior are unchanged. Wider claims require reached-path examples and a separate audit.

## Diagnostic supplement

observe-trailing.js preserves all15 sealed predecessor cases and adds decl-trailing-list: literal initial .25 .75 registered as Number|Number+, followed by two indexed random functions in the declaration. The Number branch successfully parses one function, then parse_entirely rejects the remaining token. The proposed boundary must undo that increment before Number+ produces indexes1,2. This distinguishes whole-alternative failure from failure inside the component parser. The existing single/list/failed-list controls remain. Sixteen cases across three phases produce48 rows when supported. The sealed45-snapshot probe is unchanged; this separate successor remains unexecuted.

## Validation and limits

The exact two-path patch applied forward/reverse/forward with no offset/fuzz in private scratch; both Rust files pass rustfmt --check using the repository-compatible configuration. These are transport/syntax checks, not native typechecking. The diagnostic is syntax checked only. check.py removes its scratch.

The predecessor model manually corresponds to this Result boundary: failed-prefix neutrality and first-success termination hold abstractly, while cursor-only rollback and resetting each successful member are rejected. No Rust refinement, resource purity or PRNG proof is claimed.

Root should first execute the sealed45-snapshot probe; the supplementary trailing-token case can follow separately. Preserve registration errors, explicit same-key calibrations, successful member progression and all phases. Distinct keys need not yield distinct outputs. No WPT outcomes are invented or fixtures installed. Independent source review is recorded separately.

No clean-upstream-build claim is made: transport uses captured branch bodies. The added logic has no intentional provider/zoom prerequisite, but upstream transport and native compilation remain to be established. No fix ID, accepted count or canonical formal coverage increment.
