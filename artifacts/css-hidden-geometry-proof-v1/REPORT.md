# Hidden measurement-cache and geometry-query proof

**Verdict: scoped state-machine results established; complete native repair remains open.** The provisional miss-only `AddStateBits(NS_FRAME_IS_DIRTY)` patch recovers the modeled directly queried item. It does not establish descendant-query recovery, valid-hit pending placement, or complete native layout correctness. It must not be treated as proof of the later `MarkPrincipalChildrenDirty` proposal.

## Results

The final canonical and manifest-only relocated replay each check:

| Evidence | Result |
| --- | --- |
| Lean kernel results | 30; only standard `propext`, `Classical.choice`, `Quot.sound` allowed |
| Source bindings | 14 complete units plus one exact block early-return guard |
| Native/Lean comparison | 192 original and 192 repaired rows, each at O0 and O2 with UBSan: 768 matching rows |
| Old/repaired differences | 32 of the 192 paired input configurations |
| Semantic mutations | 6 distinct mutations, detected at both optimization levels: 12 executed mutants |
| False theorem claims | 4 rejected specifically because `decide` proves the propositions false |
| Integrity controls | 13 intended rejection gates, including a resealed source-role substitution and resealed added cache |

The 192-row input product varies hidden state, initial direct dirty state, absent/matching/mismatched cache, two computed sizes, zero/nonzero padding, two actual returned-size providers, and two forced keys. Each row observes after-measure geometry, dirty eligibility, measurement/reuse, first-query geometry/force count and repeated-query state. These are small facade inputs, not 192 browser tests.

The mutations respectively omit the new dirty mark; allow dirty cache reuse; omit the containing-block key field; omit actual size publication; force clean queries; and disable forced-hidden membership. Each mutant compiles and runs without UBSan failure in the bounded corpus; each differs from the expected projection. Concrete first differing rows and complete outputs are retained.

## What is proved

The model separates numeric key equality from geometry validity. A valid hit preserves the frame, including stale or zero geometry if that was already present. A clean hidden miss creates zero output, publishes it and retains clean state in the original projection. Its new cache entry can describe the skipped output rather than real layout.

The provisional mark makes that miss dirty. Under the explicit forced-layout caller/provider contract, a direct query publishes exactly the provider's actual returned size and completes clean. The provider is arbitrary; correctness is not obtained by assuming that it equals desired CSS dimensions. The separate `fixedBlock` example models a bounded fixed-size semantic family and is not a proof of the full native block algorithm.

`repeated_query_after_recovery` proves no additional forced work on a clean frame. It does **not** prove that geometry remains correct after an arbitrary `nextKey` or provider change. `clean_changed_key_retains_obsolete_geometry` demonstrates the required invalidation obligation.

The two-frame countermodel shows that a clean queried descendant does not trigger the gate merely because its measured parent is dirty. Another counterexample shows that the provisional mark does not immediately publish real geometry. A correct broader repair must account for skipped children and pending placement, not just misses in one cache.

## Source correspondence

Frozen source roles come from authenticated `css-hidden-geometry-source-review-v1` (FILES `0f6a76d5c58315ea7de6f04c4dd5204202643ee93bab6e47fdbcfa29b9eb5206`). HEAD source identity is the historical `99a9ca84f08370c1797720db8688bcb3747f6985`; original and provisional flex sources are distinct. Their exact bytes and the added same-revision constructor snapshots are pinned in SOURCE-PINS and BINDINGS. No live instrumented source was substituted.

| Native units | Model correspondence | Remaining boundary |
| --- | --- | --- |
| CachedBAxisMeasurement and MeasureBSizeForFlexItem | all captured key fields; clean-hit/miss and cache publication | handwritten outer cache wrapper, property lifetime, other cached metrics |
| ReflowOutput constructors and LogicalSize constructor | initial zero output | constructor text inspected/bound; native facade supplies the small equivalent initialization |
| nsBlockFrame::Reflow leading guard | hidden-parent skip leaves zero | remaining block algorithm is an explicit provider |
| FinishReflowChild and DidReflow | size publication, hidden dirty preservation and normal completion | NoMoveFrame path, stable frame, inert callbacks/special observers |
| Hidden predicates and four PresShell methods | hidden forcing membership, clean query rejection, force/clear control flow | single ordinary parent, supplied scheduling and document flush callback |

The methods are extracted from retained complete files by a lexical brace parser. Full-unit identities and source hashes are checked on every replay. Some units contain unexercised branches; complete text extraction is not evidence that every branch has been modeled or tested. Read SCOPE.md for every facade/provider restriction.

## Runtime relationship

The original 32→0 CB-key example and 192-row corpus are illustrative. After the root's real instrumented trace reported a clean item with unchanged computed size 1440×1920 appunits and CB block key 1073741823→0, an additional kernel witness records those values. The unconstrained sentinel is compared as a key value, not interpreted as a finite layout size. Other fields in that witness are an explicit ordinary-provider example, not a claim to have traced every ReflowInput field.

During preparation the root reported that the provisional patch repaired the direct browser cases but retained four nested clean-descendant failures. That is consistent with this model's separation; those changing external runtime artifacts are **not authenticated execution evidence of this capsule** and do not establish acceptance here. The full subtree proposal needs its own source binding, lifecycle analysis and runtime/proof evidence.

## Reproducibility and limitations

`verify.py` authenticates the outer artifact and fixed inner pin, independently checks the exact ordered 30-theorem audit roster, recounts native/model rows and mutant witnesses, and checks both replay summaries and guards. `capsule/replay.py` checks audit count and axiom allowlist; exact name reconstruction is additionally performed by the outer verifier. The inner runner is not advertised as hardened against FIFO/socket/device input: those were not tested controls. The outer verifier rejects nonregular filesystem entries. Never execute an untrusted resealed capsule without the externally authenticated pin.

Lean uses Int; no general signed32 arithmetic theorem is claimed. Native cacheableB subtraction, border sums, physical writing-mode conversion, native size providers and callback/lifetime effects remain obligations outside the bounded facade. An O0/O2 UBSan pass does not remove them. Compiler executable hashes and versions are pinned, but their installed libraries/SDK remain trusted dependencies.

Development evidence is retained: the initial Lean `min_eq_right`/`max_eq_right` names failed and were replaced with checked `omega` steps; an early runner expected the wrong wording for a falseclaim error, then was corrected to Lean's actual `decide ... is false` diagnostic. Earlier successful development replays precede the observed-key theorem/static-roster tightening and are not the final acceptance receipts. Final canonical and relocated receipts are authoritative. Disposable executables and olean files were removed after retaining commands, generated source and outputs.

No main native files, browser build, index or Git state were modified by this task.
