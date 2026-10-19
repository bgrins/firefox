# Parser declaration history winners

## Result

For arbitrary finite incoming declaration streams, including repeated property identities, `PublicStorage.parseExtend` equals an independent whole-history winner specification:

1. For each identity, prefer its important occurrences if any exist anywhere in the history.
2. Keep the last preferred occurrence of that identity.
3. Retain those winners in their original source order.

An arbitrary valid initial unique block is treated as a source prefix. Payloads are arbitrary; no payload equality, reflexivity or comparison is required. This is a universal Lean result, not an inference from a finite corpus. No Firefox defect or production change is claimed.

## Specification and implementation boundary

The frozen `evidence/public-operations` audit and SPEC-TRACE.md bind the intended contract to [CSSOM specified order](https://drafts.csswg.org/cssom/#concept-declarations-specified-order) and [cascade importance](https://drafts.csswg.org/css-cascade-5/#importance). The audit consulted the primary drafts on 2026-10-19. Its retained trace is a paraphrase of the relevant obligations, not a complete specification snapshot. This package adds a mathematical characterization of the parsed declaration stream; it does not prove parsing, the cascade across origins/layers, computed-value validity, or serialization.

One actual native `extend` call applies one importance argument to its whole expansion. The theorem admits mixed priorities because it also describes flattened histories of multiple parser calls; it does not claim native extend accepts a per-entry priority argument.

The source snapshot's complete `push` rejects an incoming normal declaration when the existing declaration is important. Every other accepted replacement removes the old slot and appends the new one; new identities append. Its complete `extend` processes ordinary drained declarations followed by the all-shorthand iterator, accumulating return flags with non-short-circuit bitwise OR. SOURCE-BINDING.json retains both complete bodies and their source identities; the checker reconstructs and compares them. **No new native compilation or execution occurs in this package.** The source-to-model interpretation, actual iterator expansion, generated identity providers, valid mutable storage, machine widths, allocation and normal completion remain admissions.

The copied PublicStorage/AllOrder files match the committed checkpoint at `20708a78d00e6dd76889c52a11e203c757fa9d47`. DEPENDENCIES.json records exact blob and SHA-256 identities. PublicStorage was an actively reviewed mathematical checkpoint when copied, not an accepted complete native bridge. This package neither edits nor freezes the parent's directory and does not inherit unrelated removal/callback claims.

## Independent reference and theorem chain

`ParseWinners.preferred` inspects the **complete source history** to remove normal occurrences whose identity has any important occurrence. `lastOnly` then prunes every occurrence with a later occurrence of the same identity. These definitions do not invoke parseSet, pushScan or parseExtend.

* `winners_append` proves the global selection specification's append recurrence agrees with the priority-aware parser setter.
* `extend_winners` proves arbitrary extension of an already selected history; `empty_extend_winners` covers an empty initial block.
* **`arbitrary_initial_prefix`** proves `parseExtend initial actions = winners (initial ++ actions)` for every finite action list under only unique initial IDs. Incoming duplicates and mixed mapping kinds are allowed.
* `winner_per_identity` independently characterizes each result using `sourceWinner`: choose the last occurrence in the important-only source filter when an important occurrence exists, otherwise choose the last occurrence in the whole source. `last_for_occurrence` gives the exact prefix/selected-entry/suffix decomposition with no later matching identity.
* `winner_identities` proves all and only source identities survive; `winners_unique` proves exactly one result identity; `winners_sublist` proves stable source order.
* `tagged_winners_exact` connects an occurrence-index-tagged history back to the ordinary result. `winning_positions_source_order` proves the selected indices are a sublist of the original index range. This avoids conflating equal-valued repeated occurrences with their positions. Payload-map naturality is proved, not assumed.
* `raw_winner_refinement` composes the new characterization with the copied PublicStorage representation theorem: the model's separate declaration vector, importance vector and identity membership represent the declarative winners. This transfers the existing model contract; it is not a new native representation proof.

## Exact change-bit contract

`ParseFlags.pushFlag` follows the source's identity/priority scan. `push_flag_exact` proves, for a valid unique block, that push returns true exactly when the incoming declaration is important or the block contains no important declaration of that identity.

`pushResult` always computes the next declaration state and accumulates the bit. `accumulate_exact` and `returned_flag_and_state` prove the complete fold state and flag. For arbitrary duplicate input streams:

```
changed = actions.any(new =>
  new.important || !hasImportant(initial, new.id))
```

`exact_change_bit` proves that closed characterization. `full_winner_and_flag` gives the whole-history winner state and returned bit together. False means every push was rejected and the entire state was retained. True may accompany an identical final state, value, order or serialization; no stronger change claim is made.

The native source's `changed |= self.push(...)` and `changed | self.push(...)` are authenticated as non-short-circuit operations. A true accumulated bit does not authorize skipping later source entries. Failure/exception traces and allocation failure are outside the normal-completion model.

## Validation

The roster contains 136 individually audited theorem declarations: 81 copied predecessor results (55 AllOrder, 26 PublicStorage), **46 new universal lemmas**, and **9 new concrete kernel examples**. All modules compile from source in a fresh directory. Every theorem's axiom list is checked against the standard Lean foundations `propext`, `Quot.sound` and `Classical.choice`; no custom axiom, sorry, admit or native_decide is accepted.

Examples cover interleaved priorities and winner positions, an important winner followed by a rejected normal declaration, an arbitrary initial prefix, true with unchanged state, all-rejected false, and loss from stopping after the first true. An importance-irrelevant control deliberately gives the same result as plain last-occurrence selection; the reduced important-then-normal example distinguishes it. These are kernel examples, not compiled native mutations, browser tests or evidence of new bugs. The universal theorems carry the result independently of these examples.

The checker authenticates the complete closed file and directory roster before executing local source, rejects symlinks/nonregular entries, duplicate JSON keys, path escapes and unexpected files/directories, and requires a fresh output outside the capsule. Nine corruption controls include module/package shadowing and an altered replay entry point. Python isolated mode and a fresh output-only Lean path prevent accidental working-tree imports. The Lean executable is pinned; compiler and standard-library correctness remain trusted.

The retained fresh recorded replay passed all 136 audits; nine corruption controls passed. The initial late-helper compilation failure and correction are retained in receipts/INITIAL-REPLAY-FAILURE.json and receipts/CORRECTION.md. Canonical and manifest-only relocated full source replays, retained axiom/results comparisons, source-body checks and genuine corruption controls are required for final handoff. No Mach, browser, WPT, live native edits or Git mutation belongs to this artifact. Commit only the manifest roster plus MANIFEST.json and FREEZE.json, excluding generated object files and executables.
