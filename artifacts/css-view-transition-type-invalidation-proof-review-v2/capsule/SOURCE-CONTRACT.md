# Source and provider contract

## Exact changed control

`SOURCE-BINDINGS.json` retains eleven complete bodies, located in retained full source files by unique markers and balanced lexical braces. `source_extract.py` re-extracts and byte-compares them. This deliberately handles these pinned C++ bodies; it is not a general C++ parser or proof of compiler translation.

The three formatted native candidate file hashes are recorded in `evidence/FORMATTED-CANDIDATE-v1.json`. The only change from the offline `CANDIDATE-SOURCE.json` is whitespace alignment in TypesChanged. The retained offline patch remains historical, not the exact final formatted patch. Root's final source/build/paired-WPT/package receipts are separately copied and hashed by EXTERNAL-IDENTITY.json. The checker authenticates retained evidence; it does not rerun Firefox, apply patches, or infer that an external receipt is a formal proof.

| Native boundary | Model | Provider or scope restriction |
| --- | --- | --- |
| Add Has/error, SetAdd/error, atomize, AppendElement, TypesChanged | `edit .add`, `mutate`, `helperCalled` | Native/public membership agrees at each call boundary; value equality maps to atom equality. Error states return before native changes. |
| Delete SetDelete false/error; RemoveElement then TypesChanged | `edit .delete` | Successful returned membership agrees with native list. Unique types gives ordinary set deletion. No initial deduplication prerequisite patch is assumed. |
| Clear SetClear error or native empty; Clear then TypesChanged | `edit .clear` | Public/native consistency and generated helper failure contract are explicit. |
| TypesChanged active identity then root | `notified` ownership/root conjuncts | Identity is fixed during each mutation/flush interval. A successful old-object operation still invokes helper, but cannot enqueue this document's current-owner restyle. |
| nsLayoutUtils composed document/prescontext gates | `Environment.live` | A root/composed/presentation projection is supplied for the analyzed interval. |
| RestyleManager disconnected/destroying guards and Servo_NoteExplicitHints | additional manager-ready work-delivery premise | `live = true` alone does not prove an actual request is accepted. The manager must be connected, shell nondestroying, and calls outside Servo traversal. These premises are not Lean theorems about Gecko. |
| Root RestyleSubtree hint | modeled pending obligation | Actual root/descendant/pseudo traversal coverage is admitted. No equivalence with Gecko's actual dirty-bit representation is claimed. |
| direct active-type matching | `evaluate .activeType`, active owner and native membership | Source selector parsing/validity/state-bit and atom translation remain provider premises. Nat names are abstract valid names; alpha/beta fixtures instantiate them. |
| CSS rules and resulting property values | `resolve` ordered target rules | The oracle has explicit Boolean predicates and ordered replacement. Mapping its values/rules to actual cascade/inheritance/property resolution is admitted. |
| computed-style flush | `flush` visited subjects | Deliver visits, evaluate rules against current membership, apply results. This is a work/resolver contract, not an assumption that final cache values were already correct. |

The generated helper namespace is retained from the authenticated preceding type-set companion. Its scope/ToJSValue/backing-object/string-conversion/JS::Set* failure exits are visible. This capsule does not prove SpiderMonkey's JS Set failure atomicity, OOM behavior, reflector initialization or atom allocation/lifetime internals. An error returns before native mutation, but later Has/Delete routing additionally needs public/native agreement to survive the error. Arbitrary abstract error histories refine native histories only with that continuing representation/provider contract, or at newly established consistent cutpoints. The C++ calibration's injected errors preserve its mock backing collection; that is a visible test provider choice, not evidence of real JS Set OOM atomicity.

## Cache theorem boundaries

`Coherent` says each observable cache is current or a subtree rematch remains pending. `mutation_preserves`, `flush_preserves`, and `history_preserves` prove this for arbitrary finite operations, supplied rules and subject lists. `history_then_flush_observation` derives actual equality after a complete delivery. `evaluate_membership_congr` and `resolve_membership_congr` establish the rule oracle depends on membership rather than list order.

The pending Bool is a conservative abstract obligation, not a model of one native global dirty bit. Several partial deliveries whose union covers the domain may leave it true; only one individually complete delivery clears it. The invariant tolerates this conservative debt. No fairness, traversal liveness, batching optimization, or precise number of native scheduled traversals is proved. `requests` counts accepted calls in the projected provider and may exceed the number of traversals.

The environment fixes active-owner identity, root, topology, subject domain and presentation for an interval. Start, completion, owner replacement, root replacement, adoption and presentation construction are external lifecycle cutpoints requiring an established initial invariant. Mutation of an old owner is allowed inside an interval. Mid-traversal mutation/reentrancy must restart or establish a coherent cutpoint; it is not hidden in the theorem.

An absent presentation makes no rendered-style freshness assertion. The manager-ready premise is required in addition to the three fields in `Environment.live`. A fully modeled Gecko scheduler, restyle backend, invalidation propagation, general CSS cascade, or whole-browser equivalence is outside this artifact.

## Source calibration versus browser evidence

The C++ harness compiles the exact formatted Add/Delete/Clear/TypesChanged/nsLayoutUtils::PostRestyleEvent bodies. Its atom, array, generated SetlikeHelpers, document, manager, rule evaluation and cache traversal adapters are explicit substitutes. Only the first five source bodies execute; restyle backend/state snapshot/generated helpers are retained source contracts. Instrumenting Document::GetActiveViewTransition counts helper calls because it is the first expression in TypesChanged; the harness style evaluator reads its owner directly, avoiding accidental instrumentation calls.

15,234 fixed cases cover eighteen WPT operation/owner projections, every single operation/error over two names/two objects/three ownership states/eight presentation configurations/four initial masks per object, and all length-three histories over ten selected actions for six initial owner/type states. Three partial/full delivery masks exercise root-only and remaining-subtree coverage. A second independent bitset oracle agrees with Lean and source-shaped C++ at every snapshot. Finite equality is calibration, not a universal refinement theorem for the native adapters.

The five calibration subjects project the revised WPT's root color, descendant width, root ::before opacity, descendant ::before opacity, and view-transition-group(root) opacity. Integers encode observed property values. The synchronous WPT observes only the first four; the ready WPT observes all five. The harness models all five in every case as an extra synthetic subject. Old-object WPT cases observe only root and descendant; beta rules provide the current-owner blue/61px controls. No browser assertion is invented for the extra synthetic observations.

The original-source adapter reproduces six style discrepancies among the eighteen projected cases; helpers/counters may differ in other cases without an observable style difference. Root's independently retained final WPT/regression receipt records 6 FAIL/36 PASS to 42 PASS, including the new eighteen tests and existing tests. The proof checker neither executes those browser tests nor treats their finite success as a resolver/traversal proof.

## Required counterexamples

Boundaries.lean proves missing notification leaves root/descendant/pseudo stale; a root-only visit retains other debts; clearing debt after partial delivery is incoherent; a saved pre-latest-mutation snapshot gives a wrong cache; and fabricated old active flags with current type membership lose a real Delete dependency. The latter is a reduced-policy counterexample, not a claim that a tested alternate Gecko repair used that exact implementation. No new security or initial-deduplication claim follows.
