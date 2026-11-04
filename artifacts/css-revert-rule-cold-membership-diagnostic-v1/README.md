# Cold block-membership C diagnostic

`native.patch` is a two-file overlay on the coherent A+B+D candidate in `css-rollback-cutoff-e86-rebase-v1`. It changes only copied `properties/cascade.rs` and `stylist.rs`; the parent `applicable_declarations.rs` candidate remains required and unchanged. This is a diagnostic implementation, not a compiled or accepted native repair. No live source, WPT, index, application, browser or checkpoint was changed.

## API and storage

`apply_declarations` gains `declaration_block: Option<&PropertyDeclarationBlock>` immediately after its declaration iterator. The existing rule-tree caller passes `None`, selecting `DeclarationSources::Rules(rules, guards)`. `Stylist::compute_for_declarations` passes `Some(block)` from its actual author-guarded block; its deliberately empty rule-tree root is never used as a provenance substitute. Searchfox discovery found these two callers; their exact immutable e86/current-a6 bodies and API definitions underpin the patch. The two immutable stylist bodies are byte-identical.

`Cascade` holds one optional borrowed source view and an initially empty `Vec<RuleExclusion>`. Its existing lifetime is sufficient: `iter_declarations` already permits declarations to outlive the cascade borrow (`'decls: 'c`). Rule-tree ownership and the origin-specific read guards remain borrowed throughout the cascade. `StyleSource::read` ties the returned block to those borrows; direct-block ownership remains with the caller's Arc/read guard until the call returns. Each stored exclusion borrows the block for that same cascade lifetime. No raw pointer storage, pointer arithmetic, unsafe code, ownership transfer or cross-cascade cache is added.

`KeyframeCustomPropertiesBuilder` uses `new_for_custom_properties_only`, which explicitly stores no source view. Its custom-property consumer and empty longhand declaration buffer remain unchanged. If a longhand Rule trigger ever reaches that mode, the source expectation fails rather than silently inventing provenance. This is not a claim to repair general keyframe rollback semantics.

`Declaration`, its index width and inline buffer capacity are byte-for-byte unchanged. No layout-size measurement was made. There is constant per-cascade view/vector overhead. Without a Rule trigger, the vector has no backing allocation and no source-block lookup occurs. This does not prove a net memory or speed improvement.

## Exact skip point

Both existing longhand dispatch paths still reach `apply_one_longhand`. Ordinary logical declarations retain their writing-mode dependency observation and physical mapping before that call; prioritary dispatch retains its nonlogical assertion and linked-property walk. The dependency-discovery prepass is unchanged.

The existing seen and included-flags checks run first. The existing `reverted.longhands_set` fast bit gates cumulative A+B+D eligibility and then cold membership exclusion, in that order. All rollback kinds set that bit; only non-Rule kinds update the accumulated cutoff map. Rule exclusions compare physical longhand and `priority.unimportant()` before scanning the excluded block's declaration slice with `std::ptr::eq`. Other properties and priorities remain eligible. Properties never reverted bypass the exclusion vector entirely.

`original_declaration` is retained before the substitution Cow shadows `declaration`. Only an actually admitted direct or substituted Rule result triggers `containing_block(original_declaration)`, then records the block/property/normalized-priority triple. Missing source membership is a release invariant failure. Lookup neither substitutes nor evaluates values. Blocks are distinguished by stable original reference membership, not replacement values, variable text, shorthand-cache results or rule-node identity. Repeated nodes sharing the same block retain the historical C allocation-class quotient.

The custom-property cutoff consumer is unchanged. Forced-color handling remains after substitution and before rollback dispatch; a genuine Rule does not append forced-color fallback actions. This does not declare all unsuccessful prefixes pure or deferred action vectors duplicate-insensitive. The existing A+B+D order/cutoffs and the qualification in `css-rollback-rule-observation-audit-v1` remain necessary.

## Cost and unresolved validation

The first admitted Rule for a property/normalized-priority/block scans rule-tree sources and their declaration slices (or the direct block). Later eligible candidates scan stored exclusions and, for matching property/priority, block membership. The fast bit avoids that vector scan for never-reverted properties. Repeated Rule-heavy blocks and same-property candidates can still cause quadratic cold-path work. There is no lazy address map or claimed constant-time membership; source enumeration, repeated shared blocks and excluded-block sizes contribute to scan cost. No benchmark was run.

Remaining native checks include the actual common borrow/type inference across visited, direct-block and custom-only calls; both longhand consumers; substituted Rule and logical/physical mapping; forced-color/cutoff interactions; and cold-path performance. Pointer membership relies on immutable block storage while the read guards and rule/source owners live. The observation audit and ordered-block models are supporting restricted arguments, not a proof of complete native evaluator equivalence.

## Fixtures and static checks

`FIXTURES.json` references unchanged historical C72 and full D64 bytes, plus root's separate substituted-rule20 fixture and its genuine WPT preparation. This capsule copies or edits none of those pages and runs none. With the parent's unchanged A16+B16, the prospective union has188 callbacks; D64 replaces D48 in that union. The four font-size rows in the companion20 are separate-rule preservation controls, not positive same-ID exclusion cases.

Actual `aa7066` exited0. `CHECK.log` records two zero-fuzz patch operations (forward and reverse), exact reconstructed source bytes, Rustfmt edition2024 parsing of both copied candidates, unchanged Declaration/prepass/prioritary/ordinary/custom bodies and cumulative rollback state, and the source guard/original-reference ordering checks. Parsing is not Rust typechecking. The check authenticated immutable Git API objects and exact fixture hashes; it did not execute browsers, callbacks, Lean, builds, live observers or historical native suites. Temporary patch trees were removed. The export-definition excerpt was read separately after the check and is identified as such; the checked API list and production bodies are unchanged.

`SOURCE-ROLES.json` pins overlay preimages and candidates. `SOURCE-API.json` and `SOURCE-API.txt` record immutable interfaces, while `REFERENCES.json` pins parent design/audit and fixture provenance. Searchfox discovery used `apply_declarations`, `Cascade`, `StyleSource::read`, `parent` and `style_source`; exact implementation decisions use saved candidates and immutable Git objects. The patch is intended for root review before any native application.
