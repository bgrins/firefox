# Recursive typed-attribute preparation: final source review

## Decision and authorship

The exact one-function draft composes with the current namespace+tombstone stack. No blocking defect found by this static source re-review; accept it for root's build and paired tests, not as completed native acceptance. This reviewer authored the earlier draft, so this is an additional source audit by its producer, not an independent external implementation review. Root remains responsible for that distinction and the final acceptance gates.

`original/cascade.rs` is the exact tombstone candidate268d… and custom_properties.rs isff3b…. Relative to the namespace-v2 base used by the earlier draft, the only cascade difference is the contains_attr tombstone guard. `candidate/cascade.rs` preserves it. `recursive-preload.patch` is byte-identical to the sealed earlier patch950083…. Custom-properties source is unchanged. No production file or Git state was edited; no compiler or browser was run.

## Complete source path

`VariableValue::parse` creates a separate `References` list for each fallback. Parser flags propagate outward, so the top-level ATTR flag admits a declaration with nested attr(), but `refs.refs` does not contain those nested entries. `Cascade::maybe_note_non_custom_dependency` calls `update_attributes_map` while collecting non-custom declarations. For ordinary width/height, no NonCustom graph node later visits the declaration expression itself.

The changed function retains its ATTR early return and cycle-work flag, then walks every syntactic fallback References list using SmallVec. Queueing the fallback precedes the outer kind, namespace and seen-key checks. This is required for nested typed attrs under var(), env(), untyped attr(), Unknown namespaces, and repeated outer names. Each admitted typed attr still uses the existing (namespace,name) seen set and success-only query/parse insertion. URL data remains the containing declaration's data, as before. No new clone of the reference tree or native recursion is introduced.

The original scalar loop becomes a borrowed worklist; all borrowed fallback lists live in the same declaration value supplied with lifetime'a. Existing imports already include References and SmallVec. Lifetimes and exact Rust type checking remain the compiler's gate. The loop visits the top-level entries first, then queued fallback lists in stack order; this is preparation order, not a normative function-evaluation order.

The collection phase finishes before `apply_custom_and_prioritary_properties` invokes `substitute_all`. Custom roots are processed before independent attr roots; both precede ordinary-property substitution. Therefore, a prepared `chain="var(--v)"` can resolve before a direct width fallback consumes it. Preloading does NOT mean that chain is already computed when an earlier custom root needs it.

## Used versus unused fallback risk

The patch queues syntactic fallback lists for preparation, but does not append them to the parent's references and does not create dependency edges from the referring declaration. `visit_value_references` retains its used-fallback condition. Thus a valid primary does not acquire a dependency edge to an unused fallback merely because that fallback's attr was prepared.

Newly seen attrs may subsequently execute as independent roots. An unused cyclic attr can invalidate its own root without invalidating a valid outer width. A dependency from an independent attr root to an already-resolved custom property is not a reverse edge. Custom roots are processed first, and native Attr nodes use `PropertyDescriptors::unregistered`; `find_non_custom_references` returns empty for that registration. Hence a raw font-relative unit in an independently prepared attr does not itself create a registered font-size dependency edge. Existing registered-property dependency traversal remains unchanged.

This is a concrete control-flow argument, not a universal proof that the current coupled evaluator is order-independent. Existing type-eligibility and other evaluation obligations remain. Required controls include unused cyclic attrs, unused custom self-cycles, used custom cycles, and the retained registered font-size cycle diagnostic. The patch must be rejected or corrected if any of these changes its independent expected value.

Preparation can add attribute reads, parsing, map storage and tracker dependencies for unused fallbacks. Over-invalidation and additional work are possible; no performance-neutrality claim is made. Traversal work is linear in the declaration's stored reference tree, with worklist space bounded by queued fallback lists. Successful/missing typed DOM queries are deduplicated by qualified seen keys for this preparation pass, while raw attribute text parsing has its existing input-dependent cost. The patch does not eagerly flatten or recursively parse all contents itself; chained value traversal remains in the existing graph stage. A seen key from an unsuccessful query remains seen exactly as before. The contains_attr guard later preserves semantic tombstones as repaired.

## Separate graph-eligibility defect stays visible

`visit_value_references` uses !v.has_references() to call a primary valid, without checking the requested syntax of this occurrence. Thus bad="not-a-length" can suppress graph traversal of a needed fallback. A warmed literal inner value may conceal that error; an inner attribute containing var(--v) exposes the custom-root timing problem.

The sealed19-case and6-case diagnostic files and expectations are copied byte-for-byte under diagnostics19/diagnostics6. They are not modified or marked passing. The19-case baseline raw log/receipt has9 FAIL,10 PASS,1 harness OK and stable pins. Its custom invalid-type primary case is a different issue from the eight ordinary-property preload failures. The6-case corpus distinguishes direct ordinary-property preparation from earlier custom-root evaluation.

Static prediction only: the minimal preload patch fixes the eight established direct/pre-prioritary preparation failures, while diagnostic19's invalid-type custom root and diagnostics6's two invalid-type custom-root variants may remain failing. Their expected values stay13px. Root's unchanged25-case execution adjudicates this; this review does not convert predicted residual failures into accepted results or narrow a failing test's assertion.

## Proposed final WPT

`attr-fallback-preparation.html` contains16 concise testharness cases. Ten are preparation witnesses: the eight established direct cases, a direct inner attr containing var(), and one new untyped-outer fallback. Six controls cover direct typed lookup, correct custom-root missing-primary traversal, numeric-unit bypass, unused cyclic attr, unused custom cycle, and used custom cycle. `CASES.json` maps each case to its original diagnostic or the one new branch-specific case.

The new untyped-outer case is necessary to discriminate a patch that queues fallbacks only after `is_attr_with_type`; such a weaker patch could pass the typed-outer cases. The raw-inner-var case checks actual resolution readiness rather than merely inserting a literal into the map. The final test is specifically for preparation; occurrence-type custom-root graph failures remain in the separate diagnostic corpus rather than being relabeled as this patch's passing behavior.

Each test inserts its declaration in a stylesheet with known namespace context, asserts the observed property parsed, uses a fresh unique target, and checks an absolute computed length. Cleanup removes both target and rule. There is no optional support exit, browser timing, font dependency or prediction metadata. Ordinary widths are read after cascade; the sole font-size witness intentionally has no custom-property admission trigger. The unit case bypasses typed-map preparation and is a negative control.

The primary CSS Values5 snapshot and retrieval metadata are preserved from the earlier authenticated draft. Its attr substitution failure branch chooses and substitutes the fallback on missing/unknown attribute or type failure; successful primary returns before fallback. Those steps determine expected values independently of preload order. No known namespace-chaining bug2021110 feature is required; namespaced outer-missing cases only test declared versus unknown prefixes.

## Verification and limits

Root's native build, unchanged25-case diagnostic run, final16-case baseline/candidate pair, existing attr/tombstone/namespace regressions, formatting/lint and standalone patch isolation remain separate gates. The final WPT is a new file and is UNEXECUTED by this agent; the historical19-case baseline is not its execution receipt. Scope is static source/fixture review; no universal Tarjan/native heap/provider or whole-substitution proof is supplied.

The standard-library checker authenticates every input before interpreting it, reconstructs the exact one-function patch, proves the tombstone guard and all other full-file bytes remain unchanged by direct comparison, checks fixture identity and retained diagnostic hashes, and reconciles baseline19 raw statuses. Fresh local and relocated replay plus intentional tamper rejection are recorded. This replay does not compile Rust or run the WPT.
