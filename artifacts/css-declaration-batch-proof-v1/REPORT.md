# Ordinary declaration batching refinement

## Result

The universal component covers Stylo's ordinary prepare/update batching algorithm under explicit source, comparison and storage premises. It proves that initial planning, descending removal, ascending index correction and source-order publication have the same final abstract declarations and priority bits as an independent sequence of CSSOM setters. A separate raw-storage relation covers the declaration vector, importance vector and identity membership, including retained membership during removal.

No additional Firefox defect was established. The accepted all-shorthand repair is an input; ordinary update code is byte-identical in the original and candidate snapshots. The new results close the ordinary batching obligation left open by the all-order companion. They are neither a proof of the entire parser nor a machine-checked refinement of Rust/LLVM.

## Universal chain

* `BatchBase.Comparator` supplies a stable deterministic comparison and requires only **true implies equality of the abstract entry**. It may return false for equal entries. This permits conservative replacement for nonreflexive floating payloads. Actual native values are mapped to the abstract domain under an explicit soundness/congruence admission; native `PartialEq` is not globally replaced with mathematical equality.
* `BatchOrder.initial_decision_stable` uses a relevant-identity projection to show that another unique, nonopposing source action preserves the complete keep/replace/move/append decision, including payload and priority comparison. Source compatibility follows from per-group mapping uniformity.
* `identity_batch_refinement` proves that collecting identity removals before replacements/appends preserves the independent forward setter result for arbitrary finite destination and source lists. The reference searches forward and tests opposite identities after the target; it does not inspect a native plan.
* `BatchIndices.descending_rank_lookup`, `BatchOrder.descending_removal_filter` and `numeric_batch_refinement` establish original-index removal, survivor filtering, corrected target lookup and the complete indexed batch result. The selected positions are distinct and in bounds. Rank subtraction cannot underflow.
* `BatchRank.ascending_rank_loop` models the actual ascending count loop. `BatchSchedule.schedule_rank_connection` ties its output to the strictly earlier removal count; `schedule_removal_connection` ties the reverse filtered event list to descending removal indices. `stream_correction_connection` applies those updates to the original source plans. **`scheduled_batch_refinement` composes the event loop, separate raw removals, corrected updates and membership insertion with the independent setter result.** `admitted_schedule_exists` supplies a nonvacuous canonical schedule for every admitted input. The native standard-library sort is admitted to satisfy its permutation/key-order contract; unique original indices make stability irrelevant.
* `BatchStorage.raw_batch_refinement` and `final_storage_invariants` use separate operations on declaration payloads, priority bits and membership. They do not define the final storage by re-encoding an expected list. Removal retains membership; later move appends restore exact final membership. Aligned lengths and unique identities hold at the end. `batching_indices_safe` supplies all removal/update bounds and subtraction safety.
* `BatchInterface.exact_reserve_growth` proves final length is original length plus the initial append count. `reserve_bound` and `plan_zip_length` bound that count and establish one plan per source declaration. Normal allocation and machine-size bounds remain external. The native updater must receive a fresh plan and an unchanged source/destination between planning and execution; reuse of stale counters is not modeled as valid.
* `first_changing_step`, `false_gate_direct` and `guarded_batch_refinement` cover the prepare gate. A true gate denotes an implementation step, not necessarily a changed semantic state or changed serialization. `conservative_comparison_may_publish` is a concrete kernel witness of a true gate with equal final state.
* `BatchPublication.published_batch_refinement` connects the authenticated optional-payload publication shape to guarded batching. Fixed metadata identities may be filtered out; publication preserves identities, uniqueness, compatibility and capacity. Payload grammar correctness, generated Rust lowering and native callback purity remain admissions.

## Native correspondence

Exact source snapshots are inside the authenticated all-order input:

* `declaration_block.original.rs`: SHA-256 `7239be79e4864599f55b5d8898f682366290900ff484b63ce491b5b221bd3f6c`.
* `declaration_block.candidate.rs`: SHA-256 `8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a`.

Replay extracts 37 complete original items and 38 complete candidate items, including the complete ordinary planner, prepare/update, scratch/drain, declaration-block accessors, identity sets, importance operations and neighboring public functions retained by the earlier companion. Each record contains the exact body, anchor, start offset, source filename and digest. The complete ordinary update suffix is checked byte-identical between the two versions. The ordinary planner closure was factored into the candidate helper; its token correspondence remains authenticated by the prior capsule. Native execution exercises the complete original and candidate prepare/update functions, including gate bypass and source draining. Retaining other complete functions does not count as exercising every one of them in this corpus.

Adapters remain explicit: standard `Vec` substitutes for ThinVec/ArrayVec, a `Vec<bool>` wrapper substitutes for SmallBitVec, and BTreeSet substitutes for identity sets. Custom names and ordinary payloads are u16 equivalence classes; generated declarations, concrete CSS payload implementations, allocation internals, Rust aliasing and iterator lifetime semantics are not proved. The native driver uses equal common importance for each source transaction; the mathematical entry model permits more general per-entry priorities. Native source drains are consumed before observation. Sorting, stable snapshot/callback behavior, memory allocation and representable indices are admitted provider contracts.

The retained actual `data.py` and TOML inputs are executed after authentication. They generate 431 Gecko longhand records and 94 ordinary shorthand lists. Replay checks every ordinary list for unique IDs and no mixed mapping pair; maximum ordinary expansion is 19. One corpus case uses the actual `padding` provider list. Other cases are deliberately reduced canonical source lists; they are not mislabeled as parsed CSS. The source-publication capsule audits the parsed and singleton entry routes and provides optional-publication lemmas. It does not prove every value parser or the complete native template compiler.

## Evidence and mutation results

172 theorem declarations are kernel-compiled and individually axiom-audited: 55 from the immutable all-order model, 5 from the immutable publication helper, and 112 in the batching component. The latter include 3 reused root index helpers, leaving 109 newly authored theorems. The allowed toolchain foundations are `propext`, `Quot.sound` and `Classical.choice`; no `sorry`, custom axiom, `admit` or `native_decide` is accepted.

The targeted native corpus has **18 transactions per variant**, covering 56 initial plans: 8 keep, 16 append, 14 replace and 18 move. It covers multiple removals, replacements before and after removals, provider-ordered padding, common priority changes, existing important destinations, custom/unrelated entries, empty source/destination, no-op inputs and unchanged-value moves. Both original and candidate have zero mismatches.

| Compiled mutation | Transactions distinguishing it | Bounds panics |
| --- | ---: | ---: |
| Remove in ascending order | 8 | 0 |
| Omit rank subtraction | 4 | 0 |
| Add removed count | 4 | 2 |
| Omit removed importance bits | 8 | 0 |
| Invert replacement importance | 6 | 0 |

All five mutations compile and run. Panics are caught and recorded separately; completed-state discrepancies are not confused with bounds failures. Each mutation has a successful concrete Lean witness. The added-count witness is specifically an attempted index 6 in a length-6 vector, matching the first native panic. These are five native mutation checks and five kernel counterexample witnesses, not five mutated Lean theorem rejections. Additional witnesses show why mixed-mapping or duplicate source identities are excluded. No broader finite corpus was added without a concrete batching coverage need.

Raw rows expose the original state, actions, initial plans, append count, removal flag, gate, completion/panic status, final vectors, final membership and remaining plan vector. The Python oracle independently reconstructs all 18 named seeds/actions from the retained provider data, computes the forward setter sequence and checks exact fields, binary flags, whole-field syntax, roster and plan metadata. It does not trust an emitted expected state. Ten targeted corruptions verify rejection of malformed fields, changed roster/actions/seed/plans and missing rows. Golden receipts are an additional reproducibility check.

## Specification and source admissions

The normative reference is [CSSOM set a CSS declaration](https://drafts.csswg.org/cssom/#set-a-css-declaration), reached through [setProperty](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty). Exact primary-spec bytes and the previous canonical-order issue investigation are retained in the authenticated all-order static capsule. This proof accepts the fixed source expansion order as input; it does not resolve CSSWG issue 5741's absolute order question.

The separately authenticated NaN audit traces specified time versus NoCalcNumber equality and explains why conservative publication is allowed. Its time example is source-derived, not an executed parser test in this package. The supplied-comparator theorem addresses the proof admission without claiming a new CSSOM bug or universal equivalence of concrete value wrappers.

No browser tests, Firefox builds, live implementation changes or Git operations are part of this artifact. Existing WPT evidence and the accepted all repair belong to their separate parent-owned gates. DOM observers, serialization, parsing failure cleanup, malformed native representation, concurrent/reentrant mutation between prepare and update, and mixed public push/remove histories are not covered by this batch contract. The parent's separate public-storage work is not imported or claimed here.

## Reproduction and closure

Run `python3 -I -S check.py --output /absolute/fresh/output` from any location. Authenticate the externally supplied FREEZE/MANIFEST/checker hashes before trusting the entry point. The checker rejects extra files/directories, modules/packages that could shadow imports, symlinks, nonregular files, duplicate JSON keys and path escapes; output must be fresh and outside the capsule. It authenticates every copied source and executable before local imports, then authenticates the three frozen dependency capsules. Replay clears Python/Lean environment overrides, uses a fresh output-only Lean path, and recompiles from retained sources. Binary compiler pins and version details are explicit in TOOLCHAIN.json; compiler/standard-library correctness remains trusted, as in the accepted earlier companion.

The first canonical and relocated full runs completed Lean/native checks but caught a packaging bug: tuple-valued in-memory failure details were compared with decoded JSON arrays. Both reconstructed serialized results were already identical to the receipt. The checker now compares reconstructed JSON values; the failed logs and exact correction are retained, and both complete replays are rerun after this correction. Proof and native semantics did not change.

Canonical and manifest-only relocated replays, complete mutation receipts, axiom inventory, extraction records and genuine tamper-control results are the final handoff gates. Only manifest-listed source/evidence/receipt files and MANIFEST/FREEZE belong in a companion commit; replay binaries, object files and rust outputs stay outside the artifact.
