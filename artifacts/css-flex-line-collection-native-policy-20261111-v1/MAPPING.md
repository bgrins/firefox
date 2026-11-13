# Exact source and invariant boundary

The design capsule retains old/current GenerateFlexLines snapshots and SOURCE-DELTA.patch. ORIGINS.json authenticates those immutable snapshots, the approved design and predecessor proof/root review. The proof checker does not reread a mutable live native file as its authority.

| Native operation | Rational policy | Checked obligation |
|---|---|---|
| Append generated ordinary item | `current ++ [x]` | Full α values retained |
| Skip wrap test for first appended item | appended.length>1 | append_gate/loop_start |
| Stored total predates appended item | explicit `total` argument | worker span premise derived at top-level and maintained by each recursive call |
| Add outer size, then gap | total+size x+gap | next_total equals prior span_snoc |
| Old newTotal and maximum guard | oldBreak | oldBreak_iff under T<L |
| Added existingTotal>T disjunct | patchedBreak | patchedBreak_iff; no alternative singleton-only executable predicate |
| Move last appended item on break | emit previous current; restart[x] | loop_step; singleton_ready; exact source reset size x |
| Continue same line | appended/current and nextTotal | prefixes_snoc plus ready_bounded; all prefixes fit, not just final total |
| Finish input | emit nonempty current | loop_nil and independent NextLine/Collected |

The worker proof assumes a current Ready line and an equal stored span only to state its induction invariant. Singleton initialization proves Ready; a continuation proves PrefixesFit for every nonempty prefix; a break initializes the new singleton. The exposed universal theorem has no Ready/stored-total input assumptions. The old policy’s total can fit while its first prefix fails; old_ready_fails explicitly demonstrates that distinction.

When T<L, the finite-bound guard entails newTotal>T in exact rational arithmetic. This does not prove that actual nscoord totals, component additions, sentinel values or limit acquisition satisfy the model. The source-shape interpretation is manually reviewable rather than mechanically extracted. No casts/overflow are modeled by rational arithmetic.

Cases include later individually large items, first failure without lookahead, exact and zero fits, nonzero gaps, gap reset, repeated identities, fractions, empty input and limit sensitivity. Six refusal controls rewrite via checked exact case results before rejecting a false target, so unrelated reduction failure is not counted as semantic evidence. None is called a compiled native mutant.
