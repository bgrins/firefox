# Font consumer demand projection

The model proves an exact information-preservation result for arbitrary finite lists of modeled font consumers. `least_sufficient_projection` says a readiness level preserves every consumer's input tuple for all pairs of states **if and only if** it covers the joined demands of that list. The necessary direction uses independently varying size, font and orientation inputs; it is not an assumption that the chosen projection is sound.

The source-mapped distinction is concrete: em consumes computed size, whereas ex/ch/cap/ic query font metrics. The metric query receives the selected font and used size; ch/ic also use writing-mode orientation. The existing provider groups these units into FONT_UNITS and maps that flag to the FontSize semantic node. That node identity is retained in the model. It cannot recover the information needed to distinguish readiness contracts.

## Contracts and scope

`Demand` is the implication chain none < size < metrics < oriented. Metrics includes size readiness; oriented includes metrics. These are requirements, not new CSS cycle nodes. `FontState.size` represents computed size. The independent `font` token abstracts the complete remaining metric inputs, including used size and selected face/family/weight, rather than family alone. `vertical` abstracts the orientation distinction relevant to the query. Integers are abstract input identities, not pixel widths or font IDs from a browser.

`reads` returns an input tuple, not a CSS length. The metric contract deliberately includes computed-size readiness as well as the metric bundle. The leastness theorem is exact for this declared contract; it does not assert that every tuple field is a minimal dependency of every real glyph calculation. Equal tuples permit the same deterministic metric computation, but different tuples need not produce different actual glyph widths. The examples prove inadequate input readiness, not an observed numeric Firefox failure.

The single orientation Boolean is a finite witness abstraction, not an encoding of every writing mode. Native ch and ic use different orientation predicates; a real oriented-metrics readiness contract must preserve both relevant predicates or the complete writing-mode state. This theorem supplies no such encoding proof.

The unit list is supplied to the model. Selecting tokens, distinguishing a length from tokens in another grammar, choosing defaults/fallbacks and extracting requests are native correspondence obligations. This model does not settle the separate unused-fallback timing question. It excludes root-relative and line-height units, math/keyword font-size conversion, inherited versus current-style metrics and font loading. Those cannot be inferred from the five modeled units.

## Composition and later requests

- `ready_summary_iff` relates readiness for a joined list to equality of every input tuple.
- `alias_projection_composes` proves that flattening arbitrary named alias expansions and then projecting has exactly the same demand as joining each direct/alias request. The resolver is a supplied finite list per name. Multiple levels are covered by repeated application after expansion; termination or correctness of native alias resolution, including cycles, is not proved.
- `summary_append` and `accumulated_demand_exact` show that combining multiple consumer lists and processing any finite sequence of later batches retains the same total joined demand.
- `later_demands_preserved` proves the accumulated requirement covers both the old requirement and all new requests. `ready_after_escalation` shows that satisfying the upgraded requirement is equivalent to satisfying the old one and preserving every new read.

The actual/final input states are fixed throughout each readiness claim. A later input mutation requires revalidation or invalidation; a cached status cannot establish this on its own. No fulfilled-ready bit, pending computation, scheduling liveness or state-publication algorithm is modeled. In particular, recording a stronger request does not prove it has been fulfilled.

## Counterexamples and checks

The concrete witnesses hold size at20 while changing the metric token, and then hold size/metric token while changing orientation. They show that the common FontSize node and size readiness cannot guarantee a ch read, and that metric readiness without orientation is still insufficient. A named alias producing ch requires an upgrade from size to oriented readiness.

Five actual Lean files intentionally assert false claims: size suffices for a changed metric read; metrics suffice for a changed orientation read; an alias may drop ch demand; the last em consumer may overwrite an earlier ch demand; and readiness survives changing the final input state. All fail with `decide` proving the proposition false, rather than a missing import or syntax failure.

Pinned Lean4.35.0-rc4 run2 (59920/a27e9a/896dc3, exit0) compiled the source and audited17 statements, including algebraic lemmas. Axioms are only standard propext/Quot.sound or none; there are no new axioms, sorry or native-decide shortcuts. The first run failed because explicit Decidable instances were missing; its exact source/logs are retained. Both temporary directories were removed. This is a source/proof experiment with zero canonical coverage or native-fix increment.

## Minimal native integration boundary

The separate source prototype uses the same four-level implication chain alongside unchanged semantic references, preserves stronger flag demands, and joins a request before the old dependency traversal. This model can specify that transport contract: native extraction must yield the same consumer requests, aliases must not erase their joins, and a later stronger request must not be answered from a weaker fulfilled state. The proof does not verify that implementation, allow skipping generated dependencies, or justify treating the existing ensured bit as final readiness. Exact prototype bytes can be reviewed separately when stable; they are not a model import.

The existing publication/stability model handles different premises concerning writes and dependent consumption. This package adds the missing demand-projection distinction; it does not discharge that earlier model's native premises or implement a generic scheduler.
