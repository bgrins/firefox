# Independent count–iterator composition review

Verdict: accepted for the stated mathematical per-map composition, under the retained native representation/provider assumptions. No substantive proof blocker found. A checker output-path limitation is recorded separately below. This review does not claim whole-native or whole-CSSOM correctness.

## Authentication and fresh replay

Before execution, verified externally supplied freeze `642d3b6e681794c7c1edf1f9cab8b8afcbfcde662ff410e6039b6151b9f950aa`, manifest `edbe97d28bd36dbfdf684bc3adf05d2a9362d1924ab43759e79755a556885627`, and checker `331fb42e77d74714be791974cfd744c8d39487d03db88722d6515c8e74f8bddc`. All 134 inputs were authenticated, with safe canonical relative names, no symlinks, duplicate-key rejection and a closed file roster. The manifest-only relocation includes the two seals. Imported iterator and count capsules are byte-identical to the accepted predecessors, including their seals.

The fresh relocated replay used Python -I -S without optimization, a resolved canonical external output path, the pinned Lean executable and the complete 5,092-file library inventory inherited from the iterator capsule. Both predecessor proofs/mutations were rerun from their copied source, then their fresh compiled modules were copied into the composition build. There is no reuse of development outputs or repository production source.

All 105 inherited audits and 32 exact new named axiom reports passed. The new inventory has 25 general results and seven concrete-history/witness results; the latter include two all-index instances of the general theorem. Axioms are limited to propext, Quot.sound and Classical.choice. No custom axioms, proof holes or native_decide occur. All three new Lean modules, checker, mutation definitions, source join and scope documents were read completely.

## Mathematical connection actually established

The two models independently represented own lookup differently. own_find_entry proves entry-return lookup equals nested-Option lookup with its key restored; nearest_entry lifts the relation over parents. owner_bridge/lookup_bridge preserve absent owner, owned None and actual payload. valid_bridge relates per-node pairwise key inequality to Nodup of projected keys.

emitted_membership proves both directions between actual modeled cursor drain membership and the count model's nearest owner. It uses the iterator's independent recursive reference theorem and uniqueness, not an assumed correct raw stream. raw_enumeration combines this equivalence with derived key uniqueness. This discharges the previously open RawEnumeration interface.

ready_live_count applies the count component's independent finite-roster cardinality proof to this derived raw enumeration. ready_reference_count discharges the iterator getter's exact live-length premise. getter_bridge is a legitimate definitional equality between the two identical final guard/filter/index operations; it is not the substantive count proof. ready_index_exact/in_bounds and index_value then give complete indexing and nearest-owner present values.

Histories composes finite_history from the empty map with those joins. Every finite operation sequence, and every finite prefix, has stored count equal to live drain length. Below-count indexes return entries; out-of-range indexes return None. Returned keys are unique across indexes, and values are the nearest current owner. These conclusions do not assume endpoint RawEnumeration, endpoint length coherence, or CompareSound. They quantify arbitrary supplied unique/shared branch outcomes and arbitrary comparison results, with native branch admission retained separately.

Only history_value_reference, which equates resulting payloads with the independent sequence of requested updates, needs CompareSound. The unsound-comparison witness explicitly shows skipped requested insertion with a still-coherent empty count. This prevents mistaking count safety for successful value-update semantics. Native PartialEq can omit metadata; the model payload quotient/observer contract remains external when claiming requested-value equivalence.

The reusable Ready lemmas also support any admitted initial Ready state. The unconditional history corollaries start from the modeled empty initializer; they do not migrate originally corrupted counters. Caller-produced arbitrary initial states need the stated readiness relation.

## Counterexamples and semantic discrimination

The original specialized operation model begins empty, seeds nine keys, removes one through a unique branch, then restores it through a shared expanding branch. It derives old counts 9/10 against independent live counts 8/9 and a real two-node model chain. This is a reachable modeled history, not a browser reachability theorem. The repaired history uses shared removal/expansion, preserving tombstone ownership and counts 8/9; its complete-index witnesses use the general composition theorem.

All eight predecessor mutants reran successfully through their intended semantic gates. Three new wiring mutants compile complete definitions before execution. Against the same five independent observations, baseline is all true; flattened raw traversal yields false|false|true|true|true, unfiltered indexing yields true|false|true|true|true, and collapsed tombstone ownership yields true|true|true|false|true. Definition logs are successful and the exact output grammar is checked. These discriminate integration behavior; they do not mutate Rust or substitute for the universal proof.

Eight reviewer integrity negatives reject before output creation: extra file, empty directory, changed input, missing input, symlink, duplicate manifest key with a recomputed outer manifest seal, aliased input-name spelling with a recomputed seal, and nonisolated invocation. The aliased-input test is rejected at closed roster rather than the later unsafe-path assertion; exact causes are retained in GUARDS.json.

## Exact source connection and remaining scope

Both imported full original files match d29360da7b8e104a7957ea9db068b25222dbcb3514c5e4999f812c1e812cf7a6. Both final combined files match 9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d, the independently reviewed formatted native candidate. Replayed 54 iterator and 48 count method bindings overlap; they are not 102 distinct functions. Exact text and final source joins are verified, while Rust-to-Lean lowering remains manually reviewed.

The formal joint premise is now closed, but native IndexMap ordering/uniqueness/equality, exact immutable iteration, atom representation, finite acyclic Arc chains, copy-on-write/borrow/allocation behavior, actual ancestor_count metadata, filter/nth semantics, machine integer bounds and compiler semantics remain admissions. Nat termination/count theorems do not establish unbounded Rust arithmetic or heap safety. The completed component concerns one map. CSSOM's inherited/reset disjoint domains, registration routing and changes, count conversions/FFI, live style publication and invalidation remain external. The root finite browser matrix and source review are separate evidence; no browser, native build, or Git action was performed here.

## Checker limitation and replay qualification

The top checker enforces isolation and authenticates a closed source/dependency tree before execution. Its external-output test uses Path.absolute() and lexical is_relative_to. A path containing an existing sibling directory followed by '..' can pass that test while resolving inside the capsule. OUTPUT-PATH-LIMIT.json records the exact predicate witness without running the checker on that path or mutating sealed sources. The eight negative guards do not establish rejection of this alias. The inherited iterator checker has the same path pattern; the inherited count checker has weaker output/isolation guards, which the top wrapper supplies for this run.

For this independent replay the output was explicitly canonical, external and fresh. Therefore the path guard defect does not affect the accepted proof replay. It remains a tooling limitation, and future callers must resolve/validate the output path themselves until separately corrected. External authentication of the capsule remains required.

## Reproduction and cleanup

Run `python3 -I -S capsule/check.py --output ABSOLUTE_RESOLVED_NEW_EXTERNAL_DIRECTORY` after verifying the external review and producer pins. The top checker reruns both dependencies and all new audits/mutants. The exact invocation appears in replay.log/receipt commands; source-only reproduction requires the pinned external Lean toolchain.

All needed proof/mutant sources, compile/audit logs and results were retained under receipts. Completed reviewer-owned compiler output and deliberately corrupted copies were then removed; CLEANUP.json records exact paths and byte totals. Sealed predecessors and live sources were unchanged.
