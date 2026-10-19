# Attr-taint shortcut component

## Result and scope

This is a conditional mathematical component for two metadata-aware shortcuts. It proves that checking payload equality and attr taint preserves the selected value and its modeled URL eligibility. It does not prove complete native cascade, substitution, map storage, or URL behavior.

Four modules expose 31 audited results: 14 Laws results, 3 Observation results, and 14 Witnesses results. Model defines the operations. The reference performs unconditional replacement; the optimized system separately models the earlier universal-declaration gate and later shared-map deduplication. The reference does not call either comparator. Arbitrary payload types, one-way sound comparators, initial optional values, unique/shared branch choices and finite admitted input histories are supported. Comparator reflexivity, symmetry and completeness are unnecessary.

The key proof derives taint equality from the predicate. It does not assume that skipping preserves taint. Either unchanged payload-only shortcut can mask correction of the other. Executable witnesses preserve both taint directions, the unique-branch masking case, absence versus present empty-like payload, and two explicit missing-premise counterexamples. These last counterexamples concern the model, not established production reachability.

## Native connection

SOURCE-PINS.json retains seven original complete files and two candidate files. SOURCE-BINDINGS.json binds 27 complete method slices. The checker verifies positions, bodies, hashes and signature starts; this is byte identity and manual source correspondence, not a verified Rust translation. It also checks the exact two source substitutions. The existing can_deduplicate_values helper already checks payload and taint; the map correction reuses it. The cascade correction adds wrapper attr_tainted versus incoming is_attr_tainted before CSS equality. No global PartialEq changes.

See SOURCE-MAPPING.md for the actual caller chain and SCOPE.md for the admission boundary. In particular, the earlier universal gate has no explicit reference-free guard. The model's EligibleDomain is an admission, not a newly discovered native invariant. The root's paired browser evidence is separate and is not replayed by this proof package.

## Validation

Run check.py as described in README.md. It kernel checks the four modules, validates the exact 31-name axiom roster, and compiles and executes four semantic mutants. All mutant definitions must compile successfully. Seven observations distinguish the baseline from each altered operation. The check retains every command, exit status and output. Compiler failures are not counted as semantic detection.

Source-only relocation, corruption and invocation guard receipts are retained in a separate replay package. The checker pins the Lean executable and 5092 toolchain library files. Allowed reported axioms are propext, Quot.sound and Classical.choice; no local axioms or proof placeholders are admitted. These are trust boundaries, not proof of the kernel/compiler/runtime itself.

## Remaining work

No claim closes all native declarations, state-dependent eligibility, active-reference substitution, taint range construction, URL-data equivalence, arbitrary registration changes, cache/attribute observer effects, or COW allocation and machine bounds. Prior count/iterator proofs are not imported here. A separate composition can instantiate their CompareSound contract with metadata_same_sound, after explicit source-version transfer. This capsule intentionally does not claim that composition.
