# Saturation repair: proposed complete formal scope

**Status: proposal for root approval, not an implemented or accepted proof.** This scope is for the four-file saturation candidate authenticated in `candidate-review-v1/`. Sparse scoped-name root resolution remains a separate known defect. The theorem must not claim complete CSS name scoping or arbitrary DOM depth.

## 1. Intended result and three distinct evidence layers

The mathematical target is universal over arbitrary finite admitted provider inputs, not only lists already carrying correct priorities. Starting with a raw, structured shadow/slot/style-map description and declaration blocks, the candidate collector must produce a declaration/rollback observation equal to an independently defined encapsulation-aware cascade reference, throughout the supported numeric domain.

Keep three results separately named and reported:

1. **Universal model theorem:** for every admitted raw input, the complete model's collection, sorting, rule-tree linearization and cascade control agree with the independent reference. Also prove exact bounded encoding and explicit overflow behavior.
2. **Native correspondence evidence:** a complete source extraction/translation ledger plus fresh finite differential execution against the frozen candidate. A test corpus, compiled harness or hash match is not a proof of universal native equivalence.
3. **External provider and browser evidence:** reviewed source chains and root's paired WPT receipts establish finite native integration. DOM, selector matching, parsing, evaluation, invalidation, memory safety, allocation success and ABI are not silently turned into proved premises.

The final report must state which native bridge is proved versus tested. If universal native equivalence is claimed, require a checked refinement of every extracted control-flow component and adapter. Otherwise label the universal result a model theorem with finite native agreement.

## 2. Raw input and admission must be executable and noncircular

Define raw input before defining a collected action plan. It includes:

- A finite graph of element/root identities with explicit containing-root, host, owning-root and assigned-slot edges; originating element and full pseudo sequence; exportparts mappings and target part names.
- Stylesheet data for each relevant root and the document: absent/present maps, empty maps, exact pseudo-map paths, normal/host/slotted/part map contents and rule source identities.
- Unordered candidate rules with match outcomes, layer orders, specificity, scope proximity, source order and flags; declaration blocks with ordered properties, importance, ordinary values and every relevant CSS-wide/revert classification.
- Same-tree, UA, user, presentational-hint, inline, position-fallback, animation and transition contributions actually reachable through the selected entry point; explicit guard/provider results for dynamic inputs.
- Consumer state needed by longhand/custom paths: property identity, inheritance/initial action, seen state, rollback state and relevant evaluation/filter flags. Do not erase branches because the browser fixture did not take them.

Admission checks finite acyclic required traversals, edge consistency, root/slot host identities, valid origin/layer/flag domains, legal declaration classification, numeric bounds and documented provider contracts. It must not assume collector output is sorted, important groups already ordered, priorities faithful, rollback correct, or final observations equal. Those are conclusions.

If certain provider outputs are impossible by source construction, prove the constructor invariant or record it as an explicit external premise with the producing function. Do not restrict raw input to a hand-authored action plan and then prove only that plan executes correctly. A surjection/normalization theorem must connect every admitted raw input to the execution domain.

Retain explicit witnesses for empty input, zero slots, one context, the original failing filled and sparse layouts, at least eight dense contexts, at least seven forwarded slots, mixed layers, repeated sources, both importance classes, all rollback kinds, and representational boundaries. Prove admission of the witnesses independently of the top-level equality theorem.

## 3. Supported domain and separate overflow theorem

Let M=2^27−1=134,217,727. Orders in [−M,M] have an injective u32 encoding; signed order is i32. Origin occupies bits0–2, importance bit3, magnitude bits4–30, signbit31. No negative zero or noncanonical extra bits are introduced by native constructors.

Full collection correctness requires at most M eligible outer part-map contexts; n assigned slots are admitted through n≤M, with own-host declarations additionally requiring n+1≤M. Count eligible positive maps exactly as the current collector does, including empty maps. Slots count every actual assigned-slot hop, including roots without a matching map. Positive ordinals preserve physical encapsulation order even where maps are sparse; this is sufficient for declaration precedence and does not repair scoped-name root decoding.

Also prove a separate total fallback property for finite inputs beyond M: the collector emits the exactly representable prefix of outer contexts; omits unrepresentable far slots/own host; preserves exact ordinals of all nearer slots; never wraps, aliases distinct admitted contexts, crosses zero or turns overflow into same-tree scope. Prove checked usize index+1 behavior including usize::MAX. This fallback is incomplete CSS outside the support domain and must not be described as normative correctness there.

Prove arithmetic over mathematical integers, then discharge native-width preconditions: shifts, casts, unsigned absolute value, signed negation, guarded successor, index addition, vector lengths and loop termination. Do not use “the DOM would run out of memory first” as admission proof. Retain architecture width and allocation success as explicit operational premises.

Existing independent limits also matter: source order is masked to24bits; finite scope proximity clamps below u16 infinity; layer order is u16 with reserved root/style-attribute values. Either admit exactly the ranges where the spec-level order is preserved, or state and prove only the corresponding existing native semantics outside them. Do not conceal these limits under the new shadow bound.

## 4. Obligations through the complete native path

| ID | Required theorem/refinement | Native correspondence points |
|---|---|---|
| C1 | Shared pseudo/origin normalization and raw traversal reachability; same raw input controls provider dispatch | `Stylist::push_applicable_declarations`, `RuleCollector::new`, `collect_all` |
| C2 | Exported-name propagation, loop termination, exact eligible-map counting, boundary stop and per-root collection | `collect_part_rules_from_outer_trees`, `each_part`, `each_exported_part`, `part_rules(pseudo_elements)` |
| C3 | Direct inner ordinals, own-host n+1, reverse slot traversal and absent-map behavior | `collect_host_and_slotted_rules`, `collect_host_rules`, assigned-slot providers |
| C4 | All surrounding origin contributions and matching metadata are placed correctly | UA/user/presentational hints, containing tree, document, style attribute, animation/transition collectors |
| C5 | Local sorting produces layer/specificity/proximity/source precedence; tie behavior does not change the observation | `in_tree`, `ApplicableDeclarationBlock::sort_key`, `Rule::to_applicable_declaration_block` |
| C6 | Exact packed encoding, order projection, important reversal, transition precedence and layer/style-attribute comparison | `CascadeLevel`, `ShadowCascadeOrder`, `CascadePriority`, `LayerOrder` |
| C7 | Adjacent source/priority elision preserves the complete observation, with source identity/flags semantics explicit | `RuleTree::compute_rule_node`, source keys, `for_rule_tree` |
| C8 | Important partition, stable sorting/skip optimization, origin grouping, transition stashing and insertion preserve reference order | `insert_ordered_rules_with_important` |
| C9 | Rule-node insertion and ancestor/declaration iteration yield the required descending sequence without losing priority or importance | `ensure_child`, child key/equality/hash, self-and-ancestor and declaration iterators |
| C10 | Per-property longhand rollback/seen/importance/filter state machine selects the reference terminal action | `Cascade::apply_one_longhand`, priority `allows_when_reverted` |
| C11 | Custom-property rollback, seen removal and evaluation/deferred state agree with their own reference path | `cascade_custom_property` and relevant custom-property iterator/evaluation branches |
| C12 | Selected declaration's context bits are propagated unchanged where scoped values are computed | temporary `context.scope`, `TreeScoped` conversion; no claim that the separate root decoder is correct |
| C13 | Top-level composition: arbitrary admitted raw input reaches C1–C12, equals the independent observer, and terminates | The actual public extraction entry point, not a pre-sorted list entry point |

C5 must address `sort_unstable_by_key`: prove that equal-key alternatives are observationally equivalent under source/provider invariants, or model all legal permutations and prove the observer invariant. Do not replace it with stable sort without justification.

C7 must include flags, identity aliasing and repeated declaration blocks, not merely duplicate numerical priorities. C8 must prove why an important vector whose first and last priority are equal may skip sorting: endpoint equality alone is not a general sorting theorem. Establish the actual collector/order invariant for every admitted input. Stable important sorting must retain local tie order. Include empty normal-only blocks, mixed-importance blocks and the at-most-one final transition premise.

C9 may use an abstract immutable path interface only if node interning/cache identity and equality/hash preservation are explicit external or proved interface obligations. An empty ensure-child mock that simply appends cannot establish Gecko rule-tree correspondence by itself.

## 5. Independent reference and observations

The reference starts from physical root ancestry and declaration provenance, not packed levels or native traversal output. It builds applicable contributions from provider semantics and assigns mathematical encapsulation relations. For normal declarations outer contexts outrank inner; important declarations reverse that relation. Origins, layers including inline exceptions, specificity, scope proximity and source/declaration order determine the remaining relation.

Define rollback as declarative removal of the relevant origin/layer/rule region followed by reference selection. Do not implement the reference by calling `allows_when_reverted`, using native packed priority comparison, or replaying the native seen-state loop. Prove the reference relation agrees with the actual CSS rules in the admitted domain; record current primary citations and any interpretation choices.

Observe at least: collected contribution identities and provenance; exact priorities; locally sorted groups; normal/important rule path; final descending declaration trace; per-property encountered/ignored/reverted decisions; terminal selected declaration or initial/inherit/unset action; longhand/custom results under explicitly supplied evaluation providers; and propagated scope bits. Comparing only the final width can hide dropped contexts, duplicate rules, wrong intermediate order or compensating errors.

Opaque value evaluation can be parameterized, but the theorem must state that it proves selection/control under those providers, not universal computed-value correctness. Variable substitution, registered custom properties, visited filtering and invalid-at-computed-value behavior must have explicit modeled branches or documented provider boundaries; no unannounced grammar reduction to four test declarations.

## 6. Provider ledger and dependency boundaries

For each external interface retain full definition/caller chain, argument/result types, invariants needed, source hashes, native test coverage and proof status. At minimum:

- DOM roots/hosts/slot assignment, pseudo-origin reconstruction, finite graph and restyle coherence.
- `ShadowParts` parsing and forward export mapping, Gecko FFI return arrays/lifetimes, Rust part iterators.
- Exact pseudo-map presence semantics, including empty normal maps in a container holding only pseudo rules.
- Selector matching, per-rule source identity, layer allocation, specificity, source order and proximity computation.
- Property declaration classification and iteration order; importance predicates; rule flags; locks/source lifetime.
- Rule-tree interning and ancestor iteration; declaration guards; independent evaluation providers and defaults.
- FFI layout/header generation, `StyleCascadeLevel::ShadowCascadeOrder`, Rust/C++ integer agreement and actual size assertions.

Existing independently reviewed important-sort or duplicate-elision work may be reused only with its exact admitted contract and frozen source binding. Do not assume a prior theorem proves a stronger raw-provider domain. State every dependency in the final theorem and replay closure.

Sparse `get_shadow_root_for_scoped` is expressly unresolved. No theorem may claim that emitted scope bits identify the correct physical named-definition root. A reference to a named value can still be treated as an opaque selected token with scope bits, with this semantic boundary visible.

## 7. Native extraction, corpus and adversarial gates

Freeze every source file used by the extraction and observers, the build/configuration assumptions, adapters, generated C++ header, proof files, toolchain versions and complete replay command. Before execution authenticate the package from externally supplied manifest/checker pins. Use an isolated output directory. Do not read live production sources during replay or rely on precompiled binaries as the only evidence.

Retain a machine-readable extraction ledger: every native function body, transformation, removed derive or unavailable dependency, adapter, provider stub and observer. Explain the correspondence of complete dispatch and loops. Source hashes alone cannot validate a hand-reimplemented model.

Fresh finite native/reference corpus must include mixed origins, layers, inline exceptions, important vectors/ties, source duplicates, empty and missing maps, full pseudo-map presence patterns, export renaming/fan-out, normal/important mixed blocks, longhand and custom rollback chains, host plus slots, sparse and dense positive contexts, exact order boundaries and overflow. Synthetic reduced caps exercise traversal beyond bounds; label them transformed executions, while real-M scalar checks validate actual arithmetic. Report exact generated/accepted/rejected case counts and semantic coverage; no duplicate-row inflation.

Mutations must be demonstrated to fail for specific obligations: old3-bit mask; truncating C++ helper; positive count moved outside map branch; saturated successor; index+1 wrap; saturated negative rewind; skipped own-host offset; reversed slot insertion; wrong important direction; unstable important ties; layer-first/context-first swap; omitted transition reordering; overbroad duplicate removal; rollback using important comparison; custom seen-state omission; wrong export termination; and ignored raw-input dispatch. Keep the sparse physical-depth decoder mutation outside claims of saturation repair: it is an existing known issue, not a new passing invariant.

Proof audit must reject sorry/admit/axiom shortcuts, opaque imported assumptions beyond the declared foundation, vacuous admission, false external premises and circular reference definitions. Include deliberately corrupted source, manifest, extraction, observer, proof and expected-result tamper gates. A mutation that misses the corpus must be reported, not silently dropped.

## 8. Required deliverables and root approval boundary

Deliver a source-only replayable package with: exact candidate/dependency pins; executable raw-input admission; formal definitions and C1–C13 proofs; numeric and overflow lemmas; independent reference; complete extraction and provider ledgers; full observers; finite differential/mutation/tamper results; theorem axiom reports; fresh replay receipt; and a limitations/verdict table separating model, native and browser claims.

Before calling this complete, an independent reviewer must authenticate the frozen package, inspect the substantive proofs and correspondence, run a fresh full replay, and report each C obligation. Root retains final acceptance. A successful scalar/collector test package already exists, but it does not satisfy this larger proposal by itself.

Approval requested from root is the scope above, including the bounded CSS contract, complete raw-provider-to-observer composition and explicit unresolved sparse semantics. Any implementation difficulty or proof failure must be surfaced as an unmet obligation, not resolved by silently narrowing admission, dropping providers, or ending the theorem at an already-sorted action plan.
