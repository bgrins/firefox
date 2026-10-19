# Outer query attribute dependency proof companion

This package accompanies the repair of `QueryCondition::collect_attribute_references` in `servo/components/style/queries/condition.rs`. It proves an abstract structural collector theorem and conditionally proves evaluation preservation. It also tests the exact extracted Rust visitor and collector with explicit adapters. It does not formally verify Rust, Gecko invalidation, or all attribute dependencies of CSS queries.

## Replay

From the Firefox repository root, choose a fresh output directory:

```sh
python3 artifacts/css-query-attribute-wrappers-proof-v1/check.py \
  --out artifacts/css-query-attribute-wrappers-proof-v1/root-replay-v1 \
  > artifacts/css-query-attribute-wrappers-proof-v1/root-replay-v1.log 2>&1
```

An independent reviewer may point `--out` at its own artifact directory. The runner compiles isolated Lean/Rust artifacts and does not build or run Firefox. It rejects changed source, unexpected Lean diagnostics, unapproved axioms, Rust compilation diagnostics, failed semantic controls and output-count mismatches. `RECEIPT-v1.json` is written only after all gates pass. Its `result` must be PASS and the process must exit zero.

`SOURCE-v1.json` authenticates the package source and the current native file. Replay intentionally rejects subsequent edits to that native file; use a newly reviewed proof version for a changed candidate. `TOOLCHAIN-v1.json` records and hashes the Lean and Rust compiler executables; compiler runtime libraries, Lean Std and the host OS remain trusted toolchain inputs, not exhaustively authenticated dependencies.

## Native identity and preservation

- Original native SHA256: `c20483cfdccdcb98d0e9961859aa00c80ba927a934de9ba635bacf20c2a7b19a`.
- Candidate native SHA256: `ddaf9143290bdf16fb4287f5a54facc57089537872280e228b2cfce98dd01188`.

The original file is archived from the root's pre-repair snapshot. The candidate is archived from the formatted source. `bridge.preservation` requires exact full-file equality after substituting only the outer collector body, including its signature. Consequently the parser, evaluation methods, inner style collector, visitor and every other byte are unchanged. Separate controls alter the visitor, evaluation, parser and leaf collector and require this gate to reject each.

`bridge.parts` extracts the exact `Operator` and `QueryCondition` enum declarations, `QueryCondition::visit`, and `QueryCondition::collect_attribute_references`. It does not reproduce those methods by hand. The old collector is also extracted and given a distinct method name solely to call it beside the new one. Enum derive macros outside the declaration are omitted; the standalone `Operator` adds Copy/Clone for ordinary Rust ownership. Declaration bodies and candidate methods are copied exactly.

The isolated bridge replaces feature/custom-media/preference payloads with tagged integers, GeneralEnclosed payload metadata with bytes, style-query payloads with a declared finite dependency list, and `AttrReferenceSet` with `std::collections::BTreeSet<u32>`. It keeps production Box/boxed-slice recursion, the native loop, and callback execution. These adapters preserve the intended outer traversal/set-union contract, but are not the real style-leaf collector, atom namespace handling, hash set or substitution engine.

## Formal model

`Query.lean` defines an independent outer AST and a mutually inductive finite child forest. Unary negation/parentheses and arbitrary finite AND/OR lists are represented. Native Feature, Custom, MozPref and GeneralEnclosed are represented as opaque leaves (`Expr.other`). A Style leaf holds an abstract identifier. Empty operation lists are permitted in the model and fixture adapter to test traversal totality; the actual parser's nonempty-operation invariant remains a bridge premise for evaluation.

The specification is a style-leaf occurrence relation, with an attribute required exactly when it belongs to the dependency list of an occurring style leaf. The executable model instead visits children sequentially and accumulates lists. `collector_complete` and `forest_complete` prove membership equivalence for every finite tree, every finite initial accumulator and every attribute. Duplicates and traversal order have no effect on the set-level contract.

Eleven audited theorems establish:

- Collector membership equals initial membership or an occurring leaf dependency.
- Initial entries are retained; every declared leaf dependency is included; no other dependencies are invented.
- Evaluation is congruent when all occurring style-leaf values agree and opaque values are fixed.
- Attribute environments agreeing on the collected set give equal evaluation **provided each style leaf obeys its stated dependency contract**.
- The old direct-only collector misses a parenthesized leaf.
- All operation branches are collected independently of truth, including branches that runtime evaluation could short circuit.

Evaluation uses an explicit three-valued AND/OR/NOT abstraction. Native Kleene helpers and their side effects are not extracted or formally equated with this abstraction. Full-source preservation separately establishes that this repair did not edit native evaluation. The theorem concerns result equality, not evaluation order, runtime AttributeTracker side effects or short-circuit instrumentation.

All theorem audits permit only Lean's `propext` and `Quot.sound`; no `sorry`, additional axiom, `unsafe`, warning or unexpected output is accepted. `by decide` witnesses are kernel-checked reductions, not unchecked external solver results. This package has no SMT dependency.

## Native differential checks and controls

The deterministic fixture oracle is separately implemented in Python as a tree leaf projection and set union. It also predicts exact preorder visit traces and the original collector result. There are 1,074 cases: all payload variants, empty/nonempty/shared/duplicate dependency lists, seeded and empty output sets, unary depths through 16, both logical operators over all terminal pairs, wide lists of 1,000 children, and 700 deterministically generated mixed trees through depth 7. Cases include empty operations as an explicit adapter-only extension.

The candidate must match every oracle output; the old collector has 557 counterexamples in this bounded suite. Six compiled semantic mutations must fail comparisons: restore the old collector, skip negation, skip parentheses, visit only the first operation child, skip node callbacks, and clear existing dependencies. Seven Lean semantic mutations separately test those structural obligations, spurious dependencies and wrong leaf identity. Diagnostic and source identity controls exercise rejection rather than merely trusting a successful exit.

These bounded native tests establish source binding and defect sensitivity. They do not turn the arbitrary-tree Lean theorem into a formal proof of the Rust machine code. That remaining bridge consists of the straightforward mapping between native enums/boxed slices and the model, production leaf dependency and set semantics, successful allocation and finite stack capacity.

## Required integration premises and exclusions

1. The parser constructs the intended outer tree, with actual Style leaves and valid operation invariants.
2. The production StyleQuery/StyleFeature collectors report all attribute dependencies that can affect their evaluation. The structural theorem assumes this; it does not establish it.
3. Attribute identity, namespaces, atom equality, and dependency-set insertion implement the intended set.
4. Changes outside the collected set leave opaque leaf results fixed. In particular, **GeneralEnclosed reparsing and custom-media expansion may hide dependencies not collected here**. They are excluded, not proved attribute-independent.
5. ContainerCondition parsing, dependency-map insertion, named/unnamed descendant selection and RestyleManager invalidation consume this set correctly. Root-owned WPT observations exercise selected integration paths; the Lean theorem does not prove them.
6. Native recursion/resources are sufficient. The mathematical theorem covers arbitrary finite trees; it does not establish stack safety at arbitrary depth.

The proof's attribute environment is a natural-number encoding of values. Actual DOM strings, missing attributes, namespaces, registrations and conversions require the leaf contract and do not follow from the encoding itself.

## Evidence ownership

The root's repair plan is `artifacts/css-query-attribute-wrappers-fix-v1/PLAN.md`; the earlier independent diagnosis is `artifacts/css-breadth-audit-round7-v1/conditions-independent/REPORT.md`. Root reported 76 FAIL/8 PASS for the 84 new baseline WPT subtests and 139 existing PASS. This companion does not rerun or authenticate those runtime receipts and makes no post-fix browser claim. The defect was found through source analysis/browser probes; these proofs characterize and check the repair, rather than retrospectively claiming Lean discovered the original browser failure.

Package source paths for a companion commit are listed in `tooling-paths-v1.txt`. Generated executables, mutated source copies, logs and development output directories are replay products and are not source companion files.
