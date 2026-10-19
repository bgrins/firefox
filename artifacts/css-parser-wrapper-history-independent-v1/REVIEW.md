# Independent parser wrapper-history review

## Verdict

**ACCEPT the scoped model/source correspondence component.** No substantive blocker was found. External FREEZE, MANIFEST and checker hashes were authenticated before executing producer code; all 463 inputs were verified and copied by the manifest into a fresh relocation. Fresh replay passed 57 Lean modules and 448 exact named audits, including 77 new results, and reproduced 72 complete source bindings. Debug and release native probes each produced the exact 69 ordered observations for the ten frozen histories.

The result is conditional universal model reasoning plus finite correspondence with the pinned complete Rust crate. It is not a universal native parser theorem. Binding a function's bytes does not prove its translation, runtime correctness, full caller reachability, UTF-8 safety or machine arithmetic.

## Proof review

All eleven new modules were read in full: nine theorem-bearing modules plus generated cases and executable driver. The 77 additions comprise 60 general component results and 17 concrete witness results. The inherited modules remain unchanged and their predecessor capsule is independently authenticated by the replay. The actual axiom union, for both the new results and complete inventory, is propext, Quot.sound and Classical.choice; no additional or user axioms were accepted.

### Raw scan and independent reference

`WrapperWhitespace.nativeUnit` follows the actual space/tab, LF/FF/CR, CRLF and slash-star byte branches. Its reference enumerates the prefix grammar separately and uses the independent first-terminator comment reference. `unit_refines` connects them; neither side is defined as equality to the other. The run/reference recursions intentionally share the same finite scheduling shape, but one mutates state and the other collects a position and ordered comment bodies. Their unit comparison and inductions establish cursor and annotation correspondence, together with cache, mode and saved-state preservation.

Every successful raw unit consumes a positive bounded count. Source-length-plus-one fuel therefore exhausts the prefix; it is not an arbitrary recursion-depth restriction. `run_bounds` requires an initially in-range cursor and proves monotone bounded raw movement. This is mathematical byte-position reasoning. It does not prove Rust character-boundary safety, packed line metadata, UTF-16 columns, allocation or integer headroom.

### Pending cleanup, next and observers

The raw whitespace phase is preceded by actual pending-block cleanup. The model retains fresh Function observations and comment writes from that phase. The tracking-mode preservation theorem applies only to subsequent raw whitespace/comment scanning; it does not incorrectly erase pending cleanup effects. Cache and saved-state preservation compose through both phases. Cleanup's finite-model result represents the native terminating loop only under the explicit token-provider Progress premise; upper endpoint bounds are separate assumptions. Without these admissions, mathematical fuel-limited equality is not a native termination theorem.

`WrapperNext.native` composes skip and the existing primary API. Its second pending check is proved inert because skip clears the pending state, rather than assumed inert. Delimiter checking occurs after the raw prefix. Token/cursor results compose through inherited coherent-cache lemmas; mode and seen results additionally require the epoch compatibility/invariant conditions. Comment URL publication has a separate cache-sensitive reference: source tokens returned to the caller do not alone determine annotation writes.

### Histories and entry protocols

`WrapperHistory` proves arbitrary finite interleavings of skip, next, primary fetch, save and reset preserve an explicitly related state and complete returned-token list. Saved indexes abstract same-instance saved ParserState handles. Native fixture indexes are valid; arbitrary foreign states and invalid Rust saved-handle accesses are not admitted by this abstraction. Coherence follows from constructors and preservation, rather than being freshly asserted at every native operation.

`WrapperEntry.expectColon` is a Boolean success projection of actual next plus token match. A successful Colon, including a cache hit, establishes a non-relevant cached token; raw skip preserves it. A failed Colon is explicitly demonstrated not to establish that condition. Cold construction followed by raw skip also has a safe cache. The ensuing query theorem composes with those entry facts. Exact unexpected-token versus EOF error payloads are deliberately outside the Boolean projection.

Repeated epochs still require `Admitted`, which recursively checks non-relevant cache entry for each actual epoch. The proof does not derive that every re-enable is safe. The late-enable and query/re-enable Function-cache failures remain valid library histories, and the concrete wrapper witnesses preserve them. The annotation A/B witness likewise retains protocol dependence: next raw-scans the trailing comment whereas primary replay may leave the earlier raw annotation. Neither behavior establishes an invented normative sourceURL publication contract or a reachable browser defect.

## Source correspondence and caller coverage

The pinned tokenizer skip_whitespace, skip_block_at_start, consume_until_end_of_block, Parser::next, primary-fetch body, reset, try_parse, expect_colon and expect! macro were inspected along with the adapter. The actual next body performs skip_whitespace then next_including_whitespace_and_comments exactly as modeled. The two new complete bindings are expect_colon and expect!, added to 70 inherited bindings. These are manually reviewed source-selection records, not a certified Rust parser/lowering pipeline.

The Rust build uses complete copied crate/dependency sources, retaining unmodified normal bodies and appending observation methods. wrapper_next temporarily sets/restores stop_before around actual next; it does not prove parse_until callbacks. The observation adapter includes cursor, pending block, cache key/token/end cursor, mode, both Option-valued URL fields, saved states and operation result. Other token payloads collapse to `other`; line/UTF-16 metadata and detailed errors are absent. Leaked fixture names supply the native static-name lifetime; this is not a production allocation/lifetime proof.

The authenticated production audit identifies the two enable expressions and eight source files; its later caller-source comparison records historical byte equality to the observed local files. The declaration routes enter cold or after successful Colon, then raw skip; the geckolib substitution helper creates a fresh parser. Nested-rule and supports forwarding are included in the static trace. No exhaustive generated call-graph theorem is supplied. In particular, callback/depth/delimiter wrappers, next_including_whitespace filtering, and the declaration helper's saved query Boolean plus short-circuit rescan remain open. Their behavior must not be replaced by an indefinitely enabled epoch assumption.

The finite driver executes the native-shaped model. Independent references are connected by universal theorems under their premises; the finite model execution itself is not an additional independently parsed CSS oracle. Both sides share the frozen input/operation cases, not native-produced expected state. Unsupported fixture token families panic rather than invent consumption. Broader named provider functions, UTF-8/codec, machine bounds, compiler, allocator and normal-return assumptions remain explicit.

## Fresh mutation and trace evidence

All seven native mutations compiled successfully and their probes exited zero. Every rejection is an actual projected observation difference, not malformed output, panic, infrastructure error or a surviving mutant:

| Mutation | Fresh differing snapshots | Observed mechanism |
| --- | ---: | --- |
| drop-fresh-function-effect | 11 | seen/query effect is lost |
| replay-function-effect | 6 | a cached Function is newly observed |
| reset-disables-tracking | 2 | active seen state is cleared at reset |
| wrong-cache-key | 51 | incorrect cached token/cursor selected |
| skip-omits-pending | 8 | cursor remains before nested cleanup and observations are lost |
| next-clears-cache-after-skip | 8 | a former hit becomes a fresh read and changes tracking |
| skip-drops-comment-writes | 18 | raw prefix annotation publication disappears |

The counts and exact changed rows are independently recalculated in MUTATION-REVIEW.json from retained model/native traces. These mutations discriminate exact correspondence with the frozen implementation; rejection does not imply every alternative behavior is normatively wrong. In particular, cache clearing or observing hits changes the retained unsafe-entry counterexample.

All three Lean mutations compile concrete semantic witnesses. Omitted FF then fails unit_refines on byte 12. Cache clearing fails run_cache at the induction step. Omitted pending cleanup fails cursor/pending/observation joins. The reported type mismatches are mismatched semantic equalities in unchanged proofs, not missing dependencies or syntax errors. Their compiled witnesses establish the changed behavior independently of these proof failures.

The ordered trace comparator requires the input-derived complete operation roster, eleven fields per snapshot and exact equality to independent Lean execution. Fresh missing, duplicate, unknown-operation, extra-field, reordered and None-versus-empty corruptions are rejected. Thus no individually well-formed row can simply disappear from a successful replay. The earlier nondiscriminating reset fixture, privacy-rejected mutation and aggregate driver-name collision are retained as failed development evidence; none is counted as a successful gate.

Eight independent capsule challenges verify changed-source, unlisted file/directory, symlink, duplicate manifest, path-escape, missing isolation and existing-output rejection before generated work. Duplicate/path tests reseal only their disposable test copies to reach the relevant guards; external producer pins remain unchanged. Path escape is rejected by the closed roster before path normalization, so this is not evidence that a particular later path-check branch executed.

## Remaining obligations and retention

Acceptance is limited to the declared projection and source versions. Full metadata/character-boundary admission, remaining token-family consumption, native arithmetic and memory, callback contracts, declaration-parser control flow and publication consumers remain open. No production bug or native repair is certified by this component.

The independent source-only checker authenticates the complete review inventory and validates retained replay/mutation/guard receipts. The manifest-only producer relocation can perform a fresh full replay with the pinned Lean/Rust tools and an unused external output path. Needed logs, raw traces, model-mutant witnesses and native mutation records are retained; generated compiler products and scratch source copies are removed only after retention checks. CLEANUP.json records the exact removed owned paths and sizes. No live native/WPT edits, Firefox build, browser execution or Git mutation occurred.
