# Independent iterator formal review

Verdict: accepted as a conditional finite-chain iterator and live-index component. This is not acceptance of count-constructor preservation, a Rust translation proof, or whole CSSOM behavior. The source pin is final combined native 9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d. The standalone label-only candidate retained in the capsule is historical context and is not approved for safe independent landing.

## Authentication and fresh evidence

All 28 manifest inputs and both externally pinned seals were authenticated before any capsule code ran. The relocated capsule contains only those files. Fresh Python -I -S replay compiled Iterator, Contracts, CursorHistory and Witnesses with the pinned Lean executable and library inventory. All 50 exact named axiom reports match: 38 general results and 12 finite witnesses. Actual axioms are limited to propext, Quot.sound and Classical.choice; the latter occurs only in some finite witnesses. No proof holes, custom axioms or native_decide appear in the audited modules.

Four extracted definition mutants compile successfully and execute the same independent five boolean observations. Baseline is all true. Omitting shadow skip and forgetting a visited node each produce false|false|false|false|true; ignoring tombstone ownership produces true|true|false|false|true; dropping the live filter produces true|true|true|false|true. These are semantic model distinctions, not native Rust mutations or malformed-output failures. Definitions/driver sources and empty successful compiler logs are retained.

Eight independent integrity negatives reject before output creation: extra file, extra empty directory, changed input, missing input, symlink, duplicate manifest key (self-consistently resealed), aliased ./ manifest path (self-consistently resealed, rejected by closed roster), and invocation without isolation. GUARDS.json retains exact causes. The path test does not claim to reach the later unsafe-name assertion; the earlier closed-roster rejection is sufficient and is recorded honestly.

## Proof substance

The native-shaped cursor retains the full current node, remaining suffix, ancestors and visited descendants. Every nonterminal step strictly decreases rank. Runs/step_drain derive complete traversal correspondence. The independent reference recursively concatenates each node with the parent reference after ownership filtering; it does not inspect cursor state or output. walk_reference is general in arbitrary suffix/current/visited state, and initialized_enumeration instantiates the actual start shape.

CursorHistory proves original-chain decomposition and a genuine remaining suffix along reached states. Next follows internal skips to one yield/end, terminates and exposes exact remaining output. It does not preserve a terminal heap cursor in the None branch; the scope correctly states that abstraction. Coherence initialization uses a nonempty chain; native empty maps still contain an Inner node and encode as a singleton empty node, so this is not a missing empty-map case.

Arbitrary key types have decidable equality; payloads are opaque. Per-node uniqueness implies globally unique surviving keys. Nearest lookup distinguishes absent owner from owned None, and tombstones mask ancestors. Exact emitted-owner/get results and filtered live indexing are substantive. Stored-length readiness is a separate hypothesis; bad-count witnesses demonstrate why iteration alone does not imply it. Raw getIndexRaw is explicitly historical and distinct from the final live getter.

## Source correspondence and remaining admissions

The checker reproduces 54 complete method bindings across original, iterator-only and final combined files; it checks the exact two-line loop-label change, unchanged combined iteration and exact formatted filtered getter. I read the complete retained source and all four Lean modules. Method hash equality is source identity evidence, not a semantic translation proof. The model's shadow any abstracts the native inner descendant loop; correctness requires provider traversal/equality and immutable finite parent links. IndexMap key uniqueness/order, Arc/borrowing, SmallVec allocation, Rust filter/nth, representable machine bounds and compiler semantics remain admitted.

The mutable outer-loop progression, parent advance, visited-node append and raw tombstone retention match the inspected native operations. Payload metadata is copied opaquely; no full native payload equality premise is introduced here. None corresponds to removed values in this map, not every possible CSS invalid-state representation.

The count component must establish stored live length. Its later joint bridge must identify its owner/lookup/validity definitions with this iterator's definitions rather than merely label RawEnumeration as supplied. Whole CSSOM also requires inherited/reset name-domain disjointness, registration lifetime coherence, FFI bounds and complete computed values. Those conditions are not inferred from per-map results or WPTs.

## Reproduction and cleanup

For a new fresh replay, invoke `python3 -I -S capsule/check.py --output ABSOLUTE_NEW_EXTERNAL_DIRECTORY`; the output must be outside capsule. The reviewer replay command and stdout are retained in replay.log and receipts. Own completed compiler outputs and tampered copies were removed after preserving sources/logs/results; CLEANUP.json records exact byte counts. No Firefox build, native code, WPT, browser or Git state was changed.
