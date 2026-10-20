# Independent review v2: view-transition type invalidation

## V1 closure correction

The first review sealed a generated calibration bytecode cache inside its copied producer capsule. Although the mathematical replay had passed before that import, the resulting nested capsule was not replayable under its own closed-roster checker. V1 is preserved as historical review with a packaging defect. V2 removes only that cache from the new copy, suppresses bytecode before guard-module imports, and adds a separate nested producer roster check to the outer checker. See `V1-ERRATUM.json` and `CORRECTION-GATES.json`. All producer inputs, theorem claims and source admissions are unchanged. `replay/` retains the original successful evidence; `replay-v2/` records the corrected full replay.

## Verdict

**Accept the frozen component at its stated conditional mathematical and finite source-calibration scope. No remaining blocker found.** This is independent review advice; root owns acceptance. It does not establish universal Gecko restyle, selector, CSSOM, scheduler, or lifecycle correctness.

Authenticated externally supplied FILES, FREEZE, checker and report hashes before execution; all 46 regular-file inputs and the exact roster matched. A fresh manifest-only relocation replay passed: 39 axiom reports, four Lean modules, 11 complete source-body bindings, 15,234 cases and 51,702 snapshots. Retained commands, stdout, mutant sources, generated C++, and raw observations are in `replay/`. No browser, Firefox build, production edits or Git mutations were performed in this review.

## Mathematical review

Read all definitions and proofs in Invalidation and Boundaries, the calibration driver, axiom driver, source contract, architecture, extraction, checker, compiler and reference oracle. `RECONCILIATION.json` verifies the exact declared/printed/reported 39-name roster. Fresh axiom reports use only `propext` and `Quot.sound` (some use neither); no proof holes or foreign axioms were accepted.

The core invariant is substantive: within a fixed environment and observed subject domain, each stale cache entry entails pending work. Mutations derive the notification condition from effective edit, owner identity and presentation guards, rather than assuming a cache refresh. Silent mutations preserve current-owner membership. Arbitrary finite mutation/delivery histories preserve this invariant; a later complete delivery yields the current evaluator result. The evaluator separately interprets Boolean predicates and ordered last-matching rules, and membership congruence is proved through both functions. It is a small interpreted rule language, not the CSS selector/cascade implementation.

The pending Bool is conservative debt. Two partial deliveries can jointly refresh every subject while leaving it true; this is safe and does not model exact native pending-bit clearing or request coalescing. The flush transition evaluates the current state by definition. Actual traversal/resolution implementing that work is an external contract, not a proven native fact. The theorem derives freshness under a complete delivery; it does not prove delivery, bounded latency, or termination of the browser event loop.

Eight independent kernel challenges passed (`IndependentChallenges.lean`): split deliveries; mutation between partial deliveries; latest-state complete delivery; an incoherent starting state that a no-pending flush does not repair; ownership handoff requiring a new cutpoint; negated type predicates without an owner; the explicit visited-subject flush contract; and empty observation-domain limits. These witnesses expose the required premises instead of silently strengthening the theorem.

## Source and calibration

All three candidate source snapshots are byte-identical to the preceding independently accepted native review. All 11 bound bodies were checked at their retained offsets and hashes. Five complete production bodies are compiled in the C++ harness: Add, Delete, Clear, TypesChanged, and the nsLayoutUtils posting wrapper. Other bound bodies inform the source contract. A wording qualification: `source/PostRestyleEvent.cpp.txt` is a complete function slice, not all of nsLayoutUtils.cpp; the bound body is complete.

The mocks supply atoms, array/JS-set behavior, errors, manager posting, evaluator and delivery. They are not compiled Gecko/Stylo or WebIDL runtime. Compilation is `-O0 -g`; this review makes no optimized-build claim. The original source runs the first 18 cases only and differs in six intended rows. Candidate and mutants run the full advertised roster. The independently expressed bitset oracle and Lean rule evaluator agree with the extracted C++ control flow in that finite domain, not for arbitrary strings, allocations, failures or real styles.

The initially identified draft input-admission gap was corrected before freezing. The final validator enforces strict integer types (rejecting Bool), actor/name/error/mask ranges, action framing and exact keys; it independently reconstructs every advertised case and order. Independent malformed actor/name/owner/mask/framing/field/omission/duplicate/reorder challenges reject. Golden receipt agreement alone was not used to establish roster completeness.

## Mutation causes

All six C++ variants compile and execute successfully. The four mutants produce actual observation differences, not malformed-output/compiler failures:

| Mutant | Edited layer | Differing rows | Discrimination |
| --- | --- | ---: | --- |
| missing-notification | Extracted production helper control | 1,781 | Missing request/debt and stale root, descendant and pseudo values |
| owner-guard | Extracted production helper control | 3,310 | Extra request/debt from a non-owner mutation |
| root-only-delivery | Substituted traversal/cache provider | 442 | Stale descendant and pseudo observations after claimed complete delivery |
| drop-partial | Substituted traversal/cache provider | 348 | Premature debt clearing; the mathematical boundary witness also proves incoherence |

Three Lean mutations are well-formed semantic changes. Lost notification breaks the effective-active request/silent-current-type proofs; premature clearing breaks flush preservation with an unvisited subject. Root-only rematching first fails a `change` tactic's definitional match, which alone would be insufficient evidence of false semantics. `SemanticMutationWitnesses.lean` independently defines the exact mutated flush and proves both stale descendant/cleared debt and incoherence, with successful kernel compilation and ordinary axioms. Thus the defect is not inferred merely from a brittle proof script.

The synthetic previous-active-state deletion example is a reduced policy counterexample: both tests use the new empty type list and lose the old match. It is not execution of an alternative Gecko patch.

## Explicit remaining admissions

- Atom/name representation, unique and coherent native/public set membership, allocation/error behavior, and consistent continuation after errors.
- Fixed owner, topology, presentation guards and subject domain within a history; lifecycle changes need their own cutpoint relation and coherence argument.
- Connected manager, non-destroying shell, no forbidden traversal/reentrancy, and accepted post semantics. The three modeled presentation guards alone do not prove manager readiness.
- Correct coverage of actual descendants and generated view-transition pseudos, actual selector/cascade resolution, current-state work consumption, and CSSOM observation synchronization.
- Natural-number counters and abstract finite data versus machine bounds, heap/object lifetime and native compiler correctness.
- Pinned Lean/Clang executables do not pin every installed Init/Std/runtime/compiler-resource/OS component; those remain trusted as the producer explicitly documents.

## Replay safeguards and cleanup

Nineteen independent negatives passed, including -O/-OO, nonisolated/site-enabled execution, a local json.py shadow before imports, altered source, added file/directory, nested seal, symlink, and the nine case controls above. The top guard executes immediately after builtin sys import; child Python invocations preserve -I -S. Closed regular-file/directory authentication and resolved external output checks were reviewed. These are integrity checks, not adversarial sandbox or formal parser proofs.

`CLEANUP.json` and `CLEANUP-V2.json` record only completed owned compiler binaries, debug bundles and oleans removed after retaining commands, sources, raw results and challenge receipts. The local `check.py` authenticates this review and retained results; rerunning the full proof requires a new external output directory using the unchanged copied producer checker. Frozen producer and earlier native-review artifacts remain untouched.
