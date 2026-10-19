# Checkpoint, not frozen or accepted

2026-10-19. Root redirected this slot to whole-CSS requirement-ledger research. No production files changed.

## Implemented and kernel-compiled

`lean/Iterator.lean`: generic K with DecidableEq and arbitrary V; Cursor stores full current node, remaining suffix, parents and visited descendant nodes. Actual skip/yield/parent Step, strictly decreasing rank, terminating source-shaped walk, complete Runs relation and equality to independent recursive nearest-owner reference.

`lean/Contracts.lean`: generic exact nearest-owner lookup, nested Option ownership (None tombstone vs no owner), flattened native get, per-node uniqueness implies globally unique enumerated keys, exact enumeration/get relation, tombstone stops ancestry. getIndex requires explicit stored length = reference enumeration length; insert/remove are not claimed to establish it.

Both compiled with pinned Lean 4.35.0-rc4, no errors/warnings. Development .olean files are outside source capsule at ../css-custom-properties-map-iterator-proof-development-v1. This is a development observation; axiom audit, source binding, mutation and relocated closure gates still pending.

## Next required work before sealing

1. Add explicit single-next yield/termination wrapper or explain full small-step Runs interpretation; optionally strengthen membership/nearest-owner statement from current lookup + uniqueness contracts.
2. Preserve original inner-continue counterexample and execute meaningful model mutants (skip removal, lost descendants, tombstone bypass). Do not mistake a literal decision witness for the universal theorem.
3. Full source binding/extraction records for Iter::next, Inner::iter/get and public get_index; retain full insertion/chain lifecycle as boundary. Check corrected source exact only label/continue change.
4. REPORT/SOURCE-ADMISSION with IndexMap unique/equality/iteration provider and finite borrowed chain/heap/compiler premises; generic keys/payloads avoid Nat encoding assumption. No live-count/CSSOM-invalid-value completeness claim.
5. Closed-roster authenticated isolated checker, exact theorem/axiom inventory, fresh relocated replay, tamper challenges and immutable receipts; then remove completed owned generated targets only after retention.

## Reproduce current Lean check

Use absolute lean path from TOOLCHAIN.json after hashing it. Compile Iterator to an external output directory; set LEAN_PATH to that directory and compile Contracts. Only imports are Std and Iterator. Reproduce script is retained in ../css-custom-properties-map-iterator-proof-development-v1/replay_checkpoint.py.

Source originals/candidate copied only after all 37 predecessor audit pins authenticated. PRIOR.json records manifest identity; source data generic proof does not establish C++/Rust compiler/heap refinement. Root owns WPT/build and independent pua review.
