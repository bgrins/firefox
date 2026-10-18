# Accepted local gate

The first tagged-model compile succeeded with eight theorem audits. Six depend
only on `propext`; the two finite counterexamples use no axioms. The direct-key
model and a first compile with deprecated tactic names are historical, excluded.

Gate session 15787 exited 1 because the validator mistook nested `have ... := by`
blocks for multiple theorem body starts. No proof result from that run is accepted.
The validator now takes the first body start, preserving the full theorem span.
Gate session 37319 then exited 0, writing `check-v2/report.json`: eight exact
audits, three compiled semantic controls, fourteen record rejection controls,
and seven native source shape controls. Raw failures and successes remain present.

Dropping the initial guard falsifies the rollback and omitted-entry witnesses.
Dropping the final guard falsifies the omitted-entry witness. Storing shorthand ID
instead of source identity breaks the population invariant and rollback witness.
Every accepted negative has proof-body diagnostics with the exact reviewed kind
and inventory. Their compiler-generated `sorryAx` audit lines are failed-control
output, never accepted positive proof evidence.

The native source bridge covers four files: the cache/method and three caller
updates. All current snapshots match the root's candidate input hashes. The
changed numeric-property dependency file is unrelated and deliberately excluded.

The strongest result is conditional cache refinement for every finite admitted
candidate scan, not only the browser witness. Its premises are necessary: stable
identity meanings, compatible expansion environment, and externally supplied
cascade eligibility. No theorem determines native pointer identity, actual parser
expansion, logical aliasing, or environment compatibility. Those are explicit
review obligations, not proved facts smuggled in by a general refinement label.
