# All shorthand ordering: formal and extracted-native companion

## Result and exact repair

The candidate's sequential `all` update agrees with an independent CSSOM setter reference in this artifact's admitted domain. Lean checks 55 theorem declarations. The source-only native bridge compiles the exact parent-owned candidate and original control flow with explicit adapters, and independently checks 3,042 operation rows per full variant. The candidate has no disagreement; the original has 294 transition disagreements. Six compiled semantic mutants produce concrete discrepancies and corresponding successful kernel witness theorems.

Original `declaration_block.rs`: `7239be79e4864599f55b5d8898f682366290900ff484b63ce491b5b221bd3f6c`. Candidate: `8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a`. The ordinary planner closure and extracted private helper have identical Rust token sequences. The repair changes the all preparation gate to consult that planner and executes all expansion sequentially against the current destination. No live source, WPT, browser, build or Git operation is performed by this companion.

## Normative scope

[CSSOM setProperty](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty) expands shorthands in a fixed canonical order and applies the per-declaration setter. [Set a CSS declaration](https://drafts.csswg.org/cssom/#set-a-css-declaration) requires a property to occur after members of its logical group with the opposite mapping kind. [CSS Cascade all](https://drafts.csswg.org/css-cascade-5/#all-shorthand) excludes direction, unicode-bidi and custom properties.

Absolute canonical order remains open in [CSSWG issue 5741](https://github.com/w3c/csswg-drafts/issues/5741). The theorem does not choose that order: for any fixed unique expansion containing mutually opposing A and B, the final identity projection onto {A,B} equals the expansion's projection. The source's logical-first convention is an input, not a normative conclusion. Retained primary specification bytes, issue 1898's discussion, merged PR 2516 and issue 5741's open state are authenticated inside `evidence/static`; its separate independent normative review is parent-owned. No novelty claim is made.

## Universal results

`lean/AllOrder.lean` defines an independent forward setter, a reverse scan yielding four native plan kinds, and indexed execution. Destination identity uniqueness is a premise; value equality is explicit `DecidableEq`.

- `planner_refinement` proves exact list equality between reverse planner/executor and the forward setter. `planner_valid` and `planner_index_bounds` derive replacement/removal indices from a real target split.
- `reference_filter` preserves the ordered sequence of unrelated declarations. Membership, uniqueness, finite sequence refinement and every-prefix refinement hold for arbitrary identities, values and priorities. Metadata is parameterized; `opposite` instantiates optional groups and logical/physical mapping, with irreflexivity proved.
- `planner_none_iff_unchanged` connects a non-None plan to an actual single-step change. `preparation_gate_actual_changes` proves the initial any(non-None) gate equals existence of a changing intermediate step. `[A,B]` updated by `[A,B]` can move A and then restore the original order: gate true does not imply different final cssText.
- `Storage` contains separate declaration payload and importance vectors plus membership. `rawStep` performs each actual append/replace/remove-and-append operation; it does not re-encode a final abstract list. `raw_operation_representation` proves aligned vectors and exact membership at operation boundaries. Move removal deliberately retains the identity bit transiently; reinsertion restores the public invariant. Raw sequence/prefix and guarded refinement compose from actual decoded state and derived planner indices.
- `pair_expansion_convergence` and its guarded variant prove the relational order statement over arbitrary unique expansions, preserving exact values/priorities and unrelated-entry order through the reference semantics. Custom and excluded IDs stay untouched when absent from expansion.

These are universal model theorems, not compiler correctness or a theorem that arbitrary native PartialEq implementations are equivalence relations. Native/model correspondence is finite and conditional on the provider and representation contracts below.

## Complete extraction and providers

`receipts/*-extraction.json` records every complete retained item's source file, start, body and SHA-256: 37 original, 38 candidate. This includes all ordinary and all branches of prepare/update; the candidate helper; complete push/extend/removal and removal-index lookup; declaration/importance iterator and get; identity-set insert/contains/remove/clear; source scratch/drain; the complete all iterator and enabled-property iterator; and all six CSSWideKeyword variants. Only unsupported derive attributes are supplied at the declaration boundary; method bodies are copied exactly. Fresh replay re-extracts them and compares the resulting inventories with retained receipts.

The complete retained `data.py` executes under a pinned stdlib TOML adapter and pinned counted-property/descriptor inputs. It supplies 431 Gecko longhand metadata records and the 406-entry all expansion, including actual sorting, filtering and exclusions. The Rust all and enabled-property iterator bodies execute over that generated data. Three synthetic preference profiles exercise all pref-controlled entries on, off, and an alternating assignment; these are not statements about shipping defaults. RevertRule is a direct typed provider case; its parsing preference is outside the bridge.

Explicit adapters replace ThinVec/SubpropertiesVec with Vec, SmallBitVec with a Vec<bool> wrapper, longhand/custom sets with BTreeSet, custom names with u16, ordinary payloads with u16, and unparsed variable equivalence classes with u16. Rust Arc is the standard library implementation. Capacity/allocation, atom interning, arbitrary specified-value arithmetic and generated representation layout are not verified. `zip_eq` asserts lengths. The complete native drain uses an actual Vec drain and is consumed/dropped; iterator lifetime correctness is external.

The actual PropertyDeclaration PartialEq template dispatches by variant and then payload equality; it is not globally Eq. WideKeywordDeclaration compares its identity and the exact finite keyword. VariableDeclaration compares identity and Arc<UnparsedValue>; UnparsedValue includes from_shorthand and VariableValue, whose actual PartialEq compares CSS text. These inspected sources justify an admitted equality quotient for new all values. The facade does not compile the unsafe generated representation cast, full CSS string/value provider or every native ordinary payload equality. Ordinary numeric witnesses therefore cannot establish native floating-payload reflexivity. Group/mapping metadata and stable callback/normal-allocation contracts remain explicit.

The normal batched algorithm is complete in the executable bridge and exercised with actual generated unique, group-uniform shorthand metadata. Its universal batching theorem remains a future component from the static roadmap. C++ mutation scheduling, CSSOM serialization, parsing, style resolution and rendering are external; parent-owned paired browser evidence supplies the browser gate separately.

## Finite evidence and mutations

Each full variant has 2,946 setter transactions, 94 shorthand removals and two parsing-extend transactions. Setter rows include six keywords plus variables, three pref profiles, both priorities, fresh/sparse/opposite-order/full repeated states, excluded/custom entries, normal longhands, all 94 ordinary shorthands and 500 five-step stateful ordinary histories. The source-defined all provider is checked against a separate direct enumeration/payload oracle. A separate Python checker independently reconstructs each case's actions, seeds and carry state, and recomputes reference setters/removals/parsing priority behavior from raw rows. Repeats and histories continue the actual preceding native state, including original-state failures; they are not falsely described as reset paired inputs.

Raw rows retain before/actual/reference/action sequences, importance bits and membership sets. Strict full-field parsers reject nonbinary flags, malformed vectors/sets, extra fields, wrong names, missing cases and self-consistent altered all actions. Complete variants require the exact ordered 3,042-case roster. The two representation mutants stop at the first invalid representation with deliberate exit 42 and require exactly the corresponding roster prefix ending in that failure.

| Compiled mutant | Failing rows | Successful kernel witness |
| --- | ---: | --- |
| Restore legacy all update | 294 | legacy_update_witness |
| Restore legacy all gate | 168 | legacy_gate_witness |
| Omit opposite-order check | 670 | missing_order_check_witness |
| Set true instead of requested importance | 63 | priority_downgrade_witness |
| Omit parallel-bit removal | 1 of 2 executed | missing_move_bit_removal_witness |
| Omit membership insertion | 1 of 1 executed | missing_membership_insert_witness |

These are six compiled native mutations and six kernel counterexample witnesses, not six rejected mutated Lean proofs. No syntax/compiler failure counts as a mutation witness. `AXIOMS.txt` audits every theorem: only Lean's standard logical axioms are admitted; no sorry, axiom declaration, admit or native_decide is allowed.

## Replay and integrity

Run `python3 -I -S check.py --output /absolute/new/output-directory`. Authenticate this directory's external FREEZE/MANIFEST/checker hashes first. The checker verifies every input before importing or executing capsule code, rejects duplicate JSON keys/paths, escapes, symlinks, nonregular entries, unexpected files and directories, authenticates the nested static artifact, and requires an output directory outside the capsule. Fresh replay uses only retained source and pinned tool binaries; no prebuilt harness or Lean object is an input. Runtime/toolchain/stdlib integrity, OS correctness and compiler/kernel implementation remain external trust boundaries.

`MANIFEST.json` is the exact companion commit roster, plus the root MANIFEST and FREEZE files. It excludes executables, object files and mutable replay output. Compressed raw traces are evidence, not executable dependencies. Final independent formal review and parent acceptance are still required.
