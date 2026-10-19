# Independent review: ordinary declaration batching

## Recommendation

Accept the sealed producer capsule as a conditional universal batching component and a bounded complete-source native bridge. No material model, source-correspondence, oracle, or replay blocker was found. This review does not accept a full native parser/CSSOM lifecycle proof or a new Firefox bug.

Producer: `artifacts/css-declaration-batch-proof-v1`. External FREEZE SHA-256 `4ac9e867537d7fc7e5d68af04eac86ce3dc8e16ad394982c9903107b2f054fc7`; MANIFEST `7ee88ad7c0498f4da2e282684c24aa2cc3bfadbba42f97cc7dcf3c3d9c98a369`. All 209 inputs and the externally supplied checker/report pins were authenticated before executing local helpers. The review copied only that manifest and its two seals into a fresh temporary source root, then replayed it from outside the repository. The producer capsule was not modified.

## Proof review

I read all nine batching modules, the inherited forward reference and storage definitions used by them, the publication helper, source bindings, extraction facade, native driver, both row checkers, replay driver and capsule checker. The exact theorem inventory contains 172 unique audited declarations: 55 inherited AllOrder, 5 inherited Publication, and 112 batching declarations. The last group includes three reused index helpers. Fresh audits use only the stated standard Lean axioms.

1. **Comparator and reference.** `BatchBase.Comparator` requires only true implies equality of the abstract entry. False negatives are allowed, including repeated comparison of the same entry. The reference searches forward and tests opposite mapping identities after the target; it does not consume a plan or precomputed expected output. `planner_refinement` handles a false comparison by replacement and uses soundness only for the no-op branch. A native NaN is not made reflexive by assumption. The abstract value type has mathematical decidable equality; relating native payloads and their comparator to this domain remains an explicit admission. The inherited AllOrder gate-equals-semantic-change results are not reused to claim that result for the conservative comparator.
2. **Stable planning.** Relevant-identity filtering preserves the target entry and opposing entries. Another distinct, nonopposing source setter cannot change this subsequence. This derives complete decision stability, including replacement versus no-op. Unique source IDs and pairwise nonopposition are real hypotheses, not conclusions inferred from a successful run. Mixed-mapping and duplicate-source counterexamples demonstrate why they matter.
3. **Identity and numeric batch.** The removal/after-step decomposition and commutation argument moves all identity removals before source-order publication. Original indexed positions are derived from the unique destination. Distinct source IDs produce distinct indexed plans. Descending removal preserves lower lookups; corrected replacement positions identify surviving original entries. The proof derives the needed subtraction and array-index bounds instead of assuming that `Nat` subtraction represents a valid native subtraction.
4. **Actual rank schedule.** `BatchRank.walk` counts removals in ascending original-index order. `BatchSchedule` proves its relation to the earlier-removal count, connects reverse filtered events to descending removals, and connects lookup of each corrected replacement to the original source plan. `scheduled_batch_refinement` composes these with raw storage. A sorted schedule exists for every admitted input; this is not a theorem over an uninhabited scheduling premise. The standard-library sort contract and native mutable-reference wiring are still source admissions.
5. **Separate storage.** Declaration payloads and importance bits are removed independently at matching indices; membership is retained during removal. Subsequent append/move steps restore exact final membership. `raw_batch_refinement` establishes the relation after real modeled operations, rather than defining output storage from the expected list. Aligned lengths, unique final IDs, and exact membership follow. The temporary retained membership is deliberate and is not incorrectly required to describe the transient shortened vector.
6. **Gate and allocation arithmetic.** A false gate preserves the reference result. A true gate means an implementation action, not necessarily a semantic change; the conservative-comparison witness confirms this distinction. Final length equals original length plus initial absent-ID appends, and plan/source lengths agree. The reserve theorem is a mathematical length statement, not an allocator or native capacity proof. Fresh counters, native integer bounds and normal allocation remain necessary.
7. **Publication.** Optional publication retains a fixed provider ID order and filters absent payloads. Its uniqueness, compatibility and capacity results compose with guarded batching. The value provider does not establish grammar validity, complete generated Rust lowering, or callback purity. This remains the same limited provider shape previously reviewed in the separate source-admission checkpoint.

## Native bridge and independent observations

Complete source snapshots bind original `declaration_block.rs` SHA-256 `7239be79e4864599f55b5d8898f682366290900ff484b63ce491b5b221bd3f6c` and candidate `8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a`. I read the complete planner, prepare and update bodies. The candidate helper is the factored original planner; the ordinary update suffix is byte-identical, SHA-256 `c5cb56e1269545f832c36b77ac73b335372bd8fa36eb330e72ec65e9242e364b`. It reserves, sorts indexed events, removes in reverse order, fixes replacement positions in ascending order, executes source-order updates, and clears the plan vector exactly as the component describes.

The fresh bridge extracted 37 original and 38 candidate items. Every retained extraction body was independently compared against its exact source slice and digest. The source parser used by extraction is a narrow token/bracket reader, not a Rust parser proof; manual inspection of the target bodies complements these byte checks. Generated metadata has 431 longhands and 94 ordinary shorthand lists, all unique and mapping-uniform, with maximum length 19. These are retained provider results, not a proof of every future metadata revision or parser route.

Fresh original and candidate outputs are byte-identical across 18 transactions each, containing 56 plans: 8 no-op, 16 append, 14 replace, and 18 move. The corpus includes multiple removals, replacement targets before and after removals, priority changes, custom IDs, unchanged-value moves, empty inputs, and the actual padding provider order. Values are u16 classes, not concrete CSS values. The model is more general than the driver in allowing per-entry priority; native transactions use one common source priority.

The producer oracle reconstructs named input cases independently of emitted plans, then computes the forward setter result. Its row grammar rejects extra fields, malformed numeric/binary fields, changed inputs/plans/rosters, and missing rows. The review's separate `independent_checks.py` recomputes final order, bits, membership and plan clearing directly from fresh observed inputs with its own forward setter. This second check does not independently establish the driver-input roster; the source read and producer input checks provide that separate binding.

| Compiled mutant | Discriminating transactions | Caught bounds failures |
| --- | ---: | ---: |
| Ascending removals | 8 | 0 |
| Omitted rank subtraction | 4 | 0 |
| Added removal count | 4 | 2 |
| Missing importance-bit removal | 8 | 0 |
| Inverted replacement importance | 6 | 0 |

I checked the exact mutation substitutions and their successful kernel witnesses. The added-count witness attempts index 6 in a length-6 vector; the native first matching case fails at the corresponding replacement. The other failures include wrong identities/order or priority storage, not compile failures. These are five compiled native mutants plus successful Lean counterexample theorems, not five rejected Lean builds.

## Fresh replay and integrity

The manifest-only relocated source replay exited 0. It rebuilt all Lean modules and native variants and reproduced the retained receipts. Independently checked 172 exact audit names, source slices, provider invariants, and all fresh rows. Ten malformed-row controls and nine capsule controls passed. Capsule controls cover added modules/packages, executor modification, extra directories, FIFO, symlink, duplicate JSON keys, path escape, and output inside the source root. Their rejected inputs did not execute the modified helper. Compiler binary pins were checked; compiler and installed standard-library correctness remain trusted.

`fresh-replay/` retains the complete result, commands, axiom reports, raw compressed rows, extraction/mutation records and guard receipts. Generated Lean objects and native executables remain outside this review. `REPLAY-COMMAND.json` and `REPLAY-RESULT.json` identify the actual fresh run, with temporary paths retained as provenance rather than future required paths.

## Remaining boundaries

Acceptance is limited to this component. Still open are the complete native parser-to-source admission, generated concrete declaration/value representation and comparison abstraction, actual sort and container refinement, fresh plan/counter ownership across the caller callback, unchanged destination/source between prepare and update, native integer/capacity/allocation/aliasing semantics, and observable DOM/serialization behavior. The source must satisfy ordinary unique/nonopposing publication; generated `all` is a separate algorithm and proof. No arbitrary malformed native state, mixed public push/remove/clear history, or reusable stale update object is admitted. The parent's newer public-storage/API lemmas are outside this review and are not imported to close these gaps.

No further test is required for this scoped recommendation. The next useful full-composition gate is native source/callback readiness joined to this batch relation, rather than another finite row expansion.

## Recheck and inventory

Run `python3 -I -S check.py` from this review after authenticating its external seals. It authenticates this review and the complete producer closure before executing the independent checker. Add `--replay-output /absolute/fresh/directory` for another producer source replay. `--producer` can point to a manifest-only relocated producer capsule.

Review inventory: this review's MANIFEST keys plus MANIFEST.json and FREEZE.json. Producer inventory: its 209 MANIFEST keys plus its two seals. The review references the separately authenticated producer rather than duplicating it. Temporary outputs, compiled binaries and object files do not belong in either companion commit.
