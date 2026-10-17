# Native storage interpretation checkpoint

This checkpoint supplements the pinned [roadmap](ROADMAP.md). Milestones 1, 2,
3 and 5 retain their checked checkpoints; milestones 4 and 6 remain open.
The next target is native storage/recovery composition, followed by an actual
matching-to-rejection result for `section > span`.

## Reviewed storage trace adapter

The isolated package is
`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-lean`.
Its `check-v3` run and independent `reviews/check-v1` replay pass:

- Eight exact Lean theorem/axiom audits.
- Seven rejected mapping mutations, including a changed native exit hash
  vector, `current` versus `final`, declaration origin, binder scope and width.
- Rechecked source, model, proof and output inventories for the prerequisite
  481-obligation, 43-model native storage checkpoint.
- Separate invalid-input checks that remove stale acceptance output.

The generated predicates retain all four typed vector alias definitions, the
complete provider trace, and all six storage endpoint/count equalities.
`providerSymbols` explicitly interprets the new symbols; Lean checks the
insertion-trace and readiness correspondence by definitional equality.
`witness_ready` derives provider readiness from the native entry hash conditions
and the storage witness's zero initial count.

`storage_hash_history` obtains extracted insertion calls, a representation of
exactly the native exit hash vector, and conditional hash/filter high-water
history. It does not identify native vectors from equal observed hash lists.

Evidence fingerprints:

| Record | SHA-256 |
| --- | --- |
| `check-v3/report.json` | `647c1bf24c4c91eda911d63809ca8938d6ec5362da9e2b5f74e129982f4a46b8` |
| `reviews/check-v1/report.json` | `7806a111d9923d31a86cb07dc374301943ca965f96c6abcd39b6f1263361be24` |
| `reviews/ADAPTER-FINAL-REVIEW.json` | `d8eab67b979148265a112f62a853c07e1507f8cd62bb0b66434782a88ff6799b` |

Reproduce using a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-lean/check_adapter.py check-v4
```

## Reviewed storage observations

The second isolated package,
`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-observations`,
exports the native function's five numbered entry conditions and ten numbered
exit conditions. Its `check-v1` run and independent `reviews/check-v1` replay
pass eight theorem/axiom audits and six rejection controls. Independent clause
review checks their original Why3 groups, binders, typed variables and record
constructor metadata.

`stored_high_water` identifies the actual stored value with the maximum of the
entry high-water value and the final hash count. `appended_record` identifies
an ordered append of the element and its policy-event count, under explicit
record-constructor and sequence interpretations. `stored_history` combines the
hash trace with the stored high-water observation. Record append and hash
history are still separate conditional results at this checkpoint.

The controls reject a changed AST fingerprint, missing clause, unsupported
borrow projection, reversed comparison, wrong record count and wrong final
record-vector endpoint. The last control retains its historical `record-order`
label; it mutates the endpoint, not sequence order.

| Record | SHA-256 |
| --- | --- |
| `check-v1/report.json` | `85096259d39a57a48581a183e840f4f4ac0c7712c928cefc7420fb6df3d2a26c` |
| `reviews/check-v1/report.json` | `a7d3ad4aa49e198082bc7c3be7848154fe143953d200b1b04ff91ad4b810c0de` |
| `reviews/OBSERVATIONS-FINAL-REVIEW.json` | `346217a9546562b6e47b3894c1f2771b1f53e8ee55c6907453f00b2c8e0109e9` |
| `reviews/CLAUSE-PROVENANCE-REVIEW.json` | `bd2b6233db38be93a67d52c2ee0a5189643d0f84d2d11602109d1f558d63597e` |

Reproduce using a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-observations/check_observations.py check-v2
```

## Reviewed observed storage invariant

`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-invariant`
combines the observations. Its `check-v2` run and independent `reviews/check-v1`
replay pass two exact theorem/axiom audits and six rejected mutations.

`observed_push_valid` preserves high-water history, the ordered concatenation
of each record's policy hashes, and each recorded hash count. The observed
record chain gains the pushed element at its head. The result retains a
representation of the exact native exit hash vector and a related extracted
sink with auxiliary count reset to zero, permitting another push. This reset
is a witness construction, not a native continuation interpretation.

`valid_lookup` proves lookup succeeds for a policy hash of an element in that
record chain. The proof uses only standard logical axioms. Actual DOM ancestry
and stability of the fixed element-hash policy remain separate obligations.

The controls cover reversed record flattening, a changed count, chain order,
wrong vector endpoint, missing count reset and missing hash membership. The
flattening mutation breaks both push preservation and lookup; the checker
requires both expected failures. Invalid manifest controls remove stale
acceptance output.

| Record | SHA-256 |
| --- | --- |
| `check-v2/report.json` | `fdc1a2d370a51b363fa63afde0c1631627eddf20f0e7e0f9e380d35d5e1fd607` |
| `reviews/check-v1/report.json` | `a50776428f0907e568642d71032fd630d8f9542cb8912266b7ee852c867fa9f0` |
| `reviews/INVARIANT-FINAL-REVIEW.json` | `964e12ff05038dca5a796be1199ddc64d1c962ff4513667e2334c5c3f6a7a776` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-invariant/check_invariant.py check-v3
```

## Reviewed element-vector interpretation

The isolated `native-storage-element-step` package adds one source postcondition
retaining the actual element-vector primitive push transition. Runtime bodies
and trusted primitive specifications are unchanged. All 26 storage tasks pass;
the other 42 models match after checked source-location normalization.
Wrong-endpoint and wrong-count controls leave only the added postcondition
unproved. These timeouts are sensitivity checks, not counterexamples.

`native-storage-elements-lean/check-v1` and independent `reviews/check-v1` both
pass 19 exact audits and six mutation controls. Fifteen definitional equivalences
preserve the earlier numbered source clauses. The new theorem consumes native
element-vector validity, spare capacity and the transition postcondition to
obtain an extracted push and representation of the exact native exit vector.
Count encoding is checked under the explicit 64-bit width.

The element primitive refinement includes native constructor correspondence;
this remains an explicit assumption. The result does not identify vectors from
observed lists or install a new aggregate native proof certificate.

| Record | SHA-256 |
| --- | --- |
| `native-storage-element-step/EVIDENCE-v1.json` | `0789419352af80e664e704a6fee0319efd13e115a908ba639071f58ba989f9ec` |
| `native-storage-elements-lean/check-v1/report.json` | `c0e49f5f934e37624b147b0aceeebe0fc430ec3af3d7ef3a0de9f87d4fd5b67d` |
| `native-storage-elements-lean/reviews/check-v1/report.json` | `f831ecbce9d087e7773c110409dd76d58b5b39bab9ba52c76a22532f7352c15f` |
| `native-storage-elements-lean/reviews/ELEMENTS-FINAL-REVIEW.json` | `7ceca9050ec12d5422f845069e752f72c809e3e777a0c613536f471b3dd9d5c8` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-elements-lean/check_elements.py check-v2
```

## Reviewed concrete storage representation

`native-storage-representation/check-v1` and independent `reviews/check-v1`
pass 20 exact audits, including freshly compiled existing recovery modules,
and six rejected mutations. `valid_iff` and `chain_eq` connect the observation
relation to the existing `StorageInvariantProofs.Valid` and `chain` definitions.

`push_representation` combines both vector witnesses, propagates initial
record-list compatibility through the native and extracted append results,
and constructs a related extracted storage state. It preserves the exact native
exit hash and element-vector representations, recovery validity and chain order.
No vector identity follows merely from equal observed lists.

The controls reject wrong vector endpoints, stored high-water, chain order,
missing record compatibility and changed counts. The existing `SequenceModel`
also contains pop, clear and dereference contracts; their native semantics
remain assumptions. This is a representation theorem, not proof that an actual
extracted storage call produced the constructed state.

| Record | SHA-256 |
| --- | --- |
| `check-v1/report.json` | `18468ebd76cbcd66a3d5306c835d6fa15afa6eae94a832375f93091f6e5746bb` |
| `reviews/check-v1/report.json` | `474d0f1505b0e549467a371f853c14eff58c938a0f9f45442c408fa1e876f660` |
| `reviews/REPRESENTATION-FINAL-REVIEW.json` | `58e8fc2d262d0f35790f46c5863020648da4c1b5062915c346f0efed3c65ddca` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-representation/check_representation.py check-v2
```

## Reviewed provider normal return

`native-provider-normal-return/check-v1` and independent `reviews/check-v1`
pass eleven exact audits and five rejection controls. All 23 proof outputs are
byte-identical between the producer and independent replay. Invalid manifest
controls remove stale acceptance output.

`actual_return_view` derives the actual returned enumeration view and the full
provider backward-function equation directly from a successful call to the
extracted provider. Its continuation restores the initial count while preserving
the future filter and hashes. No enumeration-behavior premise is needed for
this equation.

`actual_calls` derives the existing `StoragePushProofs.ProviderCalls` from a
success-only contract for the actual opaque enumeration return. A separate
proof shows that preservation of just the returned state's filter and hashes
suffices for the extracted storage push history; the record uses the actual
returned count. Controls reject a changed reset source, returned view, hash
frame, recorded count and missing enumeration premise.

The success-only enumeration contract remains an assumption. It does not prove
completion and may hold vacuously when enumeration fails. The theorem establishes
the extracted provider's continuation, not a general native backward-function
translation.

| Record | SHA-256 |
| --- | --- |
| `check-v1/report.json` | `7cc2521655423255efeaf2554d6711e9d9ff0f50091dabac43bf55fa57277f87` |
| `reviews/check-v1/report.json` | `b198cdbf7da1eb5975931c7d7646b079f5dde4de9c0714377f9033c08b3ce722` |
| `reviews/RETURN-FINAL-REVIEW.json` | `1459a1016d6cfd41ca25daddc43f8360858822621501cb7300f94d124d4c897e` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-provider-normal-return/check_return.py check-v2
```

## Reviewed verifier level-selection correction

The isolated `artifacts/stylo-bloom-tools/projector-level-review` package corrects
one argument in Aeneas's `InterpBorrows.end_abs_borrows`. The symbolic-projector
visitor compares the requested nesting level with itself instead of comparing
the visited level with the requested level. Its neighboring borrow visitors
already use the visited level.

Independent source review and replay confirm the correction. The tests compile
the exact extracted visitor expression and its surrounding bindings against
the actual traversal classes. Direct and nested symbolic, abstract and concrete
borrow cases cover 54 outcomes: the baseline makes twelve wrong-level symbolic
selections, the candidate passes all cases, and a never-select control fails
six matching-level cases. These are synthetic typed AST traversal tests, not
complete valid interpreter-context executions.

Fresh extraction preserves both two-layer tuple/record Lean outputs exactly.
Both three-layer controls retain the original restoration cycle. The correction
does not provide the missing cross-region restoration rule, replace an accepted
tool, or establish an additional Firefox defect.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `38ed819f31af3cdf0ca61ae349f3e2f5db6988b5a84ef799f29091a301ca941c` |
| `unit-review-v1/report.json` | `72c0778c74af1c6affb965d7ed4ce19b67c6fbd7a8041595ea85819d9c0323cb` |
| `regressions-review-v1/report.json` | `b051a722ac3556244b8fe2a9e04a535c3d9e6508e05d5e30c9d6d70f528e8fce` |
| `reviews/FINAL-REVIEW.json` | `5b22d14e805cbc688624e0b8274d346c6c3ecf2a7dbfe0c4bfb3933554903b06` |

## Reviewed native pop observations

The isolated `native-storage-pop-observations` package preserves the production
`Storage::pop` body, including its debug checks. The producer and independent
replay each pass 106 debug and 63 release obligations. Both compilations retain
the 43 earlier models under checked source-location normalization and add one
pop model. Full compilation inventories authenticate all 44 models.

The result identifies the actual popped record, its element and the ordered
hash suffix removed. It retains the native record-vector pop relation, capacity
and stored high-water, and frames the filter and hashes on the empty path.
Entry premises include vector validity, recorded count/policy agreement and
the last record's policy suffix. Debug value agreement uses the explicit
expected-value contract.

Five source-contract mutations leave the intended obligations unresolved while
the other obligations pass after a focused retry. These timeouts are dependency
controls, not counterexamples. Four compilation controls reject changed or
missing models, an extra output and a changed compilation report. Independent
review found and closed a compilation-linkage gap in the first proof runner;
`prove_pop_v2.py` checks the full authenticated inventories before and after proof.

Filter removal has no semantic or safety guarantee in this checkpoint. Native
primitive safety, completion, the exact hash primitive history and repeated
recovery remain open. The one-step suffix premise alone does not preserve the
prerequisite for another pop.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `d944e5fbb04b4f0706c81df51a758ecde6a86a3e77af532b51be7d8c9e0cf8da` |
| `proof-v2/report.json` | `588e45aa85800fd52cb9f1dd83100743db06988c739582ef6a8fc31aecdd550e` |
| `reviews/proof-v2/report.json` | `5360e77f64bf075c694ff8b0375ab568daeef07ecd49134ff094c0b228edd2b2` |
| `reviews/FINAL-REVIEW.json` | `18f663f2c7b1fa7eb92fdba20feef51023af5581498e60cfb26b2ac7988211fe` |

The package README describes replay into a fresh output directory. The frozen
producer and review outputs are retained without overwriting.

## Reviewed native removal trace

`native-storage-pop-trace-checked` adds an exact transition witness to the pop
observations. Guarded production and independent replay each pass 278 new
obligations: 164 for debug pop, 98 for release pop, and eight across five checked
ghost helpers in each configuration. Both compilations preserve the 43 earlier
models and authenticate all 49 generated models and complete compiler outputs.

The witness contains the actual native filter/hash-vector pairs from entry to
exit. Each edge retains the typed hash-vector pop and filter-removal relation
for `policy[length - 1 - step]`. It preserves reverse order, duplicates and
zero-event cases. Ghost erasure restores the production runtime exactly.

Four source controls reject a wrong endpoint, forward event order, missing
filter-step guarantee and missing typed-pop guarantee. The order mutation
passes the main function obligations but fails the checked final helper;
helper coverage is essential. These rejections are timeouts, not counterexamples.
Six compilation controls reject changed or missing main/helper models, extra
output and changed reports. Independent review checks their exact mutations.

The native vector specifications and filter-removal relation remain explicit
primitive assumptions. This checkpoint does not establish native filter-counter
semantics, underflow safety, completion, repeated recovery or execution of the
separate extracted storage function. Its Lean interpretation is recorded below.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `9bc33aba960add45b3e9e595369903bea77ac2d7496f809579a4632587672a52` |
| `proof-v1/report.json` | `cc19bcb55cb4f7b5883bc219710471b2cbd53075436b740691037e925365dbdc` |
| `reviews/proof-v1/report.json` | `341f504d9d45070c6ff3ee6aa602205edc19da20ce6007ff27db8704f832253b` |
| `reviews/FINAL-REVIEW.json` | `34b3832910e7eec3d1b37e27ef8544630ff3de59380dfb5d228bac7609f4679f` |

The package README describes replay into a fresh output directory. Preserve the
frozen compiler/proof outputs and their input fingerprints.

## Reviewed complete pop contract interpretation

`native-storage-pop-lean/check-v5` and independent `reviews/check-v2` pass
14 exact theorem/axiom audits and six rejection controls. Both runs check
68 outputs, 7,651 file pins, 15,612 Lean library/binary tree entries and the
debug/release native compilation inventories. Immediate prerequisite evidence
links are checked; superseded historical tool environments are not replayed.

An isolated Coma export preserves all 424 typed task/context declarations,
153 original theory declarations and 19 roots, appending only two pre/post
definitions. The complete unspecialized contract retains both return branches
and intrinsic type invariants. Separate element, record and hash Option types
are preserved. Twelve shared caller/helper symbols are checked by source,
signature and datatype structure.

The Lean consequences retain the exact returned record, ordered hash suffix,
empty-pop frame, capacities, high-water observation, result invariant and
indexed removal witness. The witness yields a finite removal sequence with
exact native endpoints and backward policy indices. Zero policy length preserves
the filter/hash pair while still allowing a stored element record to be popped.
Controls reject changed endpoints, record identity, empty filter frame, suffix
policy, event order and missing filter transitions at the intended theorem.

The interpreted postcondition is an explicit premise. The native SMT result
does not assert that arbitrary symbol interpretations satisfy it. Native
primitive semantics, safety, completion and actual extracted storage-call
correspondence remain open.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `a511b11926a05c696a8eb3bd5bdbaa1fed3e4bf18f02d1d74040af6e6918633b` |
| `check-v5/report.json` | `66f5975fc2abdd7352b5823405ef1520edde1184507403b47f2678942dc2c3d6` |
| `reviews/check-v2/report.json` | `e92e8d42a8e0052ba20589b3c2ec150b413d3cbae45b839b1df3d530f5f55302` |
| `reviews/FINAL-REVIEW.json` | `2d4f6b98e25275284a392e7f0d69e7a41e2ec79902e5bb81af6ab696ccec1e4e` |

Use a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-lean/check_adapter.py --output /private/tmp/native-pop-replay
```

## Reviewed native pop policy history

`native-storage-pop-policy/check-v1` and independent `reviews/rebuild-v2`
pass ten exact theorem/axiom audits and four rejection controls. Each run
rebuilds all 22 local dependency modules, checks their resolved imports and
153 exact outputs, and pins 141,236 external library/tool lookup entries before
and after the run. External libraries are pinned rather than rebuilt.

The native backward-index trace is identified with the concrete reversed policy
list. Each removal step retains vector validity. Existing extracted pop/remove
proofs supply successful primitive calls, and explicit success-only refinements
identify their exact native vector and filter endpoints. Controls reject a
missing policy observation, changed vector/filter endpoints and forward event
order. The four inherited opaque SmallVec/Vec declarations remain in the
recorded axiom inventory.

The complete interpreted native postcondition remains a premise. This result
does not establish native primitive implementations, native completion or an
actual extracted `Storage.pop` call.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `9b4ba9f1239796d1943e9f76ce06c957900f27134df085be3ee362e7405d3ce1` |
| `check-v1/report.json` | `5a6060b63a656781582f4df365836852414ee87175e9d9193784b6ed27bd61e7` |
| `reviews/rebuild-v2/report.json` | `0a4c28bc7838ff5df04d46eb51366cf2be73a40b2306fa042eb617100c736654` |
| `reviews/EVIDENCE-REBUILD-v1.json` | `8cd2e74508458f30ab3a393af46adf7dfd8b84efc5db8776b30d01dc1ec9a7cd` |

Use a fresh output directory, then audit that directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-policy/reviews/rebuild.py --output /private/tmp/native-pop-policy-replay
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-policy/reviews/audit_rebuild.py /private/tmp/native-pop-policy-replay
```

## Reviewed native pop representation

`native-storage-pop-composition/check-v1` and independent `reviews/rebuild-v1`
pass thirteen exact theorem/axiom audits, two semantic controls and four typed
mapping controls. Each run rebuilds 39 local modules and checks 250 exact outputs
and 141,236 external lookup entries. Accepted source/report links include the
earlier element-observer interpretation. The independent auditor also rejects
changed, missing and extra proof objects in isolated fixtures.

The filter interpretation uses the earlier native counter projection and the
actual stored high-water value. Full element/count record projection connects
the removed native record to the represented element stack. Both return
branches preserve the observation invariant and ancestor chain, with exact
native vector representation relations. The element-vector results include
actual extracted primitive-pop equations. Typed symbol checks preserve native
origins/signatures, storage and record field order, sequence/borrow signatures
and the thirty explicit interpretation assignments.

The final extracted storage is an existential representation, not yet the
proved result of an actual extracted `Storage.pop` invocation. Complete native
pre/post interpretation, sequence meaning, primitive refinements and extracted
library models remain premises. The original resource-limited counter-observer
mutation remains an exploratory rejection; accepted semantic controls instead
change the stored high-water and final element-vector endpoint cleanly.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `ae9e6722a3c6db5cdac5d3a143ca0eb8fcb8304e6389496791e105def98107c2` |
| `check-v1/report.json` | `3cb92532b95916626a540fcfb3123d0be0375600fba67ea435639a8798a8e390` |
| `reviews/rebuild-v1/report.json` | `3f5766cfe288c5d78c2dc1b62f861817a49dbea79e2c007b52cc5eae8e4acc52` |
| `reviews/EVIDENCE-REBUILD-v1.json` | `43ce288e95ff526649da2daf06fdd87d58d5adc6652f082a8c5182544a6585eb` |

Use a fresh output directory, then audit that directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-composition/reviews/rebuild.py --output /private/tmp/native-pop-composition-replay
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-composition/reviews/audit_rebuild.py /private/tmp/native-pop-composition-replay
```

## Reviewed next-pop entry conditions

`native-storage-pop-entry/check-v1` and independent `reviews/rebuild-v1`
pass four exact theorem/axiom audits and four semantic controls. Each rebuilds
40 local modules and checks 261 outputs and 141,236 external lookup entries.
The independent auditor also rejects changed, missing and extra proof objects.

Indexed record reads and the full element/count projection recover every
recorded policy count from the observed invariant. Ordered append, injectivity
and finite-list representation for logical `HashSeq` values recover the exact
last-policy suffix. These laws concern logical sequences; they imply no
identity principle for opaque native vectors. The next-call theorem combines
preserved observation validity and native vector validity with an exact
next-current/prior-final state link and a fresh intrinsic borrow premise.

Controls reject changed counts, reversed append, the wrong last index and a
missing native-vector state link. The state-link control supplies observation
validity directly at the next state, isolating the two native vector-validity
transfers. Earlier resource-limited state mutations remain exploratory.
All four theorems use only standard Lean logical axioms.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `950204e43be52773fe1c33a84f1f7f8803c4307568c8cf33b05590a0c708dc7b` |
| `check-v1/report.json` | `4fbe5d192160c935aa4270ef64ab2df6f4e3646e67458ae35db09e5dcd895914` |
| `reviews/rebuild-v1/report.json` | `46210bb599e5a1133d46c16cd333517ce70c3cb2995151fd3ddc758704c0b4be` |
| `reviews/EVIDENCE-REBUILD-v1.json` | `f97d1fe64351a0c5913413085efff1aaace44c64167cef42081339640f96df30` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-entry/reviews/rebuild.py --output /private/tmp/native-pop-entry-replay
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-entry/reviews/audit_rebuild.py /private/tmp/native-pop-entry-replay
```

## Reviewed logical sequence codec

`native-storage-pop-entry/codec-check-v1` and independent review pass eleven
exact theorem/axiom audits and two controls. The guarded check uses the fresh
entry-proof dependency closure and checks twelve outputs.

The finite-list codec proves hash encoding/decoding, append, injectivity and
representation, plus indexed record length/read laws. These construct the
entry interfaces under explicit canonical observer equations. They do not
construct a simultaneous model of every native symbol and primitive.

| Record | SHA-256 |
| --- | --- |
| `CODEC-EVIDENCE-v1.json` | `8d4fb19ab0d2e13b926fb558323dea1cc778722954f2e58ee7d79f44256a2247` |
| `codec-check-v1/report.json` | `014bd489e501ee7c3ec7173b970d29304bb7f6bc45f4f6790580152da0fb7af5` |

## Reviewed actual extracted pop execution

`native-storage-pop-execution/check-v1` and independent `reviews/rebuild-v1`
pass six exact theorem/axiom audits and eight semantic controls. Both rebuild
44 local modules and check 297 exact outputs and 141,236 external lookup entries.
The independent auditor also rejects changed, missing and extra proof objects.

The actual extracted removal loop follows the native reverse-policy trace.
The nonempty storage call derives the popped element and count from the same
native record, then preserves the actual final storage representation, both
native vector relations, validity, ancestor chain and identity backward frame.
The empty branch proves the actual call equation and final representation.
Neither a complete loop equation nor a complete storage-call equation is a
premise.

Controls reject changed filter/vector endpoints, removal order, counts, popped
record and backward frame, and a missing expected-result contract. Extracted
library and Option models, successful primitive endpoint refinements, complete
native pre/post interpretation and the expected-provider completion/content
contract remain explicit premises. The recorded inherited opaque declarations
remain in the axiom inventory. This is conditional extracted-call correspondence;
native primitive implementations and native completion remain separate work.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `e93de52b0859d02d7ea38f85d2ab13d4f8b6f96453cacd10496852830351eee6` |
| `check-v1/report.json` | `edec9881d64fe71b5bbd0fec9c79edd1f7a9dccc2ccfea81f0cacff15b87a117` |
| `reviews/rebuild-v1/report.json` | `5fcfe105f0aa6220de30b6fb148bbe64a4853962f7af4140c0704af82c28fecd` |
| `reviews/EVIDENCE-REBUILD-v1.json` | `108a763dcabb3bfc14281b683333e3703924643d1125cfb5ed81cb5247498b00` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-execution/reviews/rebuild.py --output /private/tmp/native-pop-execution-replay
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-execution/reviews/audit_rebuild.py /private/tmp/native-pop-execution-replay
```

## Reviewed native U8 removal

`native-u8-remove-chain/proof-guarded-v1` and independent
`reviews/proof-guarded-v1` each pass 76 debug and 76 release obligations.
The source audit checks eight exact runtime functions, three constants and
both storage structs. Complete compilation inventories cover all twelve
generated models, including the concrete array update and its trait refinement.
Cached compiler dependencies and tool prerequisites are authenticated before
and after execution.

The contract describes two ordered updates of the actual array view. Saturated
255 remains unchanged; other counters decrement. The second nonzero premise
reads the state after the first update, which matters for coincident indices.
Four additional checked callers prove same-slot `2 -> 0`, `254 -> 252` and
`255 -> 255`, and distinct-slot `(1, 255) -> (0, 255)`, with the complete array
frame. These add 48 obligations while preserving all twelve baseline models
under source-path normalization.

Four source controls change the second safety premise, saturation threshold,
second update and second index. Their intended obligations remain unresolved
with Unknown/Timeout results; unrelated tasks pass. These are not SMT
counterexamples. Separate tests of exact method snippets demonstrate the
corresponding concrete failures, including underflow from coincident-slot
initial count one. Five compilation controls and three proof-output controls
reject changed, missing and extra evidence.

The contract-bearing trait is restricted to U8-compatible semantics; it does
not cover Bool storage or arbitrary overriding implementations. Standard array,
integer and borrow specifications remain assumptions. This checkpoint does
not discharge the live-history safety premises or connect the native pop
`remove_step` observer to the proved array transition.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `4e27803699601180f4e0d75b5ef55cd9ca16821e1f61af2de38117787338a4d7` |
| `proof-guarded-v1/report.json` | `5b7598d5c58653d407dc52898b222c6d5d8c216c40d6f4495cb307bcbc6c2c41` |
| `reviews/proof-guarded-v1/report.json` | `f7a6432b5175edff1e6e35a813004825e785280eb7078129f213a8b18fc1f3e1` |
| `reviews/FINAL-REVIEW.json` | `d089f37ff1340a7eda1bb85ac540ccc9d42b173793536f5becbda090e54cd3e3` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-chain/prove_guarded.py /private/tmp/native-u8-remove-replay
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-chain/reviews/audit_guarded.py /private/tmp/native-u8-remove-replay
```

## Reviewed native U8 filter clear

`native-u8-clear/proof-guarded-v1` and independent `check-v1` each pass eight
debug and eight release obligations. Source checks retain the production
default constructor and clear method signatures/bodies, both storage structs
and array constants. Clear is specialized to U8 storage; other implementations
and generic dispatch are excluded.

The concrete constructor creates 4096 zero counters, and clear replaces its
storage with that result. All three generated models are checked, including
default's trait refinement. No initial counter-value condition is required;
saturated counters are reset as well. The standard array and borrow models,
cached dependencies and compiler/prover remain trust boundaries.

Three source controls replace zero with one, omit the assignment or retain a
saturated slot. Each leaves only the intended zero postcondition unresolved
with a Timeout result. Separate complete-array runtime tests demonstrate the
mutant failures. Five compilation controls and three proof-output controls
check evidence integrity.

The result concerns filter clearing. It does not clear storage hash/element
vectors, establish their high-water value or supply the typed native counter
observer mapping needed by the storage interpretation.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `1715644608557e52f8e7c66794906d92d057c11e83cab2aa00272542b967bdba` |
| `check-v1/report.json` | `8fcaf38234bd875f3ff7793349f48e8a470f5b39503a677edb81a3b15c64bfd9` |
| `proof-guarded-v1/report.json` | `1a8865a7266d612ee1c8a5d7618bea0a2a255f3cafe654eff501af6284d0078c` |
| `EVIDENCE-PRODUCER-v1.json` | `236c10d31ac03432c873d9c29f239cb1181287ea5d86f6d42956e236a5a68f9e` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-clear/prove_guarded.py /private/tmp/native-u8-clear-replay
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-clear/reviews/audit_guarded.py /private/tmp/native-u8-clear-replay
```

## Reviewed raw counter encoding and removal safety

`native-u8-counter-lean/check-v2` and independent `reviews/rebuild-v1`
each rebuild 19 local modules and pass sixteen exact theorem/axiom audits
and five semantic controls. Each checks 138 outputs and 141,236 external
lookup entries. The independent auditor rejects changed, missing and extra
proof objects. All sixteen theorems use only standard Lean logical axioms.

The raw 4096-slot byte representation commutes with the actual extracted
ordered removal and zero reset. Represented live history and hash membership
supply both sequential nonzero premises, including two contributions when the
indices coincide. Saturated counters retain 255. Explicit native observer
endpoint equations connect these results to observed states.

Controls reject a changed saturation threshold, an initial-state second safety
premise, a changed reset value, missing membership and the wrong second slot.
The native observer equations remain premises. This history-conditioned result
does not discharge the existing success-only primitive-removal interface;
that interface also covers successful calls without a history premise.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `48361f8f00709745d7dec85d176f0724640a797a767faae5ed4125e2db8c2aa5` |
| `check-v2/report.json` | `19f4d878b7c2c1de999ddbaf144f66ef3dc4648e53eb93b6ae228c94e9fda3e7` |
| `reviews/rebuild-v1/report.json` | `69d0318eb83922048470b94d32ee6b00655fc78b1081ba513940d929e132902e` |
| `reviews/FINAL-REVIEW.json` | `839678ef082b3aa8579773d64f042d635b8c3ecdd22f12ea6ac580e83791bd9b` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-counter-lean/rebuild.py --output /private/tmp/native-counter-replay
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-counter-lean/audit_rebuild.py /private/tmp/native-counter-replay
```

## Reviewed native filter-clear interpretation

`native-u8-clear-lean/check-v1` and independent `reviews/rebuild-v1` each
rebuild 21 local modules and pass five exact theorem/axiom audits, four semantic
controls and six typed mapping controls. Each checks 190 exact outputs and
141,236 external lookup entries. Three independent output controls also pass.

Fresh export preserves the original 337 typed task declarations, both roots and
all 30 theory declarations, appending only two contract definitions. Typed
mapping preserves byte bounds, datatype fields, borrow endpoints, array view,
sequence indexing and the complete pre/post predicates. The final bounded zero
clause proves the raw counter endpoint and actual extracted filter-clear result.

Controls reject a changed endpoint, length, zero value or missing alternative
observer compatibility, plus six typed mapping changes. The complete interpreted
native postcondition remains an explicit premise. The chosen symbol assignments
do not automatically satisfy every native contract. No opaque native identity
principle is used; the separate canonical observer-update prototype is excluded.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `5863251f4814bd80defea6e99f373f5bee08f66d363fc6c9fcd8434458ed29d4` |
| `check-v1/report.json` | `d53f472ed29caee4f41b353117f21550f3f97e12172da4cde3eef90dd6309771` |
| `reviews/rebuild-v1/report.json` | `f0f67b798c86c9444fd30ca0e5b84aa7d3e8f6900c7008b4a68a02fac934f7d2` |
| `reviews/FINAL-REVIEW.json` | `cf9b1fd10a5f6a8fa06ec8964618c454dfb8fac1ed48c44e7ae5cc97e15fca15` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-clear-lean/rebuild.py --output /private/tmp/native-clear-interpretation
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-clear-lean/audit_rebuild.py /private/tmp/native-clear-interpretation
```

## Reviewed success-only removal refinement

`native-u8-counter-lean/success-check-v1` and independent
`reviews/success-gate/rebuild-v2` each rebuild 47 local modules and pass
22 exact theorem/axiom audits and eight semantic controls. Each checks 315
outputs and 141,236 external lookup entries. Three output controls also pass.

Six new declarations invert actual successful extracted array adjustment and
ordered removal calls. The second adjustment receives the first call's actual
returned storage. These results supply the existing history primitive-refinement
interface under an explicit native raw-counter endpoint mapping and independent
vector-pop refinement. No history or nonzero premise is added to that interface.

Five new declarations use only standard logical axioms. The constructor also
retains the existing SmallVec type/pop and array-size declarations. Controls
reject missing successful-call evidence, a changed native endpoint and the
wrong intermediate storage. The native endpoint equation remains to be connected to the checked
native removal contract. The earlier history proof separately establishes
successful removal for represented live hashes.

| Record | SHA-256 |
| --- | --- |
| `SUCCESS-EVIDENCE-v1.json` | `9127fe34d2e1d0cb4c6a47490c8603c3ae2b1273a4bf673666821b27ac058070` |
| `success-check-v1/report.json` | `bbe0f3f5edafd9212f4f1aef9d7e1e2ef50027b0ea2412ea1de0186b33a2935c` |
| `reviews/success-gate/rebuild-v2/report.json` | `aa98d3fdccb18299fc536bdb0e0ead3c4af0d2d928835754298f8464174fb11a` |
| `reviews/success-gate/EVIDENCE-REBUILD-v1.json` | `bffdd225777026dbd3dc55fef9fd5f3040666c0fd38778565b518db217f62612` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-counter-lean/reviews/success-gate/rebuild.py --output /private/tmp/native-removal-success
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-counter-lean/reviews/success-gate/audit_rebuild.py /private/tmp/native-removal-success
```

## Reviewed native U8 zero check

`native-u8-is-zeroed/proof-guarded-v1` and independent `check-v1` each pass
26 debug and 26 release obligations. Source checks preserve the exact local
production loop, array structure and constants, erasing one loop invariant and
two ghost assertions. Complete compilation/proof inventories and cached tool
prerequisites are checked. Five compilation and three output controls pass.

The loop returns true exactly when all 4096 counters are zero, under its library
models. A new explicit borrowed-array iterator contract relates the array view
to the iterator's slice view; the iterator implementation itself is not verified.
The inherited next/produces/completion specifications remain assumptions.

Two return-value mutations leave only their intended obligations unresolved.
The unchanged runtime passes fourteen examples; those mutants fail thirteen
and one respectively. Removing only the array-view contract retains a declared
extern specification and leaves three obligations unresolved, with the other
23 passing. These Timeout results are not solver counterexamples. The excluded
first prototype had a missing-contract warning and an impossible precondition;
it is not counted as verification evidence.

The result is conditional functional correctness of the exact loop in an
inherent specialization. Native trait dispatch, the debug wrapper, total
termination and complete storage clearing are outside this checkpoint.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `9da8f34e8b8a014bd6289422cde149f16400db4872c8e6aa2da7b74a534f6bea` |
| `check-v1/report.json` | `e8ea7f7f39368d130971de783aeaf07c35298d736fce0237293912100a936312` |
| `proof-guarded-v1/report.json` | `76064cefda61013493b5aa35708875a4f09f4cc7d6dd46198d9b05624bfa3d98` |
| `EVIDENCE-PRODUCER-v1.json` | `5fd3c206f8f6f336367fee5e79b7e2f31734e3ae6aaf684f953f40a4553854cd` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-is-zeroed/prove_guarded.py /private/tmp/native-zero-check
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-is-zeroed/reviews/audit_guarded.py /private/tmp/native-zero-check
```

## Reviewed concrete U8 removal caller

`native-u8-remove-specialized/proof-guarded-v1` and independent `check-v1`
each pass 88 debug and 88 release obligations across thirteen models per
configuration. The twelve preceding removal models remain unchanged. Source
checks preserve the accepted removal implementation and add a concrete caller
with explicit array length and sequential nonzero preconditions. No new trusted
external specification is introduced.

The caller's postcondition exposes both ordered counter-array updates through
its native filter storage. The second nonzero precondition reads the array after
the first update, including when both hash indices coincide. Two source controls
leave their intended obligations unresolved: a wrong second index and a missing
second nonzero precondition. Five compilation and three proof-output controls
also pass. Unknown/Timeout results are not solver counterexamples.

The producer's 7,315 pinned inputs and outputs were rechecked, and an independent
auditor validated the root replay's complete 52-file proof-output inventory.
This checkpoint supplies the concrete native contract for the next Lean adapter;
it does not establish that every earlier abstract removal edge satisfies that
contract. Native observer interpretation and that edge correspondence remain open.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `729c0390dbdf51e9e4011f19f390f74a7e71ffeae8043dee83e917cbdf9f5bf0` |
| `check-v1/report.json` | `dbb48f4da6b02dd260ccdbac62f99658d7be1c9676e2ff5ce1e14783b03294d8` |
| `proof-guarded-v1/report.json` | `70ea4cbd48954c673ce0a446497bfa2d1faa8d40232e6feafbd8dfd902e88349` |
| `EVIDENCE-PRODUCER-v1.json` | `f2706c3541359634f20833ac0fb79f91f86103ae503b339bad1ce1f316cf767d` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-specialized/prove_guarded.py /private/tmp/native-removal-caller
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-specialized/reviews/audit_guarded.py /private/tmp/native-removal-caller
```

## Reviewed native removal interpretation

`native-u8-remove-lean/check-v1` and independent
`reviews/remove-gate/rebuild-v1` each freshly compile 21 modules and pass nine
exact theorem/axiom audits, five semantic controls and ten typed mapping
controls. Three output controls pass. Each replay checks 210 outputs and
141,236 external lookup entries; all 8,155 producer evidence pins were rechecked.

Fresh export preserves all 1,355 task declarations, four roots, 49 original
theory declarations and 125 typed identities, adding only the complete native
pre/post definitions. The typed adapter retains native storage projections,
ordered updates and both sequential nonzero preconditions. Explicit constant
bindings and bounded sequence laws connect its final counters to the raw model
and to successful extracted removal, including coincident hash indices.

The nine declarations use only standard logical axioms. Complete interpreted
native pre/postconditions remain premises, as does compatibility when using an
alternative observer. Why3 narrowing correspondence is restricted to the actual
key-size value 12. The adapter is not a general Why3 importer.

Review caught and corrected a translator display-name/origin mismatch that could
swap current and final observations. Structural controls reject that mismatch
and nine other malformed mappings. Semantic controls reject changed endpoints,
a missing sequential precondition, reuse of the first index, changed sticky
counter behavior and missing observer compatibility. This was a tooling defect;
no additional Firefox bug is established.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `81163ae0dc71ace319fa3496538f988bc0561334c69b4d5fd993ef112ecd41a8` |
| `check-v1/report.json` | `242ff93ee80f2d848533476ade549572a9f6ca96693e23b0f2c8881333217efd` |
| `reviews/remove-gate/rebuild-v1/report.json` | `1cb52c86e57c43a7941efc15a795f8969d7e8911b20049257b5290b5de76ab83` |
| `reviews/remove-gate/EVIDENCE-REBUILD-v1.json` | `0441aa5756642e4bba6a5a9ed7714f0db7da321e61e8817ea55f0be76b7ff898` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-lean/reviews/remove-gate/rebuild.py --output /private/tmp/native-removal-interpretation
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-lean/reviews/remove-gate/audit_rebuild.py /private/tmp/native-removal-interpretation
```

The separate history-to-precondition, primitive-witness and storage-observer
prototypes are excluded from this checkpoint. Connecting every abstract removal
edge to the complete native contract remains open.

## Reviewed removal history and call adapters

`native-u8-remove-lean/followon-check-v2` and independent
`reviews/followon-gate/rebuild-v1` each rebuild 52 modules and pass 41 exact
theorem/axiom audits, eight new semantic controls and ten fresh typed mapping
controls. Two auxiliary observer-projection checks and three output controls
also pass. The root audit checks 391 outputs and 141,236 external lookup
entries; all 8,378 producer pins were rechecked.

History and hash membership now derive both sequential nonzero conditions in
the complete native removal precondition. Native intrinsic validity, array
length, constant bindings and bounded sequence laws remain explicit. Combining
that precondition with the complete native postcondition establishes the
successful extracted removal endpoint.

The primitive adapter preserves the earlier success-only refinement interface.
It requires a complete native call witness for every removal edge: current and
final endpoints, the same hash, and full pre/postconditions. This `Covered`
premise is not yet established for the actual native pop loop. A selected
storage observer interpretation uses the native array view and current filter;
its projection and endpoint equations are proved. Choosing those observations
does not establish simultaneous validity of all earlier native contracts.

The new semantic controls remove membership or change the updated state,
witness endpoints/hash/pre/post, current/final projection or byte index. All
fail at their intended proof obligations. The new proofs use standard logical
axioms, except the primitive constructor also retains the existing opaque
SmallVec/pop/array-size declarations. Earlier counter and success-only
controls are consumed as pinned prerequisite evidence.

| Record | SHA-256 |
| --- | --- |
| `FOLLOWON-EVIDENCE-v1.json` | `693f98b35555129c904bd5eda3a68e0bfbeddeb1e886357771e5d414be5ec792` |
| `followon-check-v2/report.json` | `83aafbc4c00193e7054e0cdfdf49c5f0ba3297123c193080456e900f1f2fc1f2` |
| `followon-check-v2-audit.json` | `07ec73f104a1534e42a70216b3fb2a20a55759924601e959c20402748f0f52d8` |
| `reviews/followon-gate/EVIDENCE-REBUILD-v1.json` | `5175be7447ea977e7b0ee20e10f0c2c648c4dfc5df6649b1cfbd7cc94de21e32` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-lean/reviews/followon-gate/rebuild.py --output /private/tmp/native-removal-adapters
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-u8-remove-lean/reviews/followon-gate/audit_rebuild.py /private/tmp/native-removal-adapters
```

## Reviewed native optimized filter clear

`native-clear-filter/check-v1` and independent `proof-guarded-v2` each
pass 160 debug and 160 release obligations across twenty models per
configuration. All thirteen preceding removal models are preserved. Source
checks retain the production clear helper after enumerated ghost erasure,
plus the checked U8 removal, default constructor and whole-array reset.

For a high-water value above 25, the helper resets every counter directly.
Otherwise, exact live counts and hash length bounded by high-water imply every
counter is at most 50. The loop proves both ordered decrements safe, including
coincident indices, and preserves exact counts for the remaining suffix. Its
final array is zero. No new trusted external contract is introduced; slice
iteration and array/sequence models remain assumptions. Deriving the native
count premise from storage history remains open.

Three source controls omit removal, branch on current length instead of
high-water, or omit exact counts. Each leaves its intended obligation
unresolved; these Timeout results are not counterexamples. Seven runtime
examples pass, and both runtime mutations produce mismatches. Five compilation
and three output controls pass. The producer's 7,879 pins and the root replay's
complete eighty-file proof inventory were independently checked.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `0c1db2799d726d9a6abb39f91f53e03ff10504ae4b8d7af336ba2bdb2debc7b2` |
| `check-v1/report.json` | `2ce6ab2e17b3dbe4c5cc4cddf786d299a7f7169546326e052d14fcc85a78361d` |
| `EVIDENCE-REBUILD-v1.json` | `6c4f2045935236eea3656d125644c4135f41c1e4a3c182cd97afb0f40e4a8994` |
| `reviews/INDEPENDENT-REVIEW-v1.json` | `c3f2523fab3ec4ae71adf0a27a8752be2798dbe8a4d2cbf6c7cd788de10c0ca3` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-clear-filter/prove_guarded.py /private/tmp/native-optimized-clear
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-clear-filter/reviews/audit_guarded.py /private/tmp/native-optimized-clear
```

## Reviewed native storage clear

`native-storage-clear/check-v1` and independent `proof-guarded-v1` each
pass 215 debug and 209 release obligations across 23 models per configuration.
All twenty optimized-clear models are preserved. Source checks retain the exact
production `Storage.clear` body and field layouts, together with the checked
clear helper and native zero-check loop.

Under the conditional count/high-water premise, clearing leaves both buffers
empty, high-water zero and every filter counter zero. Buffer validity and
capacities are preserved. New explicit SmallVec clear and dereference contracts
supply their library semantics; the borrowed-array iteration contract is
inherited from the zero-check checkpoint. Abstract element carriers, allocation
behavior and native history correspondence remain outside this result.

The release zero-query wrapper always panics in production. Its verification
model therefore has a false precondition, is retained in the inventory and
contributes no substantive coverage. The ordinary release clear precondition
is satisfiable, and the proof establishes that this query branch is unreachable.
A control forcing the query leaves its false call obligation unresolved.
Three other controls omit clearing elements, hashes or high-water and leave
only the intended postconditions unresolved. Unknown/Timeout results are not
counterexamples. Five compilation and three output controls pass; all 7,969
producer pins and the root replay's 92 proof outputs were independently checked.

| Record | SHA-256 |
| --- | --- |
| `EVIDENCE-v1.json` | `0f75f5865790a5791e62e5520ce97ee5638371f8064368767aa6d3ede187bb95` |
| `check-v1/report.json` | `fff0894659f5dc2e29380a9930b4ceaa8272c3e0c600b00ad8930be38111aaaa` |
| `EVIDENCE-REBUILD-v1.json` | `0606ae92b4a938f4165c7437c7006258ac6e60ad4f4cf108e50506987e5ad051` |
| `reviews/INDEPENDENT-REVIEW-v1.json` | `a45a8910b4340f2796dad3f65baa5f298be5123fca6fe89a8c5a7a8fc74c9962` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-clear/prove_guarded.py /private/tmp/native-storage-clear
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-clear/reviews/audit_guarded.py /private/tmp/native-storage-clear
```

## Reviewed native removal readiness

`native-storage-pop-concrete/readiness-check-v1` freshly rebuilds 27 Lean
modules and passes nine exact theorem/axiom audits. Independent source and
output review checks all 226 outputs, 8,084 prerequisite pins and 141,236
external lookup entries. Nine semantic, eight typed-schema and four output
controls pass. This checkpoint has one fresh rebuild and an independent audit;
it does not claim a second independent rebuild.

Live high-water history implies that removing a represented suffix in reverse
order satisfies both nonzero conditions at every step. The second condition
reads the counters after the first decrement, including coincident indices.
The proof connects raw counters, native byte sequences and an integer-indexed
prefix recurrence.

Typed export reads the native `removal_ready` definition without instrumentation,
preserving 300 task declarations, eighteen theory declarations and 45 identities.
The final source refresh changes only four source-file paths in the selected
typed export. The translator preserves the guarded equation, and Lean proves
that equation under the selected interpretation. All nine results use only
standard logical axioms. Constant bindings, bounded sequence laws and the
represented history remain explicit.

Controls change an index, the intermediate counters, the recursive state or
count, or a count bound. The generated semantic mutants still compile, but
their interpretation proofs fail at the intended obligations. Structural
controls reject malformed symbol identities, types, binders and ranges.

This proves the readiness predicate under a selected symbol interpretation.
Shared interpretation of all native contracts and the full pop precondition
remain open. It does not establish native completion or readiness from an
unconnected native provider trace. No additional Firefox defect is established.

| Record | SHA-256 |
| --- | --- |
| `READINESS-EVIDENCE-v2.json` | `6b1d45ecb813a2e9acbb6c31807b389ea57c3ba28fb4f6a885e48c061820010e` |
| `readiness-check-v1/report.json` | `1817fcf1a22e75a328f6ed558543d5c1ef6a6731034a24bf9ccd71eba883d6cc` |
| `reviews/solver-probe/readiness-review-v6/report.json` | `a69d3c9b78aee9e07e5b6c3dee6c762bb667e646ce928f3159f50f61fc89a480` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/readiness-gate-v1/rebuild.py --output /private/tmp/native-removal-readiness
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/solver-probe/readiness-review-v6/audit.py --output /private/tmp/native-removal-readiness --report /private/tmp/native-removal-readiness-audit.json
```

## Reviewed concrete native provider and pop

`native-storage-pop-concrete/native-check-v1` independently replays the
guarded native candidate's complete 69-model inventory in each configuration.
Debug passes 774 obligations and release passes 700. The three provider models
are byte-identical across configurations, so their 289 induction obligations
are explicitly shared: each replay checks 1,185 distinct solver obligations.
Six inherited atom adapter models have no goals and supply trusted contracts.
They contribute no substantive proof coverage.

The producer performs fresh guarded debug and release compilations. Both proof
replays consume those authenticated compilations. The independent replay checks
8,715 inputs and 1,911 outputs; all 17,255 producer evidence pins were rechecked.
The complete enumeration, insertion and expected-vector induction strategies
retain every original root and both proof and use branches of each cut.

Source checks preserve nine native runtime functions, constants and layouts,
plus the inherited provider, push and pop runtime after enumerated ghost
erasure. The native U8 array supplies the actual counter observation and both
ordered updates. The fixture exposes the outer storage field for contract
projection; the counter array stays private. No new trusted Bloom contract is
introduced. DOM/atom and sealed SmallVec contracts remain assumptions.

Pop now has an explicit recursive readiness requirement. A proved helper
exposes each next decrement's nonzero conditions and the remaining readiness.
The array-length guarantee requires the native intrinsic invariant, rather
than claiming that malformed logical arrays have length 4096. This correction
addresses a proof-interface defect, not a Firefox bug.

Four source controls remove readiness, read the second counter too early,
skip removal or assert unconditional array length. Each leaves only the intended
obligations unresolved. These Timeouts establish rejection, not counterexamples.
Five compilation-provenance and three output controls also pass.

This checks the concrete native slice under its strengthened preconditions.
Actual caller history establishing those preconditions, a shared interpretation
of the native contracts, complete recovery and matcher composition remain open.

| Record | SHA-256 |
| --- | --- |
| `NATIVE-EVIDENCE-v1.json` | `ed3e39201547f5f0bd30fd0517f361cdf14b99e6899e2edf9bdc8c96a1e31f49` |
| `native-check-v1/report.json` | `271c716386efcfb55c535df3c24bf6d37b9f288877c76458400dadc9b2502e7c` |
| `native-check-v1-audit.json` | `b898842b7a82da2bdac1bdb56e0e58616d6043274643baf3c657eebc993d5ac4` |
| `reviews/solver-probe/gate-v1/EVIDENCE-v1.json` | `34ff9be7b4fa991467a6964efeb9f23b572b910916a3a7b211f055115f78606b` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/solver-probe/gate-v1/rebuild_v4.py /private/tmp/native-provider-pop
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/solver-probe/gate-v1/audit_v4.py /private/tmp/native-provider-pop --report /private/tmp/native-provider-pop-audit.json
```

## Reviewed concrete removal-step interpretation

`native-storage-pop-concrete/readiness-step-check-v2` freshly rebuilds 38
Lean modules and passes sixteen theorem/axiom audits. Independent review checks
all 332 outputs, 8,189 input pins and 141,236 external lookup entries. All 10,277
review evidence pins were rechecked. Sixteen structural, thirteen semantic,
two canonical-root and five output/reference/report controls pass.

The exact native removal relation observes a 4096-counter input and performs
two ordered decrements. Successful checked extracted removal supplies both
nonzero conditions, including the intermediate read when the indices coincide.
Under the existing constant and sequence laws, the interpreted native relation
therefore returns the same observed filter as that extracted operation.

This constructs the existing success-only primitive refinement without an
additional complete-call witness premise. Fifteen audited results use only
standard logical axioms. The constructor also retains the three extracted
SmallVec declarations `Bloom.smallvec.SmallVec`, `Bloom.smallvec.SmallVec.pop`
and `Bloom.ArrayT64.Insts.SmallvecArray.size`. Its vector-pop refinement remains
an explicit premise. Native release success alone does not supply the checked
extraction's non-underflow condition.

Review caught a canonical export selecting a helper goal instead of `vc_pop_E`.
The corrected export retains the actual pop task's 486 declarations and 462
identities; its selected removal-step typed AST is byte-identical. Unspecialized
pop contract instrumentation preserves that task and extends only the theory.
Two controls reject the wrong canonical goal. This was an evidence selection
error, not a Firefox defect; the earlier readiness export was unaffected.

The result validates selected symbols and the primitive interface. The complete
native pop contract, caller history, provider correspondence and native
completion still require composition. One fresh combined Lean rebuild and an
independent source/output audit support this checkpoint.

| Record | SHA-256 |
| --- | --- |
| `STEP-READINESS-EVIDENCE-v1.json` | `8d5208620e2bc0c25c01e7e1ffd8b842a0c89f01160d5b1979c03f63a9ddd3dc` |
| `readiness-step-check-v2/report.json` | `893ba3790ad572083a0336ed9cbbe8211376fea48bcc8c7cdc71f01f5f4f6cd0` |
| `reviews/solver-probe/step-review-v2/REVIEW-EVIDENCE-v1.json` | `287d4eddc0d5513c07588810804bf48ace902a9e938ea389e7aecb08f8192888` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/readiness-step-gate-v2/rebuild.py --output /private/tmp/native-removal-step
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/solver-probe/step-review-v2/audit.py --output /private/tmp/native-removal-step --report /private/tmp/native-removal-step-audit.json
```

## Reviewed full native pop contract bridge

The complete typed native pop precondition, postcondition and helper trace now
have a selected Lean interpretation. The trace and postcondition are
definitionally equal to the earlier contract under the shared symbol record.
The precondition is exactly the earlier five conjuncts plus removal readiness.
An explicit equation preserves readiness's nonempty guard, last-record policy
and complete event count.

The shared interpretation uses native counter observations, ordered native
removal steps and the checked readiness recurrence over represented hash lists.
Given the earlier precondition, conditional live suffix history, counter length
4096, constant bindings and sequence laws, Lean proves the complete new
precondition. The earlier five conjuncts remain premises. This does not derive
actual native history or establish a joint interpretation of every native
contract.

The translator checks exact metadata, closed types, polymorphic applications,
binders, patterns, triggers and definition result types. It validates the shared
vector-validity alias and couples the removal and readiness declarations to the
accepted exports by origin, signature and source location. Thirteen new
structural controls reject malformed translations. Six generated semantic
mutants compile, then fail only the intended interpretation proofs: omitted
invariants, final trace or vector pops, a wrong reverse index, zero readiness
count and omitted readiness.

The fresh `pop-adapter-check-v1` rebuild passes 41 modules and 21 theorem/axiom
audits, retaining the earlier controls. Twenty audited results use only standard
logical axioms; the primitive constructor retains the three SmallVec
declarations recorded in the preceding checkpoint. Independent review checks
433 outputs, 8,205 input pins and 141,236 lookup entries. The combined inventory
contains 29 structural, nineteen semantic and two canonical-root controls.
Five physical output/reference/report controls reject the intended changes;
all 2,855 direct review evidence pins were rechecked. One fresh dependency
rebuild and an independent source/output audit support this checkpoint.

| Record | SHA-256 |
| --- | --- |
| `POP-ADAPTER-EVIDENCE-v1.json` | `adc3a12d4ed7a9d3e41320453fd700c4d592fc46f1d61ef90e4cb856b6731726` |
| `pop-adapter-check-v1/report.json` | `7aa4982069d50fd9f21a18c83203642be249d96f46a1e9e144d8c46a4c9278be` |
| `reviews/pop-adapter-review-v1/REVIEW-EVIDENCE-v1.json` | `d5313fbd126e1f3b1157451b432c250d726fb755a800cf7147c73b567308ecff` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/pop-adapter-gate-v1/rebuild.py --output /private/tmp/native-pop-contract
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/pop-adapter-review-v1/audit.py --output /private/tmp/native-pop-contract --report /private/tmp/native-pop-contract-audit.json
```

## Reviewed stored history and successive pop calls

The selected native pop interpretation now derives its complete precondition
from ordered record accounting and the current stored hash history. Record
counts agree with each record's policy, and flattening those policies gives the
stored hash list. The representation's length and indexed-read laws establish
the earlier count and suffix conditions; the full history establishes removal
readiness. Borrow intrinsic validity, both vector validities, native counter
length and the constant/sequence laws remain explicit entry premises.

For both returned-element and empty results, the interpreted postcondition
preserves record accounting, counter history, the stored high-water mark and
counter length. Each native removal step is connected to successful checked
extracted removal using live membership. These new history proofs do not depend
on the extracted SmallVec operations or require a vector-pop refinement premise.
They still assume the complete selected native postcondition.

The next-call theorem derives vector validity, counter length and live history
from that postcondition. It establishes the next pop precondition given equality
between the preceding final state and the next current state, plus the next
borrow's intrinsic validity. It does not prove native completion or discharge
that borrow premise.

The fresh `pop-live-check-v1` rebuild passes 44 modules and 36 theorem/axiom
audits. All fifteen new audits use only standard logical axioms; the combined
inventory retains the earlier primitive constructor's three SmallVec
declarations. Eleven new semantic controls reject wrong append order, history,
counter length, record counts, record order/indexing, removal order and the
next-call endpoint. The combined inventory is 29 structural and thirty semantic
controls, plus two canonical-root controls. Independent review checks all 487
outputs, 8,221 input pins and 141,236 lookup entries. Five physical
output/reference/report controls reject the intended changes; all 2,459 review
evidence pins were rechecked. One fresh dependency rebuild and independent
source/output review support this checkpoint.

| Record | SHA-256 |
| --- | --- |
| `POP-LIVE-EVIDENCE-v1.json` | `e2ced20cd127e1f4f718c3ab3d02528b4f82a86b9a2adb6f49068b3729000125` |
| `pop-live-check-v1/report.json` | `9eb3901cf49ecacf33b3c1d12ba993112fe2677cf7688fafb800f3d1774b4c9c` |
| `reviews/pop-live-review-v1/REVIEW-EVIDENCE-v1.json` | `c3147522d22ea0498e636eb257053e003a90c919b45447014ce9894fde44be4c` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/pop-live-gate-v1/rebuild.py --output /private/tmp/native-pop-live
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/pop-live-review-v1/audit.py --output /private/tmp/native-pop-live --report /private/tmp/native-pop-live-audit.json
```

## Reviewed native clear precondition

The native clear routine's complete typed precondition now has a selected Lean
interpretation. Eight definitions and both contracts for recursive counts agree
with native hash indices, ordered hash lists and bounded byte observations.
Exact counts include the counter length of 4096. The exported precondition
retains the borrow intrinsic and the choice between a high-water mark above 25
and the bounded-history exact-count path.

Stored history derives that count domain. After either pop result, the full
selected pop postcondition and initial history establish the clear precondition
when the clear filter, hash slice and high-water argument observe the pop's
final state. The clear borrow's intrinsic validity remains explicit. This
derives the count premise; native completion, the clear postcondition under
these observers, and provider/recovery composition remain open.

The fresh `clear-count-check-v1` rebuild passes 47 modules and 56 theorem/axiom
audits. All twenty new audits use only standard logical axioms; the combined
inventory retains the earlier primitive constructor's three SmallVec
declarations. Twelve new structural controls check the translation. Eighteen
new semantic controls reject incorrect count recurrence, saturation bounds,
thresholds, counter size, omitted intrinsic validity and mismatched pop/clear
endpoints. Generated semantic mutants compile before their interpretation
proofs fail. The original native clear task retains all 1,387 declarations and
2,359 identities after unspecialized contract instrumentation.

Independent review checks all 638 outputs, 8,293 input pins and 141,236 lookup
entries. The combined inventory contains 41 structural, 48 semantic and four
canonical-root controls. Five physical output/reference/report controls reject
the intended changes; all 3,214 review evidence pins were rechecked. One fresh
dependency rebuild and independent source/output review support this checkpoint.

| Record | SHA-256 |
| --- | --- |
| `CLEAR-COUNT-EVIDENCE-v1.json` | `76103fefb3c156939161251ea6b6bd8fbe81fc0ab36ef49431549bad45c6d1d6` |
| `clear-count-check-v1/report.json` | `2e631bf61c2514cfc221dd3c7630512eeff6b7f4c17001d8349768b32e527e1a` |
| `reviews/clear-count-review-v1/REVIEW-EVIDENCE-v1.json` | `80cde3083ff72fbc6993436a9f9db35dd139d5b348f834764f6eed1b38952a0a` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/clear-count-gate-v1/rebuild.py --output /private/tmp/native-clear-count
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/clear-count-review-v1/audit.py --output /private/tmp/native-clear-count --report /private/tmp/native-clear-count-audit.json
```

## Reviewed native push history composition

The complete typed `push_internal` postcondition now preserves the same stored
history and ordered record accounting used by pop and clear. Native insertion
is connected to checked extracted insertion, including saturation and sequential
updates when the indices coincide. Its ordered fold preserves counter length
4096 and records the maximum of the previous high-water mark and final hash
count. The postcondition's hash append, record append/count and high-water
equation establish the final live invariant.

The selected interpretation satisfies the exported insertion and recursive-fold
contracts. Counter length is derived from an explicit initial size; the counter
observer's intrinsic-to-length condition remains explicit. Record constructor
and projection laws, sequence append/snoc laws and the complete native post are
also premises. No additional opaque SmallVec declarations enter these proofs.

The final invariant establishes the next pop precondition given its current-state
endpoint and borrow intrinsic. It also establishes the next clear precondition
given its filter, hash-slice and high-water endpoints and borrow intrinsic.
These implications do not establish native completion or the actual provider's
execution and policy correspondence.

The translator checks 24 shared native signatures, eleven identical source
locations, five datatype layouts and the three native counter primitives.
Datatype layout checks justify the differently named generated SendElement
projection. Thirteen intrinsic predicates and two rewrite axioms have identical
source definitions, with only generated axiom labels normalized; three opaque
intrinsic leaves remain explicit. The maximum-count constant has the same exact
definition. Unspecialized contract instrumentation preserves the native push
task's 508 declarations and 974 identities.

The fresh `push-live-check-v1` rebuild passes 50 modules and 76 theorem/axiom
audits. All twenty new audits use only standard logical axioms. The combined
inventory contains 54 structural, 64 semantic, six canonical-root and six
binding controls. Generated semantic mutants compile before failing the intended
proofs. Independent review checks all 772 outputs, 8,349 input pins and 141,236
lookup entries. Five physical output/reference/report controls reject the
intended changes; all 3,885 review evidence pins were rechecked. One fresh
dependency rebuild and independent source/output review support this checkpoint.

| Record | SHA-256 |
| --- | --- |
| `PUSH-LIVE-EVIDENCE-v1.json` | `b450c14bd1b2e1dd419d386a3c5188baafde47e45cd60a10c06e929faed1094e` |
| `push-live-check-v1/report.json` | `b74e5002db837f83ea4bc6270f5bc21cd6a34afbbbf0f56c357709eeafcb7b87` |
| `reviews/push-live-review-v1/REVIEW-EVIDENCE-v1.json` | `fd1dab1b9eadaed71e9b5601642414b8ed158d8ce7c1a953bab51fc3b6d6a644` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/push-live-gate-v1/rebuild.py --output /private/tmp/native-push-live
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/push-live-review-v1/audit.py --output /private/tmp/native-push-live --report /private/tmp/native-push-live-audit.json
```

## Reviewed shared native storage clear

The native provider/push/pop crate now includes source-preserved `Storage.clear`
and its reset helpers. Existing provider, push, pop and native counter bodies
are preserved. Cross-module helper contracts use the existing guarded counter
observer; their earlier raw private-field projection produced an unbound symbol
and was rejected before proof acceptance.

The complete debug and release inventories each contain 79 models: 76 supporting
models and three disjoint provider induction models. Debug proves 614 supporting
obligations and release proves 531. The three provider proofs contribute 193,
15 and 81 shared leaves, giving 903 debug, 820 release and 1,434 unique solver
obligations. These induction leaves cover their three original models. Six
inherited atom/hash/deref wrappers have no goals; release also contains the
explicitly noncallable `requires(false)` zero-query wrapper. Empty models add no
substantive proof coverage.

The clear postcondition retains empty record and hash buffers, vector validity,
capacity frames, a zero high-water mark, counter length 4096 and every counter
zero. Added SmallVec clear/Deref and borrowed-array iterator view contracts
remain explicit assumptions, alongside inherited DOM, atom, vector, intrinsic
validity and count/readiness premises. No native Bloom contract is trusted.
Fresh root compilation uses authenticated cached dependencies; it does not
rebuild the Cargo dependency graph.

Independent review checks 8,949 input pins, both complete prototype inventories,
1,951 proof outputs, all raw results and the model partition. All 11,542 review
pins were rechecked. Five compiled mutations each fail exactly one intended
obligation: omitted record clear, hash clear, high-water reset, counter reset,
and a forced release zero query. Their `Unknown (unknown)` results are proof
sensitivity checks, not counterexamples. Five output/report/reference tamper
controls and four source/contract tamper controls also reject.

This checkpoint accepts the shared native model proofs under those premises.
The full clear postcondition's Lean history/accounting interpretation is
recorded below. Actual provider execution, recovery composition, global
observer interpretation and native completion remain open.

| Record | SHA-256 |
| --- | --- |
| `SHARED-NATIVE-CLEAR-EVIDENCE-v1.json` | `83849b5d6dbdb4459f14f56105932441422cdec4ae9f52d8601779e126a3e1a0` |
| `native-clear-integration-v1/check-v2/report.json` | `bd7d4427a004ec937e319db1e60f9e966df83f2b89da68f2618c7b38239ae04b` |
| `native-clear-integration-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `1fec0a5fe0568437fa8e347d4d050aea902a1db88e3eb58919eba68bd7937191` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-clear-integration-v1/gate-v2/rebuild.py /private/tmp/shared-native-clear
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-clear-integration-v1/reviews/checkpoint-review-v1/audit.py artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-clear-integration-v1/check-v2 --report /private/tmp/shared-native-clear-audit.json
```

The audit command authenticates the completed replay snapshot. A fresh solver
run has different timings and needs fresh review anchors.

## Reviewed shared clear interpretation

The complete selected `Storage.clear` contract now has a typed Lean
interpretation using the same stored counter, hash and record observers as
native push and pop. Its postcondition proves the encoded filter is empty from
all 4096 zero counters, then establishes empty history and record accounting.
The next pop and clear preconditions follow with explicit next-state equality
and borrow-intrinsic premises. The record sequence's empty interpretation and
the guarded counter-length domain remain explicit assumptions.

The exporter preserves the original task's 1,398 declarations and 2,338
identities while appending the unspecialized complete pre/post predicates.
Typed translation checks 14 types, 40 functions, six definitions and one
selected contract. Binding checks cover 18 shared functions, seven source
addresses, four datatype layouts, 13 intrinsic predicates and two rewrite
axioms. The selected unsigned bit-vector operations use bounded `Fin`
interpretations. Source equality links the count helpers to the preceding
count bridge; complete count-model and global observer interpretation remain
open.

A fresh dependency rebuild passes 52 modules and 91 theorem audits. All fifteen
new audits use only standard logical axioms. Independent review checks 877
outputs, 12,833 input pins and 141,236 lookup entries. All 1,378 review pins were
rechecked. The combined controls comprise 66 structural, 73 semantic, eight
canonical-root, twelve binding and five physical evidence checks. Semantic
mutants compile before their intended proof failures.

| Record | SHA-256 |
| --- | --- |
| `STORAGE-CLEAR-LIVE-EVIDENCE-v1.json` | `cba02dd5129c5d0b5721f80590051c8b61d2f3e5b3cafe35787e3c770a2f3aff` |
| `storage-clear-live-check-v1/report.json` | `830acaf5fe8244fcc3f57f85cf618ef625074f6af04576f84efc67b0044dc051` |
| `reviews/storage-clear-interpretation-review-v1/REVIEW-EVIDENCE-v1.json` | `aa5b33a656d0a41f56663837a0cb2fcc6bd4e47f1cd31a70c414b2ec0809e997` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/storage-clear-live-gate-v1/rebuild.py --output /private/tmp/native-storage-clear-live
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/storage-clear-interpretation-review-v1/audit.py --output /private/tmp/native-storage-clear-live --report /private/tmp/native-storage-clear-live-audit.json
```

## Reviewed native ancestor-chain interpretation

The shared stored-record observer now yields the ancestor stack used by
recovery: reverse record order, with each record mapped to its element. Ten
Lean theorems connect this observation to native record length and the last
record's element, push/prepend, pop/head-tail and clear/empty. Push followed by
pop returns the pushed element and restores the previous chain; clear followed by pop
returns `None`. Both composition results require the actual subsequent native
postcondition and an explicit connection between the two operations' states.

The fresh rebuild passes 53 modules and 101 theorem audits. All ten new audits
use only standard logical axioms. Independent review checks 904 outputs, 14,052
input pins and 141,236 lookup entries; all 1,428 review pins were rechecked.
Six new controls change chain order, operation endpoints, the empty-record
interpretation or the next-state connection and fail the intended proofs.
The combined inventory has 66 structural, 79 semantic, eight canonical-root,
twelve binding and five physical evidence controls.

Sequence length, append, record constructor and empty-sequence laws remain
explicit. These implications establish stack observations under the selected
contracts. Parent-edge consistency, recovery loop execution, resource bounds
and native completion remain separate obligations.

| Record | SHA-256 |
| --- | --- |
| `NATIVE-RECOVERY-CHAIN-EVIDENCE-v1.json` | `ceff6ef578bc56e7a65d2e095b2ccebcffa6610ac5131f6fa6c0a258e99ddec2` |
| `native-recovery-chain-check-v1/report.json` | `9239fa991959fe37fc978589b39915eba9aade3be8baeef051b1c7b48f9c4ec5` |
| `reviews/recovery-chain-review-v1/REVIEW-EVIDENCE-v1.json` | `d897ef7f7afa9d1cc700791a82f2f33b23fdcb3c31ade3e9852954e33fe63b85` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-chain-gate-v1/rebuild.py --output /private/tmp/native-recovery-chain
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/recovery-chain-review-v1/audit.py --output /private/tmp/native-recovery-chain --report /private/tmp/native-recovery-chain-audit.json
```

## Reviewed native recovery-stack adapters

The shared native crate now checks the exact `RecoveryStack` declaration and
five original method bodies as inherent adapters: constructor, length,
current-parent query, pending push and pending pop. Pending mutations preserve
the storage and provider fields. The query requires stored-record validity;
pending mutation requires pending-vector validity and push also requires room.

The sealed array domain now additionally admits `[E; 16]` for `E: TElement`,
with a distinct pending-sequence observer. Existing generic SmallVec contracts
gain this explicit new instantiation. The pending sequence is not identified
with the stored-record or hash sequences. Original `RecoveryState` trait
dispatch, parent/equality semantics, finite ancestry and recovery loops remain
open. Compilation uses authenticated cached dependencies.

The complete debug and release inventories each contain 84 models: 81 support
models and three disjoint provider induction models. Debug proves 648 supporting
obligations and release proves 565. The 289 shared induction leaves give totals
of 937 debug and 854 release. Counting shared induction once gives 1,502;
supporting obligations remain separate per configuration. This count is not a
global semantic deduplication. The inherited six debug and seven release empty
models supply no additional substantive coverage.

Independent review checks 2,627 outputs, 11,904 review inputs and 7,116 dependency
pins, including complete prototype compilation trees. All 14,547 review capsule
pins were rechecked. Induction roots and SMT leaves match the accepted shared
clear tasks after removal of source-location comment lines only. Five compiled
mutations each leave one intended timeout, testing pending ordering, current
parent, length and storage preservation. These are sensitivity checks, not
counterexamples. Five physical evidence and four source controls also reject.

| Record | SHA-256 |
| --- | --- |
| `NATIVE-RECOVERY-WRAPPERS-EVIDENCE-v1.json` | `bcee10724922f25d020c4a7bb8d70191f1c8ce8decec8d7476524050b7a90df1` |
| `native-recovery-wrappers-v1/checkpoint-v3.json` | `6147dd3a4ef7210b5d340414d00b14ee226e685e75f1bc09ab2ff7b778f226eb` |
| `native-recovery-wrappers-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `36aaf79621faedd02b93ed0a4cd500e7890e56f723ed1f9f3a1e6bf940318a64` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-wrappers-v1/reviews/checkpoint-review-v1/audit.py --report /private/tmp/native-recovery-wrappers-audit.json
```

This audit authenticates the completed replay snapshot. New timed solver runs
need fresh review anchors.

## Reviewed recovery storage adapters

`native-recovery-storage-wrappers-v1` extends the shared crate with exact native
`Storage.push` and inherent recovery clear, pop, push and parent bodies. Storage
contracts retain their complete conditions through the recovery storage field,
including both insertion-trace endpoints. Mutations preserve pending and provider
fields. The added parent observer assumes a stable DOM snapshot; native DOM
stability is not proved. Empty-storage insertion requires a root element, and
the sealed SmallVec model explicitly specifies `is_empty`.

All 89 models per configuration are covered: 86 support models and three provider
induction models. Debug proves 764 supporting obligations and release proves 656.
Adding 289 shared induction leaves gives totals of 1,053 and 945, or 1,709 counting
the shared induction once. Supporting obligations remain separate per
configuration; the inherited six debug and seven release empty models add no
substantive coverage.

Independent review checks 2,682 outputs, 14,811 review inputs and 7,116 dependency
pins. All 17,509 review capsule pins were rechecked. Inherited goal inventories
are unchanged, and induction tasks match after removing only complete source
location comments. Missing Rust source warnings are compared as exact multisets;
other warning order is retained. Compilation uses authenticated cached
dependencies.

Five compiled mutations each leave exactly one intended unproved obligation:
wrong parent, missing root premise, omitted pop and changed pending fields during
clear or push. Responses include timeouts and unknown results, so these are
sensitivity checks rather than verified counterexamples. Five physical evidence
controls and five source controls also reject. Trait dispatch, equality, finite
ancestry, recovery loops and allocation-enabled completion remain open.

| Record | SHA-256 |
| --- | --- |
| `NATIVE-RECOVERY-STORAGE-WRAPPERS-EVIDENCE-v1.json` | `a6d8464ba760e65658340960a02e454e8869880608eefbb166bfbd77c2dcb683` |
| `native-recovery-storage-wrappers-v1/checkpoint-v2.json` | `35a802d0f0973f8d7c4895d3d7f897980fd86dcf985a209ea265af18b4f5ae6e` |
| `native-recovery-storage-wrappers-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `f0864b01acc9522b4fbb28132bfcef26c55587e673431dbd395dc8d63a5f4461` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-storage-wrappers-v1/reviews/checkpoint-review-v1/audit.py --report /private/tmp/native-recovery-storage-wrappers-audit.json
```

This audit authenticates the completed replay snapshot. New timed solver runs
need fresh review anchors.

## Reviewed recovery trait binding

`native-recovery-trait-v1` binds the eight source-preserved runtime methods to
`bloom_recovery::RecoveryState`, imported by the sibling storage module. Sixteen
private logical predicates retain the complete native preconditions and
postconditions, with explicit before/after projections. The verification trait
adds `Sized` for value observers; the concrete implementation adds the existing
element equality bound. That bound supplies no proof relating runtime equality
to logical equality.

The eight method models, eight trait-refinement models and a generic pop-dispatch
probe add 103 checked obligations in each configuration. The probe transports
the abstract pop contract; it does not establish readiness or completion.
The complete inventories each contain 106 models: 103 support models and three
provider induction models. Supporting totals are 867 debug and 759 release.
With 289 shared induction leaves, totals are 1,156 and 1,048, or 1,915 counting
shared induction once. Supporting counts remain separate per configuration.

Independent review checks 2,630 outputs, 17,862 review inputs and 7,116 dependency
pins. All 20,509 review capsule pins were rechecked. Removing the two inserted
source fragments restores the inherited source byte-for-byte; all eight runtime
bodies also match exactly. Full contract reconstruction, unchanged inherited
goals, induction tasks and empty-model classifications pass. Three compiled
controls each produce one intended timeout: omitted trait pop, weakened trait
postcondition and strengthened trait precondition. Five source controls and five
physical evidence controls reject. These controls do not supply counterexamples.

| Record | SHA-256 |
| --- | --- |
| `NATIVE-RECOVERY-TRAIT-EVIDENCE-v1.json` | `40678362dd092f8eee34e9e256b98906e7425a23e215da121a4d6adad9b2a65c` |
| `native-recovery-trait-v1/checkpoint-v1.json` | `5e7399a83e04ac6d9fc9e48618201c124eee0614e12603ca3146b58dfda7877e` |
| `native-recovery-trait-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `6903866405670df58b17d2c41331293819d58dfb23d4ec4647e966504d00ee4b` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-trait-v1/reviews/checkpoint-review-v1/audit.py --report /private/tmp/native-recovery-trait-audit.json
```

This authenticates the completed replay snapshot, with cached compiler
dependencies and inherited library contracts. New timed runs need fresh anchors.
The next proof target is one pending-pop to storage-push iteration under a shared
ancestor/pending interpretation, explicit borrow validity and separate hash and
record capacity budgets. Relational native postconditions alone cannot instantiate
the existing extracted recovery theorem's successful-call requirements.

## Reviewed native pending interpretation

`native-pending-contract-translation-v1` translates the actual trait pending-push
and pending-pop contracts, including their complete entry/exit predicates and
borrowed endpoints. Two freshly built Lean modules pass 16 standard-axiom audits.
The interpreted pending stack reverses the actual ordered pending sequence.
Theorems establish push/pop order, the empty case, strict decrease after a
successful pop, validity/capacity frames and preservation of the complete storage
value. The next pop's precondition follows under an explicit new borrow endpoint
and its intrinsic validity.

Independent replay produces byte-identical Lean sources and objects and the same
16 audits. Six fresh native canonical/typed export replays reproduce complete
stdout and stderr exactly. The original theory prefixes and both roots per model
are retained; only complete pre/post predicates are appended. The inherited
export summary incorrectly named the earlier clear model. That stale summary is
explicitly rejected; provenance comes from actual command paths, guarded pending
model hashes and exact contract capture.

Twelve structural, eleven generated semantic, five shared-binding and four
canonical controls pass. Each semantic mutant compiles as a generated module,
then fails exactly its expected interpretation check. Bindings check 22 shared
function signatures, four datatype/borrow layouts, native observer locations and
both pending aliases. The fresh replay authenticates 17,894 toolchain lookup
entries; all 272 independent review capsule pins were rechecked.

| Record | SHA-256 |
| --- | --- |
| `NATIVE-PENDING-CONTRACT-EVIDENCE-v1.json` | `08a0cf74b5d2338b575e15ecaea4207d3baedac4893eef4366908ae1d9a87e81` |
| `native-pending-contract-translation-v1/check-v1/report.json` | `8fa1f186d4dd3654fcedf31e0e889af3176b8ed2be9058c49b39d3f43d0b8707` |
| `reviews/native-pending-translation-review-v1/REVIEW-EVIDENCE-v1.json` | `1ae6f42472d173002fcb4d89377c95cdadafb1743c65312cd31b1d9db8f77a47` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-pending-contract-translation-v1/gate-v1/rebuild.py /private/tmp/native-pending-replay
```

Use a fresh output directory. Sequence length/snoc laws, native intrinsic
predicates and observer meanings remain explicit premises. The complete storage
value is preserved abstractly; this result does not itself identify all storage
observers with the existing `Live` interpretation or establish execution.

## Reviewed conditional flush composition

`native-recovery-flush-v1` adds fifteen Lean proofs connecting the interpreted
native pending-pop result to the shared storage push contract. Separate hash and
record budgets derive the full `push_internal` precondition. The interpreted
posts preserve the combined pending/ancestor path, remaining budgets and `Live`.
A separate root condition permits an empty ancestor chain only when the next
element has no parent in the supplied parent snapshot.

Independent review rebuilds four modules and checks 31 standard-axiom audits,
including the fifteen new proofs. Nine semantic mutations cover path order,
both budgets, root admissibility, borrowed endpoints, popped identity, output
path, `Live` endpoints and consumed hash cost. Five physical controls reject
changed, missing or unexpected output, a changed reference and a forged report.
All 1,782 review capsule pins were independently rechecked.

The accepted 53-module parent closure remains an authenticated cache. Its
14,049 source pins, 141,236 external lookup entries and 904 outputs are checked
before and after the fresh four-module replay. This is not a fresh rebuild of
the complete dependency closure.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-flush-review-v1/REVIEW-EVIDENCE-v1.json` | `32aedb33c632102462673ebd5b8c86d9cfb0f0c9b50df75b85df034d6fdbc35f` |
| `native-recovery-flush-review-v1/check-v1/gate-report.json` | `4114901a8d597bbc61d57339c4ae39014e6104a71e5feda0f687d77e3d818a41` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-flush-review-v1/rebuild.py /private/tmp/native-flush-replay
```

Use a fresh output directory. Every composed call retains an explicit borrowed
storage endpoint, intrinsic validity and native postcondition premise. The
parent snapshot is not yet tied to the native parent observer. The next target
is the actual `RecoveryStack.push` contract and its pending frame. Provider
completion, successful extracted calls and the full recovery loop remain open.

## Reviewed native pending flush loop

`native-recovery-flush-loop-v1` checks a concrete specialization of the identical
pending-flush loops in `rebuild` and `recover`. Explicit qualification retains
`RecoveryState` dispatch. Removing snapshots, annotations and ghost calls restores
the production loop; deleting the inserted fragment restores the accepted trait
crate byte-for-byte.

The loop preserves the old record prefix, appends the initial pending elements
in reverse order and empties the pending stack. It establishes exact hash and
record totals, validity and capacity/provider frames under separate resource
budgets. A decreasing pending-length variant is checked. The root premise applies
when the record list is initially empty; complete ancestor correspondence remains
separate.

Four new models contribute 64 obligations per configuration: 58 for the loop,
one for the checked order-extension procedure and five for the hash-cost helpers.
The guarded inventory contains 110 models per configuration, comprising 107
support models and three provider induction models. All 931 debug and 823 release
support obligations pass. With 289 shared induction leaves, totals are 1,220 and
1,112, or 2,043 counting shared induction once.

Five compiled mutations each leave one intended timeout and 63 valid obligations:
missing hash budget, missing record budget, missing root condition, forward output
order and a constant loop variant. These are sensitivity results, not
counterexamples. Independent review reproduces the collector, checks raw results,
commands, inherited task correspondence, cached compiler dependencies and complete
output inventories. Five physical source controls and five evidence controls
reject. All 23,749 review capsule pins were independently rechecked.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-flush-loop-v1/checkpoint-v1.json` | `ad222f69fad1f186bfb50e8787c7276a5754a827306cef9545b403adf518f5d8` |
| `native-recovery-flush-loop-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `db78d3fc1db52a70e20f7178025c833c7f9e5278dad657157a4a0fb356168e24` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-flush-loop-v1/reviews/checkpoint-review-v1/audit.py --report /private/tmp/native-flush-loop-audit.json
```

This audits the completed snapshot without rerunning solvers. Native method and
library contracts remain explicit. Provider completion, DOM parent stability and
the surrounding recovery algorithms remain open. The next native target is a
finite trace connecting each actual pop/push transition to the Lean invariant.

## Reviewed recovery push and parent interpretation

`native-recovery-push-translation-v1` translates the complete native trait push
and parent contracts. Its three fresh Lean modules pass seventeen standard-axiom
audits. The push bridge retains all eleven storage postconditions and the exact
pending/provider frames. It derives the complete trait entry condition from the
separate budgets, root relation and explicit intrinsic validity.

Composition now reaches the final recovery state: path, `Live`, remaining hash
and record budgets, pending decrease and the parent-result equation are checked.
Both nested storage endpoints and the join between consecutive recovery-state
calls remain explicit. The parent equation describes the supplied native snapshot;
DOM stability and call completion remain open.

Independent replay produces byte-identical sources, objects and all seventeen
audits. Of 156 outputs, 130 are identical and 26 differ only in the fresh output
path. Twelve schema, nine generated semantic, three endpoint, six binding, four
canonical and eight provenance controls pass. Source review corrected stale
function/type indices in the binding checker and added normalized-key and Option
branch checks. A discovery run exposed relative Lean paths selecting an original
module; the final gate checks absolute import resolution for every positive and
mutated module.

Both replays authenticate the cached 53-module chain and four-module flush
closures before and after compilation. This remains a selected interpretation,
with explicit primitive/sequence laws, borrowed endpoints and intrinsic predicates.
The generated provider value is unit. No joint global intrinsic interpretation,
provider completion or complete recovery result is inferred.

| Record | SHA-256 |
| --- | --- |
| `NATIVE-RECOVERY-PUSH-INTERPRETATION-EVIDENCE-v1.json` | `68cde98a70e5b10a3febadb4ed7f4081b244afaa44e91231980ca2c932576659` |
| `native-recovery-push-translation-v1/RECOVERY-PUSH-TRANSLATION-PROTOTYPE-v1.json` | `8ed1141b3fc0a915fd12da508f610b5798286cc34fc39a7e447dce0d03c6acd6` |
| `reviews/native-recovery-push-review-v1/REVIEW-EVIDENCE-v1.json` | `e8ee35db39ed06a90789e27dd0f1b2eacfb37474072c224027010d5a223068a8` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-push-translation-v1/gate-v1/rebuild.py /private/tmp/native-recovery-push-replay
```

Use a fresh output directory. The next connection is the finite native flush
trace, retaining each explicit transition and the final empty-pop frame.

## Remaining interpretation work

Connect the native enumeration trace to the exact successful return of the
opaque extracted enumerator, preserving its callback, ordered events and
initial/final endpoints. An existential represented state with equal observed
lists does not establish that correspondence. The actual provider continuation
equation is now proved separately and need not be assumed.

The retained enumeration extraction failure involves nested-borrow restoration.
Its proposed tool extension needs a justified association between symbolic
projections and future arguments before implementation. The accepted pop adapter
now links the caller predicate to the checked helper definition and preserves
both return paths. Exporting the unspecialized contract avoids the ambiguous
branch-specialized clauses found during preflight.

The selected stored-history invariant now derives the full pop precondition
and is preserved by its interpreted postcondition. The next priority is
establishing this invariant from actual provider execution and connecting it
to recovery and clear under the same observer interpretation. The reviewed
count bridge now derives the full native clear precondition from history,
including after pop. Native push's interpreted post now preserves this same
history and accounting through ordered counter updates, hash and record appends,
and the high-water maximum, starting from explicit counter length and laws.
The shared native provider/push/pop/clear crate now passes its complete model
inventory. The typed clear postcondition now derives empty history and
accounting and establishes the next operation preconditions under the same
observers. The ancestor-chain observations now follow those same posts. The
next priority is connecting them to recovery's pending sequence, parent
relation and loops. The constructor, queries and pending wrappers now have
checked native bodies and frames, as do the storage mutation and parent wrappers.
Their shared trait binding is now checked under the complete projected contracts.
The pending-sequence interpretation now retains its exact ordering and storage
frames. Conditional pending-pop to storage-push composition now preserves history,
ancestor order and budgets while deriving the full `push_internal` precondition.
The selected recovery-stack push frames and parent-result equation now share this
interpretation. The finite native flush trace, including its final empty-pop
transition, now preserves the same storage invariant and ancestor observations.
The complete native rebuild body and its generated clear/collection/flush relation
now have a reviewed conditional connection to that Lean interpretation. The
interpreted rebuild post establishes `Live`, empty pending and the exact supplied
ancestor chain. Actual DOM correspondence and the remaining `recover` branches
remain separate.
The native filter reset now has conditional extracted endpoint correspondence.
The native storage reset path is now checked under its count/high-water and
library premises and its postcondition now uses the shared storage observers.
Linked-pop integration remains useful
but does not discharge primitive semantics or the provider boundary. Complete
recovery and the next borrow's intrinsic validity remain open.

The matcher still has a preserved verifier limitation involving its borrowed
dynamic callback, associated data and mutable cache reference. The reviewed
runtime capability experiment remains separate from storage interpretation.

## Scope and assumptions

These are scoped interpretations of pinned generated predicates and conditional
Lean implications. They are not a general verified Why3 importer or an
end-to-end native execution proof. Applying the native storage result requires
its full source preconditions, including independent element-record capacity
and native type invariants. Sequence/counter meaning and primitive vector
refinement remain explicit. The imported extracted library retains opaque
SmallVec operations, recorded in the axiom inventory.

Native allocation-enabled completion, enumeration correspondence, DOM hash
stability, thread safety and complete recovery remain open. No additional
Firefox defect is established by this checkpoint. The two existing production
fixes and their WPT commits are unchanged.

The separate [HeaderSlice finding](HEADER-SLICE-FINDING.md) records a library API
defect encountered during matcher modeling. Browser reachability and a production
fix remain unestablished.

The old roadmap is retained byte-for-byte because earlier reviewed evidence
pins its contents. Experimental packages and their toolchains remain local
artifacts; this file records their scope and reproduction entry points.


## Reviewed native pending flush trace

The isolated `native-recovery-flush-trace-v1` package retains the concrete
specialization of the production pending flush loop and adds a finite trace of
its explicit pop/push contracts. A separate final empty-pop transition connects
the last trace state to the returned state. The contract preserves the complete
storage value at that transition; it does not assert equality of the whole
recovery state.

All 111 models pass in both configurations: 108 support models contribute 929
debug and 821 release obligations, and three identical induction models add 289
shared obligations. That is 1,218 debug and 1,110 release obligations, or 2,039
counting the shared induction once. Supporting obligations are still counted
separately per configuration. The trace loop and four helpers contribute 62
obligations per configuration. The earlier indexed-order loop checkpoint remains
separate and unchanged.

Independent review reproduced the checkpoint and mutation collectors, checked
complete output inventories and cached dependencies, and verified that erasing
ghost code recovers the production loop. Five source mutations and five physical
evidence mutations were rejected. Five compiled controls each leave exactly one
intended obligation unresolved and the other 61 valid: reversed push endpoints,
a wrong next state, a nonempty terminal pop, whole-state equality at termination,
and an initial endpoint bound to the final state. Four timeouts and one Unknown
result establish sensitivity, not counterexamples.

The caller's edge predicate is opaque. Its checked introduction helper contains
the actual conjunction of explicit pending-pop and push contracts. Binding that
definition and the finite trace into Lean is the next step. This checkpoint does
not establish actual DOM ancestry, provider completion, or the surrounding
`recover` and `rebuild` algorithms. Milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-flush-trace-v1/checkpoint-v1.json` | `7ddc3a00638a7c7eca6fc02961dc193960c79e634dc6af72118b7862ac3a1f78` |
| `native-recovery-flush-trace-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `d5d5408a9d0dfa59f89bf1851127002b466abc19ca82afdeb4c0c7d7e999dfdf` |
| `NATIVE-RECOVERY-FLUSH-TRACE-EVIDENCE-v1.json` | `8baf847d99769701ac47f4dea215aa6ce183ab36bd17c30d7c1e8c1fa73ef2d4` |

The snapshot auditor checks the completed native proof evidence without rerunning
the compiler or solvers:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-flush-trace-v1/reviews/checkpoint-review-v1/audit.py --report /tmp/native-flush-trace-review.json
```


## Reviewed native ancestor collection

The isolated `native-recovery-collect-v1` package specializes the first loop in
`rebuild`. An additional erased snapshot supplies a finite ancestor sequence:
the first entry is the element's parent, each next entry is the preceding
entry's parent, and the last entry has no parent. The empty sequence means the
element has no parent. These are conditions on the native stable parent
observer, not a proof that the actual DOM supplies such a sequence.

The loop and checked ordering helper prove 45 obligations per configuration.
They preserve the old pending prefix, append the supplied ancestors in order,
and preserve the complete storage and provider values, pending validity and
capacity. A decreasing remaining-length measure bounds the loop, subject to
normal return of the native parent and pending-push calls. The entry capacity
budget excludes pending-vector growth.

The complete replay passes all 108 models: 912 debug and 804 release support
obligations, plus 289 shared induction obligations. Totals are 1,201 debug and
1,093 release, or 2,005 counting the induction once. Independent review reproduces
the checkpoint and controls, checks raw proof and model inventories, authenticates
cached dependencies, and reconstructs the exact production loop after ghost
erasure. Five source and five physical evidence mutations are rejected.

Five compiled controls remove the capacity premise, finite parent-chain premise,
storage-frame invariant or decreasing measure, or reverse the required final
order. Each leaves one intended obligation unresolved. The storage-invariant
removal also removes one obligation, leaving 43 valid; the other controls leave
44 valid. These timeouts establish sensitivity, not counterexamples.

Native call completion, actual DOM ancestry and the surrounding recovery
algorithms remain open. The next composition target is the complete `rebuild`
body: clear, collect ancestors, then flush the pending sequence.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-collect-v1/checkpoint-v1.json` | `ef24d9e860c9e1a0f7a1214145878eb2f170ce6cdf6e5ea33a0a305723086687` |
| `native-recovery-collect-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `537210b72f75de999ff60ff2222489803381afdf83266dada4f895e9f1a8fc34` |
| `NATIVE-RECOVERY-COLLECT-EVIDENCE-v1.json` | `3567b3a70f3b6149697c03d283bd58b19cb3f3cf267d4ec8d2ead8fa8ca036c9` |

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-collect-v1/reviews/checkpoint-review-v1/audit.py --report /tmp/native-collect-review.json
```


## Reviewed native flush trace interpretation

The isolated `native-recovery-trace-translation-v1` package translates the native
edge, indexed path, existential run, complete flush pre/postconditions and helper
pre/postconditions. It binds the caller's opaque edge to the helper's actual
explicit pending-pop/push conjunction, with checked source identities, signatures,
datatype layouts and prior contract definitions.

The three fresh Lean modules pass 22 standard-only axiom audits. Logical state-pair
adapters support the storage lemmas without asserting that an actual native borrow
exists. Explicit pending-pop contracts are used directly, without adding return
intrinsics. Bounded induction covers every edge, and the separate final empty pop
preserves the complete storage value while emptying the pending observation.
It does not identify the whole recovery state before and after that final pop.

Given the native flush postcondition, initial `Live` invariant and counter size,
the proof preserves both and obtains an empty pending observation. The final
record chain is the original stored pending sequence followed by the original
record chain. Equivalently, it is the reverse of the original pending pop order
followed by that chain. Counter, record, sequence and hash-operation laws remain
explicit. Actual DOM stability, native call completion and the full recovery
composition are not established by this theorem.

Independent replay reproduced all modules, audits and controls: 162 outputs are
byte-identical and 26 differ only by output-directory paths. Both fresh gates
authenticate the cached 53 chain, four flush and three push modules, their completed
output inventories and external lookup trees before and after compilation.

Controls reject 12 schema mutations, ten generated semantic mutations, five
state-pair mutations, six binding mutations, four canonical-task mutations and
eight provenance mutations. Two earlier metadata inequality checks remain labeled
as sensitivity probes; the six binding mutations invoke the actual positive
checker on rebuilt mutated indices. Milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-trace-translation-v1/RECOVERY-TRACE-TRANSLATION-PROTOTYPE-v1.json` | `32f21246a23c05d3d06e97358abb7fe77268b9e9bcde2460aad4a38e33819bab` |
| `native-recovery-trace-translation-v1/check-v1/report.json` | `4b2b139152afaf19dc6613952f451289ccbb1e2e7892fb4aa7f98d111ac21b1f` |
| `reviews/native-recovery-trace-root-v1/report.json` | `887edef6d14f6eb66408dfa94b4b3696e74f8b84db525c59b9b8ad9e904a73e3` |
| `reviews/native-recovery-trace-review-v1/REVIEW-EVIDENCE-v1.json` | `e09244696a7ae9d5539876a7ed2690328580f4f3092df098d1eb06242137b82d` |
| `NATIVE-RECOVERY-TRACE-INTERPRETATION-EVIDENCE-v1.json` | `c0dd5c7eb7a0d08f539ebcffeebc61f0885b874218e49da8c2602f408c298747` |

Rebuild into a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-trace-translation-v1/gate-v1/rebuild.py /tmp/native-recovery-trace-replay
```

## Reviewed native rebuild composition

The isolated `native-recovery-rebuild-v1` package checks the complete production
`rebuild` body specialized to the concrete recovery stack. Erasing ghost snapshots,
annotations and checked helper calls restores the production clear, ancestor
collection and pending flush statements. Both loops remain in the body.

The native postcondition connects the initial clear contract to a collected state
with identical storage and the supplied ancestor sequence as its pending values,
then connects that state to the returned state through the finite flush trace.
It also establishes empty pending storage and a final record count equal to the
ancestor count. Entry requires clear readiness, initially empty pending storage,
a finite stable parent-chain witness and separate pending, hash and record
capacity budgets. These budgets exclude vector growth.

All 115 models pass in both configurations: 112 support models contribute 1,064
debug and 956 release obligations, and three induction models contribute 289
shared obligations. Totals are 1,353 debug and 1,245 release, or 2,309 counting
the shared induction once. The nine new models contribute 197 obligations per
configuration, including 87 for rebuild and three for the checked sequence
extensionality helper. The first two attempts left an ordering assertion
unproved; their evidence is retained separately.

Independent review reproduces the checkpoint and control collectors, checks the
complete model and raw-output inventories, authenticates cached dependencies and
verifies production-body erasure and inherited helper correspondence. Five source
and five physical evidence mutations reject. All 35,536 review pins were checked
again by the root agent.

Five compiled controls remove initial pending emptiness or one of the three
capacity budgets, or bind the clear contract to the wrong initial state. Removing
initial emptiness leaves three intended timeouts and 194 valid obligations; each
other mutation leaves one timeout and 196 valid obligations. These are sensitivity
checks, not counterexamples.

The native method and library meanings and normal return remain explicit. This
checkpoint does not prove actual DOM ancestry, allocation-enabled completion or
the surrounding `recover` algorithm. The generated rebuild-to-Lean interpretation
is a separate gate in progress. Milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-rebuild-v1/checkpoint-v1.json` | `95a526735e89a91c34212cfa078cc38d17f880a342ef3eecf1d38d91f6876622` |
| `native-recovery-rebuild-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `9c87c5ee026c30cbd7c261bce5d96f357e163d6bf0fdb7ebf3988a165b943d21` |
| `NATIVE-RECOVERY-REBUILD-EVIDENCE-v1.json` | `2e2b341c69842a3bef5bbddab5370c5767f3d8b4566bfc7353ba7eb2c3639c3f` |

The authoritative snapshot audit includes the expanded input anchors and checks
the completed evidence without rerunning solvers:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-rebuild-v1/reviews/checkpoint-review-v1/audit_v2.py --report /tmp/native-rebuild-review.json
```

## Reviewed native rebuild interpretation

The isolated `native-recovery-rebuild-translation-v1` package binds the reviewed
complete rebuild contract to the accepted clear and finite flush interpretations.
The generated run retains the initial clear edge, identical storage between the
cleared and collected states, exact supplied pending sequence and final flush.
The clear binding retains all nine storage clauses and both pending/provider
frames. Logical Unit endpoint adapters do not establish actual native borrows.

The interpreted native rebuild post now establishes counter size 4096, the `Live`
storage invariant, empty pending observation and a stored ancestor chain exactly
equal to the supplied ancestor view. Initial `Live` is unnecessary because the
clear post establishes empty history. Native clear entry, valid borrowed execution,
finite stable ancestry, no-growth budgets and normal return remain separate.
The full entry predicate retains its distinct state and element intrinsics.

Independent fresh replay compiles three modules with fourteen standard-only axiom
audits and reproduces all controls: twelve schema, eleven generated semantic,
three relational-source, ten actual binding, four canonical and eight provenance
controls. All sources, objects and axiom output are byte-identical. Of 183 output
files, 157 are byte-identical and 26 differ only by the fresh output path.

Both gates authenticate the cached three trace, three push, four flush and 53
chain modules, their output inventories and external lookup trees before and
after compilation. Source review checks the limited unsigned-carrier transport:
exact ranges, value projections and unsigned comparisons, without normalizing
bitwise operations. Historical pending-provenance wording in frozen comparison
reports is superseded by the authoritative v2 native export capsule.

This closes the selected rebuild post interpretation. It does not establish
native call completion, actual DOM correspondence, full `recover` or milestone
4 completion. The next target is the remaining recovery control flow using the
same storage observers and explicit parent/depth and equality correspondence.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-rebuild-translation-v1/RECOVERY-REBUILD-TRANSLATION-PROTOTYPE-v1.json` | `6992919e2655d5e0edcfd4ebeb1be701abfef81f1af28b5e1bc7b64352e22360` |
| `reviews/native-recovery-rebuild-root-v1/report.json` | `42a024ce25eea6b6765ce6935584cf02fec855ad6fc709273adbcfad327f8389` |
| `reviews/native-recovery-rebuild-review-v1/REVIEW-EVIDENCE-v1.json` | `d28015694ea25bded4ba462d86d7e8c53b0911603552f2f1cb70d337c4e29592` |
| `NATIVE-RECOVERY-REBUILD-INTERPRETATION-EVIDENCE-v1.json` | `1170ec7a74ccd4939b6b2b89af09013c3f030c4c42dd92e5501ea3bbda8414d5` |

Rebuild into a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-rebuild-translation-v1/gate-v1/rebuild.py /tmp/native-recovery-rebuild-replay
```

## Reviewed native recovery depth trimming

The isolated `native-recovery-trim-v1` package specializes the actual depth-trimming
block in `recover`. Ghost erasure restores the initial depth calculation, pop
assertion, loop condition and decrement exactly. Entry requires a nonempty record
stack, positive requested depth and pop readiness at every state reachable from
the initial state through a finite sequence of explicit successful-pop contracts.

The post retains that finite pop trace and establishes a positive final record
count equal to the smaller of the initial count and requested depth. Pending,
provider and high-water values are unchanged. This native checkpoint leaves the
hereditary readiness premise explicit. A separate eleven-theorem Lean experiment
preserves validity, counter size and `Live` through finite pop paths, derives the
next storage precondition and identifies the final ancestor list as the initial
list with the popped prefix removed. Exact native predicate binding is the next
gate; logical endpoint adapters do not create native borrow witnesses.

All 109 native models pass in both configurations. The 106 support models have
926 debug and 818 release obligations; three provider induction models add 289
shared obligations. Totals are 1,215 debug and 1,107 release, or 2,033 counting
induction once. The three added models contribute 59 obligations per configuration.
Independent review reproduces the checkpoint and control collectors, checks exact
model/output inventories and cached inputs, and rejects five source and five
physical evidence mutations. All 35,199 review pins were independently rechecked.

Five compiled controls retain all 59 obligations. Removing readiness or positive
requested depth leaves the primary assertion or overflow obligation and an
ancillary trace-endpoint invariant unresolved, with 57 valid obligations. Removing
positive initial length, changing the final endpoint or using a constant variant
leaves one intended timeout and 58 valid obligations. These establish sensitivity,
not counterexamples or separate endpoint defects.

Native library meanings, borrow intrinsics and normal return remain explicit.
After binding readiness, the next target is a single source-preserved complete
`recover` composition with the accepted rebuild and flush results. Its initial
compilation experiment exposes the element equality boundary: Creusot requires
`DeepModel`, and the generated comparison contracts compare deep models. A
`Copy + Eq` bound alone does not establish identity correspondence. Actual DOM
parent/depth consistency and equality interpretation must be stated separately.
Milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-trim-v1/checkpoint-v1.json` | `0a4d2bb37a31ab5761cc7544a11281b8fb7769972329921145294dae692b35ca` |
| `native-recovery-trim-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `2fdc019174996b2fdad828795dc6aced9eec7830df7e854034c6f272207e38bf` |
| `NATIVE-RECOVERY-TRIM-EVIDENCE-v1.json` | `d4825a7faef2da4c942070e8c4a0ed3f3d7081d74ea4a596ee0c9420d9b4b890` |

Audit the completed native evidence without rerunning solvers:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-trim-v1/reviews/checkpoint-review-v1/audit.py --report /tmp/native-trim-review.json
```

## Reviewed native depth-trimming interpretation

The isolated `native-recovery-trim-translation-v1` package binds the checked
trimming contracts to the actual successful-pop edge and the accepted storage
interpretation. The finite indexed native path becomes a Lean pop path. Initial
vector validity, counter size 4096 and `Live` now derive the native hereditary
readiness predicate; it is no longer an unexplained assumption in this selected
interpretation.

The generated post preserves validity, counter size and `Live` and establishes
that the final ancestor chain is a suffix of the initial chain. Full pre/post
equivalences retain positive initial and requested depths, exact borrowed
endpoints, the conditional final record count, and pending/provider/high-water
frames. Logical Unit endpoint adapters do not establish actual native borrows or
runtime return witnesses. Counter, sequence and record laws remain explicit.

Independent fresh replay compiles three modules with 28 standard-only axiom
audits and reproduces twelve schema, twelve generated semantic, three state-pair,
ten binding, four canonical and eight provenance controls. All sources, objects
and axiom output are byte-identical. Of 196 outputs, 168 are byte-identical and
28 differ only by output-directory paths. Both gates authenticate the cached
53-module chain checkpoint, its 904 outputs and external lookup trees before
and after compilation. The first gate's packaging failure remains recorded;
the accepted runner is `gate-v2/rebuild.py`.

This closes the selected trimming readiness and post interpretation. Complete
recovery must use a mixed search relation because pending pushes change the
recovery state while preserving its storage. Native call completion, actual
DOM ancestry and provider execution remain separate. Milestones 4 and 6 remain
open; the separate exact-drop suffix experiment is outside this checkpoint.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-trim-translation-v1/RECOVERY-TRIM-TRANSLATION-PROTOTYPE-v1.json` | `265617c37fdb516285d395edcf337e1e2832361058d861429201ea17658a1680` |
| `reviews/native-recovery-trim-root-v1/report.json` | `0bc91952cfa1b4596243d30b373a03a137880d7acefa097ac11c5fa2188034dc` |
| `reviews/native-recovery-trim-review-v1/REVIEW-EVIDENCE-v1.json` | `119744f74ee77e43a1b09025b36d81020cc661c8c2972a3d59d6e31d240e560a` |
| `NATIVE-RECOVERY-TRIM-INTERPRETATION-EVIDENCE-v1.json` | `0694ed25a36114d2fbf66547f85a8bbe7c3e916fb0fb0587a4dc910c4eea6fcb` |

Rebuild into a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-trim-translation-v1/gate-v2/rebuild.py /tmp/native-recovery-trim-replay
```

## Reviewed complete native recovery

The isolated `native-recovery-complete-v1` package verifies the complete production
`recover` body specialized to the native recovery stack. Source erasure restores
all runtime branches and loops, including depth trimming, target ascent,
common-parent search and final pending flush. The post records four outcomes:
rebuild, clear, unchanged cache hit, or a finite search followed by flush. Pending
is empty on return. Search edges are actual successful storage pops or pending
pushes; pending pushes change recovery state while preserving storage.

All 122 models pass in each configuration. The 119 support models contribute
1,325 debug and 1,205 release obligations; three provider induction models add
289 shared obligations. Totals are 1,614 debug and 1,494 release, or 2,819 counting
induction once. The complete recover model contributes 239 debug and 227 release
obligations, with 22 further obligations from six new helpers. Six debug and
seven release models retain their explicitly inventoried zero-goal status.

All twelve compiled controls retain the complete 239-goal recover inventory.
They exercise readiness, exact depth, rooted records, shared roots, identity
reflection, independent record/hash/pending budgets, ancestry, the search
endpoint, pending order and the loop variant. Exact primary and ancillary
timeouts are checked; they demonstrate sensitivity, not counterexamples.
Independent review also rejects five physical source mutations and five physical
evidence mutations. Its audit reproduces the completed collector, source erasure,
raw output inventories and dependency checks. A separate root replay matches the
review exactly, and all 28,099 review pins pass a fresh hash check.

The original full-splitting proof attempt exceeded the bounded preprocessing
memory experiment. The successful recover run uses `compute_specified` and
`split_vc` without filtering goals. The failed attempt remains recorded, as does
an initial reviewer-only misclassification of the checked logical cost helper.

Native primitive and borrow semantics, finite stable parents, rooted initial
records, exact depth, equality reflection, shared roots when required, initial
empty pending, clear/search readiness and no-growth budgets remain explicit.
The separate generated Lean interpretation must still derive readiness and
compose final validity, storage history, exact ancestors and retained-hash lookup.
This checkpoint does not establish runtime completion or concrete DOM
correspondence. Milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-complete-v1/checkpoint-v1.json` | `df73824f8219508fc3ef0569ad68408541b1d6a375cca9d9129c83ad1963530e` |
| `native-recovery-complete-v1/reviews/checkpoint-review-v1/REVIEW-EVIDENCE-v1.json` | `97c53640c6a7f95856dba7b0d1809056cfcb00ccd2a73a0ab117dfb6a6669c6b` |
| `NATIVE-RECOVERY-COMPLETE-EVIDENCE-v1.json` | `12a359f6ecdcb0438fc30df856c62cf96e53c38af4b119c30f18af77e5bf712a` |

Audit the completed native evidence without rerunning solvers:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-complete-v1/reviews/checkpoint-review-v1/audit.py --report /tmp/native-recovery-complete-review.json
```

## Reviewed complete recovery interpretation

The isolated `native-recovery-complete-translation-v1` package binds the full
native recovery contract to the accepted storage, pending, rebuild and flush
interpretations. Exact typed exports preserve the native proof tasks and retain
the entire pre/post interface. Source and signature checks distinguish the
caller's opaque search edge from its separate flush edge and bind both search
helpers to their checked definitions.

The mixed search path preserves vector validity, counter size and `Live`;
initial validity and history derive hereditary search readiness. Rooted native
records and the complete ancestor witness use the same parent observation.
Their finite-chain properties establish the exact retained suffix for search
and the complete chain for a cache hit. Composing all four native outcomes
establishes final vector validity, 4096 counters, `Live`, empty pending and the
exact requested ancestor chain. Each represented ancestor's policy hash is
retained, and lookup on the encoded native filter returns true. Final validity
and history also derive renewed clear and search readiness.

Independent fresh replay compiles eight modules with 43 standard-only axiom
audits and reproduces 73 controls: fourteen structural, 21 generated semantic,
four Lean source, thirteen binding, six canonical and fifteen provenance checks.
All source files, objects and axiom outputs match. Of 385 output files, 325 are
byte-identical and sixty differ only by the fresh output path. Both gates
authenticate six accepted cached parent output trees and the complete external
Lean lookup inventory before and after checking. The snapshot audit rechecks
all 17,556 producer pins; the complete review record contains 17,947 pins.

The result retains explicit library, borrow and observation laws, initial
validity/history, stable finite parents and hash policy, identity reflection,
depth, shared-root and resource premises. Logical state-pair adapters supply no
runtime borrow witnesses. Lookup concerns the encoding of native observations;
actual native query and matcher calls remain separate. The old Aeneas provider
backward-function correspondence is not a premise of this native composition,
but remains required for claiming the earlier Aeneas execution equivalence.

Milestones 4 and 6 remain open. The next native work binds actual initialization
and wrapper entry: `StyleBloom::new` borrows an existing thread-local filter
without clearing it. First default construction, prior successful drop/clear
and exclusive borrowing must establish its zero state. A separate follow-on
also derives final pending validity and native rooted records for subsequent
entry; it is outside this frozen checkpoint.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-complete-translation-v1/RECOVERY-COMPLETE-TRANSLATION-PROTOTYPE-v1.json` | `6402cb97f7df00d3648eb7913972e5ec9f14f541d0a2a1e5841a9ab57d7f90cf` |
| `reviews/native-recovery-complete-root-v1/report.json` | `296cf25fa6b5f590d3391ea362032195e2c0cb69e1fb55556c693661c83779d7` |
| `reviews/native-recovery-complete-review-v1/REVIEW-EVIDENCE-v1.json` | `42549cc4b617aa8e8c238bb06ae392de1766513928d50f851c44782d89ee7018` |
| `NATIVE-RECOVERY-COMPLETE-INTERPRETATION-EVIDENCE-v1.json` | `9d4a97b0802dc5305ac2fe67c3870b2537524fc9aacb725fb281f440bfcc0297` |

Regenerate and check the interpretation in a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-complete-translation-v1/gate-v1/rebuild.py /tmp/native-recovery-complete-replay
```

## Reviewed recovery entry invariants

The separate `native-recovery-reuse-v1` package strengthens the complete recovery
interpretation with final pending validity and native rooted records. Flush
obtains pending validity from its terminal pending-pop contract; clear preserves
it through the pending frame, and an unchanged cache hit uses entry validity.
The exact final ancestor chain yields the native root-first record predicate,
including the root's terminal parent. These results compose with final vector
validity, counter size, `Live`, empty pending and clear/search readiness without
adding external premises.

Independent replay passes one module, seven standard-only axiom audits and three
source controls. The controls change the pending endpoint, omit entry pending
validity, and reverse record orientation; their exact failure diagnostics match.
Fifteen outputs are byte-identical and one control report differs only by output
path. The snapshot audit checks all 17,599 producer pins and both complete output
inventories; the review record contains 17,621 pins.

This establishes reusable state invariants, not every precondition of a future
call. Fresh target ancestry, resource budgets and actual borrow acquisition
remain separate. Initialization, thread-local ownership, native completion and
actual matching are still open, so milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-reuse-v1/RECOVERY-REUSE-PROTOTYPE-v1.json` | `1dbce95cbd6ec26d82eb980a556665401c54b0d16ee0605eec18f2d8b750f0ba` |
| `reviews/native-recovery-reuse-root-v1/report.json` | `46dd98d10b78c0b060f7430d476e68569f2095cf4d00db480882a8eab6c0ea01` |
| `reviews/native-recovery-reuse-review-v1/REVIEW-EVIDENCE-v1.json` | `c4df9f50d798d51ee0a38e4759eea607949cb242cab8b99ca69d925b61e37ded` |
| `NATIVE-RECOVERY-REUSE-EVIDENCE-v1.json` | `b08c365ee7bc1a589799eb748b6a6d62d984a2dbd73498a37ae12a34e78a5923` |

Replay the additional proof in a fresh output directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-reuse-v1/gate-v1/rebuild.py /tmp/native-recovery-reuse-replay
```

## Reviewed native storage constructor

The isolated `native-recovery-initialization-v1` package adds the exact production
`Storage::new` body to the complete recovery proof. Its four postconditions
equate each returned field reference to its input, preserving complete borrowed
references rather than only their current values. The generated model retains
the current, final and identity information needed for the wrapper bridge.

Both configurations pass all 123 models: 120 support models contribute 1,336
debug and 1,216 release obligations, and three shared provider induction models
contribute 289. The combined count is 2,841 with induction counted once. The
constructor adds eleven obligations per configuration. Three compiled controls
each retain exactly one intended timeout: resetting the high-water value,
collapsing a final borrowed value to an entry value, and denying filter reference
identity. These are sensitivity checks, not counterexamples. An earlier
clear-filter mutant has an unbound raw-counter import and is excluded.

Independent review checks exact source correspondence, reproduces the complete
evidence collector, audits all 1,231 checkpoint inputs and 2,375 outputs, and
rejects three physical source mutations. A fresh focused solver replay also
passes all eleven constructor obligations. The review record contains 3,613
pins. The complete support and induction solver runs are producer evidence,
independently checked through their raw outputs.

This constructor does not establish initial zero counters, empty vectors,
thread-local ownership or native completion. The separate typed interpretation
must connect explicit initial observations to valid storage history; actual
`StyleBloom` acquisition and drop remain lifecycle obligations. Milestones 4
and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-initialization-v1/checkpoint-v1.json` | `166f23bcde7da5e82eaf8a2461be06e3f345be0bf55b6849e80b17c997fa9a18` |
| `reviews/native-recovery-initialization-root-v1/REVIEW-EVIDENCE-v1.json` | `c07240b95a8798bd99ed8018af01f352fea63f5d90226d870abe8b0a0b58c80b` |
| `NATIVE-RECOVERY-INITIALIZATION-EVIDENCE-v1.json` | `895d459b6c612af1de60bb4e09473f72f58a8b8dc803c187688ccd5b3742d2cb` |

Audit the completed constructor evidence:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/native-recovery-initialization-root-v1/audit.py --report /tmp/native-recovery-initialization-review.json
```

## Reviewed storage constructor interpretation

The separate `native-recovery-initialization-v1/translation-v1` package preserves
the full typed constructor pre/post, including the result intrinsic and equality
of all four complete reference fields. Exact origin and signature checks bind
twelve shared functions, three layouts and the shared intrinsic declarations to
the accepted recovery export. A preflight origin mutation exposed an insufficient
normalized-name comparison; the final binding checks exact origins as well.

The Lean interpretation transports supplied observations through those reference
equalities. Zero counters, empty records and hashes, and a zero high-water mark
establish accounting and storage history. Explicit vector validity and counter
size then yield an intrinsic, valid result with 4096 counters, `Live` and an empty
ancestor chain. A separate lemma establishes the native rooted-empty predicate.

Independent fresh replay passes three modules, eight standard-only or axiom-free
audits and all 22 controls: five structural, three binding, four generated
semantic, three missing-observation source, two canonical and five provenance.
Of 59 outputs, 56 are byte-identical and three differ only by the output path.
The snapshot audit checks all 20,973 producer pins; the complete review contains
21,038 pins. Both gates authenticate the accepted cached parent and external
lookup inventories before and after checking.

The initial observations are premises, not consequences of acquiring the
thread-local filter. Actual default construction, `AtomicRefMut` acquisition,
native completion and the remaining recovery entry composition remain separate.
Milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-initialization-v1/translation-v1/STORAGE-CONSTRUCTOR-INTERPRETATION-PROTOTYPE-v1.json` | `b053b2b410d4fa553dc2f27072ade296ac72c58aee015ee63e69b6df37484176` |
| `reviews/native-storage-constructor-interpretation-root-v1/report.json` | `595c9cc56786ac0a7f42e7b1a9c0dd17a8f1533cf559fa3d541514b6fa86ba2b` |
| `reviews/native-storage-constructor-interpretation-review-v1/REVIEW-EVIDENCE-v1.json` | `a11abc31cf1e7c50d73b4b1dd30de8a124c5415363e183b3f3a0d35c1354cbb8` |
| `NATIVE-STORAGE-CONSTRUCTOR-INTERPRETATION-EVIDENCE-v1.json` | `8ed1134c108e1a8e0462d5e052e80d4d049cbf13d06893b661381eb00adc50c3` |

Regenerate and check the interpretation in a fresh directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-initialization-v1/translation-v1/gate-v1/rebuild.py /tmp/native-storage-constructor-interpretation-replay
```

## Kleene helper proof prototype

The matcher experiment under
`matcher-dyn-capability-candidate/backend-v1/actual-context-v1/native-kleene-v1`
preserves the production Kleene enum variants and handwritten helper bodies.
Proof adapters add named generic parameters, `IteratorSpec` bounds, enum proof
derives, contracts and erased witnesses. The copied enum is still a distinct
nominal type.

The exact truth-table contracts prove the operator law used by `any_value`.
On normal return, `any_false` returning `True` implies iterator exhaustion and,
for every visited item, a successful callback postcondition witness from a state
related to the initial callback by its history invariant. The dual property
holds when `any` returns `False`. These are independent per-item witnesses, not
a connected callback trace or final borrow-restoration result. Readiness for
every generic item and history-related callback state remains an explicit
premise; the actual selector caller needs a narrower reachable-item condition.

All sixteen models pass 85 obligations, with one generated `Eq` marker model
simplifying to zero goals. A fresh Cargo target reproduces every model exactly
and passes all 85 obligations again. Three compiled controls reject early success,
omitting the first callback result and dropping the left conjunction operand.
The first two retain 85 goals and one intended timeout each; the last has 84
goals and two intended `Unknown(sat)` results. No concrete counterexample is
claimed. Bounded independent review finds no blocker in the conditional theorem.
The prototype has 303 evidence pins; complete compiler and Cargo lookup guarding
remains pending, so it is not an aggregate acceptance checkpoint.

A separate `native-enum-model-v1` experiment reverses the dependency: an isolated
verification-library copy depends on ordinary selectors and owns proof models
for its native enums. The original compound body now translates with both Rust
enum comparisons unchanged. Adding exact context accessor contracts yields
three models, eight valid obligations and two timeouts at the featureless-host
helper and `any_false` boundaries. The two accessor models simplify to zero goals.
This establishes translation feasibility, not actual matching. Native equality,
the iterator relation and actual `next`, callback execution, and `HeaderSlice`
ownership still require binding and proof. No production source is changed.

The following paths are relative to `actual-context-v1`:

| Record | SHA-256 |
| --- | --- |
| `native-kleene-v1/KLEENE-PROTOTYPE-v1.json` | `21cd57c4e742ce70e7a65b520c180cf84cabf62fe2f50ac755042b7d0d98d928` |
| `native-kleene-v1/reviews/source-review-v1/REVIEW-v1.json` | `083a76f69fcfbf22b996f25799eb98581309dd9beb3922c4c9160ffbdea866a6` |
| `native-enum-model-v1/DIAGNOSTIC-v1.json` | `29dffa7c0be37f3a1392c154c2e5216aa4c4849b83f09fc93a6d6e122b49efb5` |

## Reviewed complete recovery entry

The `native-recovery-stack-initialization-v1/translation-v1` interpretation joins
the exact `Storage::new` and `RecoveryStack::new` posts. The latter preserves the
state intrinsic, storage identity, empty pending values, capacity 16 and pending
validity. An explicit current-borrow endpoint connects the constructed state to
the actual argument of the recovery contract.

With the initial zero/empty/valid observations, the theorem establishes the
complete recovery precondition and `Valid`, 4096 counters, `Live` and an empty
ancestor chain. It derives clear/search readiness and rooted-empty records;
the shared-root condition is vacuous for empty records. Borrow and element
intrinsics, finite ancestry, exact depth, equality reflection and independent
pending/record/hash budgets remain explicit premises.

Independent replay passes two modules, three standard-only or axiom-free audits
and all 26 controls: five structural, three binding, six generated semantic,
five source, two canonical and five provenance. Of 73 outputs, 70 are identical
and three differ only by the output path. The snapshot audit checks 21,256
producer pins; the complete review contains 21,335 pins. Both gates authenticate
cached parents and the external lookup closure. Binding checks cover fifteen
shared functions, two layouts and the shared intrinsic declarations and rewrites.

This closes the conditional constructor-to-entry composition. Initial observations
are still premises; actual TLS acquisition, `AtomicRefMut`, wrapper execution,
DOM/provider binding and native completion remain open. Milestones 4 and 6
are not complete.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-stack-initialization-v1/translation-v1/STACK-CONSTRUCTOR-ENTRY-PROTOTYPE-v1.json` | `79a4c1a3102471a6282c0f64e355b4fd6867b3e6b8180abf772b4a9cc547df77` |
| `reviews/native-recovery-stack-entry-root-v1/report.json` | `b6c353c9b5a61286702cb7f875108429066c3ddc5e17569ace835facb08c3b6f` |
| `reviews/native-recovery-stack-entry-review-v1/REVIEW-EVIDENCE-v1.json` | `4660bd0bed9412608b725269cf9f1709a374e470b707f7c796827051b1a3d2a2` |
| `NATIVE-RECOVERY-STACK-ENTRY-EVIDENCE-v1.json` | `405436de05beecd64b7ea63d20e90cfad5e45f7be67296e45570d83eaa5d70dd` |

Regenerate and check the entry interpretation in a fresh directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-stack-initialization-v1/translation-v1/gate-v1/rebuild.py /tmp/native-recovery-stack-entry-replay
```

## Reviewed caller reuse composition

The separate `native-recovery-caller-reuse-v1` package derives reusable rooted
records, `Valid`, 4096 counters and `Live` from the previous recovery post. A
second lemma joins those invariants to fresh constructor posts and establishes
the complete next recovery precondition, preserved invariants and unchanged
ancestor chain, including when retained records are nonempty.

Four explicit current-value correspondences connect the previous final storage
to the new filter, records, hashes and high-water inputs. Old and new reference
identities need not agree. The parent snapshot, policy/hash observers and equality
interpretation remain shared across calls; preservation across DOM or policy
mutation is not claimed. Common root, ancestry/depth, intrinsics and independent
budgets remain premises. Record and hash budgets include retained counts.

Independent replay passes one module, two standard-only axiom audits and eight
source controls. Thirty outputs are identical; the remaining control report
differs only by output path. The snapshot audit checks all 21,376 producer pins;
the complete review contains 21,417 pins and includes the accepted stack-entry
evidence. Both gates authenticate the cached parent and external lookup closure.

Actual wrapper field restoration, `AtomicRefMut` dereferencing, TLS acquisition
and native completion remain open. This is a conditional composition checkpoint;
milestones 4 and 6 are not complete.

| Record | SHA-256 |
| --- | --- |
| `native-recovery-caller-reuse-v1/CALLER-REUSE-PROTOTYPE-v1.json` | `f19677b89eff491311f9c75f50e0b58b88cdf04e928e0967af2c2c44e902ad6f` |
| `reviews/native-recovery-caller-reuse-root-v1/report.json` | `47399bb89bce2ec84ff68731a271646100e8159134d2cf5ba25c80c487d76c8d` |
| `reviews/native-recovery-caller-reuse-review-v1/REVIEW-EVIDENCE-v1.json` | `35087f2aecfcb171ce6e7542a4db8e6d5bcb7229f0676f19375570ac8200df0c` |
| `NATIVE-RECOVERY-CALLER-REUSE-EVIDENCE-v1.json` | `68775f127aeb93b208585ee65c63227c1618912a0187088ad7098b50a6ed764f` |

Regenerate and check the caller composition in a fresh directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-recovery-caller-reuse-v1/gate-v1/rebuild.py /tmp/native-recovery-caller-reuse-replay
```

## Imported native Kleene helper prototype

The separate `actual-context-v1/native-kleene-imported-v1` package uses the actual
imported `KleeneValue` type through the frozen verification-library dependency
arrangement. Ten native helper bodies are checked as free functions, with explicit
receiver, `Self` and call-name transport. Two external operator contracts match
the contracts of separately checked conjunction and disjunction bodies. The source
audit checks every transported signature and runtime body against production.

Callback readiness now ranges over items in sequences the initial iterator can
produce, rather than every value of the generic item type. The conditional
normal-return result remains iterator exhaustion and independent successful
callback witnesses when `any_false` returns `True`, with the dual for `any`.
It does not establish a connected callback trace or final borrow restoration.

Eleven models pass 71 obligations. A fresh Cargo target reproduces all models
exactly and passes the same obligations. Four compiled controls reject early
success, an omitted first result, a missing conjunction operand and a missing
readiness premise. Three retain one intended timeout each; the conjunction
control has 70 obligations and two intended `Unknown(sat)` results. These are
sensitivity checks, not concrete counterexamples. Independent source review
prompted the complete signature inventory and checks four physical source
mutations. The prototype records 476 pins.

The first control runner reused a Cargo target and encountered a successful
compile without regenerated models. Its inventory check rejected that run;
the retained controls each use a separate target. A collector diagnostic also
identified four expected warning-location shifts in the missing-premise control;
the final collector checks those exact shifts.

No `IteratorSpec` instance for native `SelectorIter` is installed. Its `next`
requires no pending combinator for debug assertion safety, while stopping at a
combinator sets one. The actual caller must establish readiness for every call;
relation laws alone do not discharge that obligation. Native equality binding,
iterator/callback execution, borrow restoration and complete toolchain lookup
guarding remain open. This is not aggregate acceptance or milestone 6 completion.

Paths below are relative to `actual-context-v1/native-kleene-imported-v1`:

| Record | SHA-256 |
| --- | --- |
| `IMPORTED-KLEENE-PROTOTYPE-v1.json` | `ab914b2cd9c99a6a4bad6ac6a749b1a3db0bfbff2f61d60b4f0e62ce488d9089` |
| `SOURCE-AUDIT-v2.json` | `890d97aae561cf34fb072cd0ba72f4cefaa594d7b87335c195f032ebc8b05749` |
| `reviews/imported-source-review-v2/REVIEW-v2.json` | `e972cc9e1e66c087e6d881416f224b0914ca38310ef6ea2079ffddaf53b7cdaf` |

## Reviewed native owner storage contract

The `native-style-bloom-storage-v1` package preserves the exact `StyleBloom`
layout and `storage` body with the actual imported `AtomicRefMut` type. Its
mutable-reference field and opaque borrow guard remain present. Three dependency
visibility edits and four storage-field visibility edits permit inspection.
The native generic `DerefMut` body is checked separately with explicit receiver
and lifetime transport; its three posts exactly match the external contract.

The owner method proves current and final observations for all four storage
fields and preserves the guard. It does not equate complete old and new reference
identities. The source audit's pinned `bloom.rs` snapshot also matches the current
production file.

Both guarded compilations contain 125 models. The 123 inherited models per
configuration match the accepted constructor checkpoint after only source-path
rebasing; their authenticated proofs are reused. The two new models are identical
in debug and release. Independent replay passes all 41 new obligations: 32 for
storage and nine for reborrowing. Five compiled controls each retain 40 valid
goals and one intended timeout; all five physical source controls were also
independently replayed. Collector reproduction checks 4,972 producer pins, and
the complete review contains 5,016 pins.

An immutable erratum corrects an inherited exploratory label in the selected
proof reports: a paired external `DerefMut` success contract is present. The
source audit and checkpoint disclose it; raw proof evidence remains unchanged.

TLS acquisition, ownership protocol, `Drop`, actual caller temporary restoration
and native completion remain open. Composing this contract with caller reuse
still requires the prior recovery field-resolution equations or a checked caller
body that establishes them. Milestones 4 and 6 remain open.

| Record | SHA-256 |
| --- | --- |
| `native-style-bloom-storage-v1/checkpoint-v1.json` | `6f0d80b71b1f76cd87d8216000d85299cbc0281eb940c44df33839ab3ab4f595` |
| `native-style-bloom-storage-v1/PROOF-SCOPE-ERRATUM-v1.json` | `259d95d216135d55bbaf26a4bdc9d62ebb08c52460432a1687f379726043445e` |
| `reviews/native-style-bloom-storage-root-v1/REVIEW-EVIDENCE-v1.json` | `b6016b3e4a5adfcc4dd8622e08bde177967767a88e451b0f502ca560b47cfbb9` |
| `NATIVE-STYLE-BLOOM-STORAGE-EVIDENCE-v1.json` | `82377a00eb3c459c241f4ea0eacc659c0f654aadd0c9f24da3c91441b7d0bf43` |

Audit the completed evidence:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/reviews/native-style-bloom-storage-root-v1/audit.py --report /tmp/native-style-bloom-storage-review.json
```

## Reviewed owner storage interpretation

The `native-style-bloom-storage-v1/translation-v1` package exports the exact
native owner storage pre/post predicates without changing the original
245-declaration, 478-identity verification task. Typed metadata and recursive
validation cover eleven types, 24 functions and five layouts. Shared binding
checks compare thirteen functions, three layouts and the storage intrinsic
closure with the accepted constructor export. Four explicit field-projection
renamings account for the enclosing owner's field names.

Two owner posts and a shared owner endpoint establish four old-final to
new-current storage observations and guard preservation. Combining these with
four explicit prior recovery field-resolution equations supplies the observations
needed by the accepted caller-reuse theorem. The resulting theorem establishes
the complete next recovery precondition, reusable invariants and unchanged
ancestor chain. It preserves the stable DOM/policy, ancestry, identity, intrinsic,
common-root and independent capacity premises, including retained counts.

Independent replay rebuilds three modules and passes six axiom audits: five
axiom-free interpretation lemmas and one standard-only composition lemma. All
29 controls pass: five structural, four binding, eight generated semantic, six
source, two canonical and four provenance. Of 103 outputs, 101 are identical and
two dependency lists differ only by output path. The snapshot audit checks all
23,026 producer pins; the complete review contains 23,136 pins. Both replay gates
authenticate cached parents and external lookup closure; the parent Lean graph
is not rebuilt here.

The actual caller must still establish the four field-resolution equations and
current-state borrow endpoint. Complete reference identities are not equated.
TLS acquisition, ownership protocol, native completion and preservation across
DOM/policy changes remain open. Milestones 4 and 6 remain incomplete.

| Record | SHA-256 |
| --- | --- |
| `native-style-bloom-storage-v1/translation-v1/OWNER-STORAGE-INTERPRETATION-PROTOTYPE-v1.json` | `08255520499267729553d02a9ea83aa7693010803d19ed474e3fe2d825962a5d` |
| `reviews/native-owner-translation-root-v1/report.json` | `306cd296e907441ce9dad405f026f13a64c281e9b65a87a201e0aab5c892156f` |
| `reviews/native-owner-translation-review-v1/REVIEW-EVIDENCE-v1.json` | `53cf4d703ca77edfc04e37e63699b1224c2e997ccafa7c1be196de52eec47604` |
| `NATIVE-OWNER-STORAGE-INTERPRETATION-EVIDENCE-v1.json` | `03a54cfc1348a08d05f69f499121a7f24255dd6594d47e6d22df3a80a45374c7` |

Regenerate and check the interpretation in a fresh directory:

```sh
python3 artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete/native-style-bloom-storage-v1/translation-v1/gate-v1/rebuild.py /tmp/native-owner-storage-interpretation-replay
```

## Native selector fold prototype

The separate `actual-context-v1/native-selector-fold-v1` package connects the
specialized native `any_false` body to the checked native `SelectorIter::next`
body. Its core retains the native `any_value` runtime statements after explicit
`for`-loop lowering. The source audit checks signatures, ghost erasure, the
lowering, the iterator body and the paired conjunction contract.

On normal return, `True` establishes exhaustion of the actual final iterator
through an ordinary component prefix. At the slice boundary the remainder is
empty; at a combinator boundary the combinator has been consumed and recorded
in the final iterator. Every visited component has an independent successful
callback witness. Readiness ranges over ordinary components in the original
remaining slice and history-related callback states. The loop establishes the
no-pending-combinator precondition before every native next call.

Five models pass 77 obligations. A separate fresh Cargo target produces identical
models and passes all 77 again. Four compiled controls corrupt early success,
omit the first result, repeat next after the terminal boundary and remove
callback readiness. Three have one intended timeout each; the repeated-next
control has 79 obligations and two intended timeouts, including the native next
precondition. These are sensitivity checks, not concrete counterexamples.

A separate optimized MIR comparison with debug assertions enabled matches 21
blocks, including normal and unwind edges. It permits the checked next-call
correspondence, block renaming, one goto-only block per side and storage markers
for two non-addressed Copy locals. Review found overly permissive call
normalization and incomplete parser consumption in the initial checker. The
final checker closes both gaps, passes nine rejection controls and has five
additional independent physical controls. This is a bounded compiler-output
comparison, not a verified general MIR equivalence theorem.

Independent contract review also reproduced the collector exactly and checked
the actual-final-iterator postcondition. The prototype has 702 pins; its contract
review has 704. A genuine borrowed iterator is still an entry premise. Unsafe
`HeaderSlice` entry, connected callback execution/final context restoration,
native derived equality, full matcher composition, termination and complete
compiler/Cargo lookup guarding remain open. This is not aggregate acceptance
or completion of milestone 6.

Paths below are relative to `actual-context-v1/native-selector-fold-v1`:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-SELECTOR-FOLD-PROTOTYPE-v1.json` | `17530d4d708bde536906429794f6f84b76a48f83d3f237bf0fedd7ac7b807ea3` |
| `SOURCE-AUDIT-v3.json` | `4a418b53fe580cdeec15764e5e36e8d984d769673d3fd3840092c5748c12272e` |
| `mir-comparison-v1/GRAPH-CHECK-v4.json` | `756b22eba7668991cbc7d07d56d0be41b55f45ad9ebbc9d9f1ae444c9f88e764` |
| `mir-comparison-v1/reviews/source-review-v2/REVIEW-v2.json` | `83e4ac211f4da826d9932651fff9cfd088adeec0c3bf85cf7d7feac16759ed4b` |
| `reviews/contract-review-v1/REVIEW-v1.json` | `68b71a7f5204a4885d88bafe52a22baf6a4a83ad50d4d7bdc28a43fdc01710f5` |
## Native local-name callback prototype

The `actual-context-v1/native-local-name-callback-v1` package checks the full
native simple-selector body under a LocalName-component premise and the native
nesting assertion. Every runtime branch remains present. Checked copies of
`matches_local_name` and `select_name` establish the exact modeled Kleene result;
the simple-selector body also preserves the complete local matching context.
The native context, mutable borrows and dynamic callback field remain present.

Six models pass 112 obligations, reproduced with identical models in a separate
Cargo target. These comprise 101 simple-selector, four local-name, five
name-selection and two boolean-conversion obligations; the two native accessor
models simplify to zero goals. Three compiled controls retain all 112 goals:
wrong name selection leaves three unproved goals, inverted name matching leaves
one and an unexpected context mutation times out at one postcondition. These
are sensitivity checks, not concrete counterexamples.

Independent review reproduced the source audit and rejected five physical
changes to the signature, body, interface contracts, logical model and context
postcondition. Root replay reproduced the complete collector byte-for-byte.
The prototype pins 362 inputs/evidence files; the independent interface review
pins 197. Source auditing compares runtime bodies and signatures, inventories
all proof additions and checks the precise elementary interface contracts.

HTML-document mode and name lookup still rely on explicit Element interface
contracts. Borrow preserves name models and PartialEq agrees with model
equality; concrete Gecko/atom implementations of these laws are not proved.
Namespace bounds and the inherited OpaqueElement model support translation of
excluded branches. Compound/ancestor composition, native equality, termination
and complete compiler/Cargo lookup guarding remain open. This conditional
prototype does not complete milestone 6 or establish aggregate acceptance.

Paths below are relative to `actual-context-v1/native-local-name-callback-v1`:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-LOCAL-NAME-CALLBACK-PROTOTYPE-v1.json` | `0bbbf2218f8bcb1a464a4401c65c062884b033be61c0d15303489f75f2fd74b4` |
| `SOURCE-AUDIT-v1.json` | `e1909e6198dfcbc7a25b5bcf8c7e4217d6151dad2636d1cb975d5a01a83788a9` |
| `reviews/interface-review-v1/REVIEW-v1.json` | `df8cf5826eca9a61665f2380b8ad8511f9f40ed566bf4884b1b28c30330cffdf` |
| `reviews/collector-root-v1/report.json` | `8099beaf3fbbd0667f337e7e5e6f3cc6022f23351ec0d27092ef3ba8efa77f97` |

## Native compound-selector prototype

The `actual-context-v1/native-compound-callback-v1` package connects the native
compound body to the checked local-name/simple-selector callback and specialized
iterator fold. All native runtime branches remain. The declared premises select
LocalName/Combinator input, no pending combinator, a non-featureless context
outside quirks mode and the native nesting condition.

On normal return the complete matching context is restored. A True result
establishes exhaustion of an ordinary prefix of the actual final iterator and
successful modeled local-name matching for each visited component. The fold
requires callback readiness for valid component values and preservation of the
captured state. Its body proves the corresponding loop invariant and final
borrow resolution. No new trusted success contract replaces callback execution.
The fold's runtime statements and previously checked loop lowering are unchanged.

Fourteen models pass 203 obligations; a separate fresh Cargo target reproduces
identical models and all 203 proofs. Three compiled controls each leave the
compound postcondition unproved: immediate success without traversal (201 total
obligations), ignored callback result (203), and context mutation (203). Their
Timeout results establish sensitivity, not concrete counterexamples.

A separate compiler experiment permits callable contracts for exact local
closure types eligible for the existing body translation pass. Eligibility is
not proof completion. Four query controls reject raw/nested dynamic callbacks
and closures under trusted/untranslated parents. Direct, forwarded and nested
dynamic calls, plus a false result, retain unproved obligations. All forty prior
compilation outcomes and emitted models remain identical. A fresh second compiler
build and complete compiler/Cargo lookup guarding are still open.

Independent review reproduced the 10,921-pin collector byte-for-byte and rejected
seven physical source mutations. It checked the complete source reconstruction,
callback state/borrow contracts and compiler eligibility condition. DOM/name
interface laws, native equality, valid borrowed iterator/HeaderSlice entry and
termination remain explicit boundaries. Actual ancestor matching and the
connection to nonempty ancestor Bloom hashes are still required for milestone 6.

Paths below are relative to `actual-context-v1/native-compound-callback-v1`:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-COMPOUND-CALLBACK-PROTOTYPE-v1.json` | `c63be64e3b17ee2675544982760a14662d5648af888221325a18a174af383664` |
| `SOURCE-AUDIT-v2.json` | `9982660378cecf80c5a996ad7f9c30c2aa3adf9a853f343d5c1ffac8b6c4bc8c` |
| `reviews/css-independent-v1/REVIEW.json` | `252b69ce2a7b12043d5d5a5b55fbb504c36e3d90120b9a46830961b17cb415f6` |
| `../../closure-body-v1/CLOSURE-BODY-PROTOTYPE-v1.json` | `e931744ee7a65ebcc36d5984ee006f8845860a09dbd8a5f4a4b86b5de9be3a9f` |

## Native recovery owner composition

The `native-recovery-prophecy-frame-v1` package proves preservation of all four
storage field-reference final values through the native storage mutations,
recovery operations and loops. The native caller then establishes initial/final
recovery witnesses, empty pending work, restored owner observations and an
unchanged atomic borrow guard. These are field-value guarantees; complete borrow
identity is not asserted.

The native evidence contains 126 models per configuration: 1,381 debug and 1,246
release support obligations, plus 289 shared induction obligations counted once.
The sole differing non-Gecko caller adds ten obligations; its other 125 models
are identical. One release recovery timeout at ten seconds is preserved, with
all 235 obligations for that model passing at twenty seconds. Four compiled
controls leave their targeted obligations unproved, and six physical source
controls are rejected. Independent review freshly proved 1,417 selected
obligations and authenticated the remaining evidence.

The `translation-preflight-v1` interpretation connects these native contracts to
the reusable-storage and exact-ancestor-chain results. Its actual helper closure
includes the stronger clear/pop/push frame posts. Separate Lean implications
transport accepted readiness into the stronger interface and actual outcomes
back into the accepted recovery invariants. The caller readiness premise is
derived from reusable storage and explicit DOM/resource premises.

Independent replay reproduced seven Lean modules and their compiled outputs,
32 axiom audits using only standard Lean axioms, and all 66 controls. The typed
binding couples visible record observations without equating the caller's opaque
private carrier with the recovery model's count representation. The previous
parent Lean graph is authenticated rather than rebuilt. A preserved first replay
failed only when Python tuples were compared with JSON lists; the second runner
normalizes that representation before the same exact comparison.

Milestone 4 remains open. These results assume normal return, elementary
library/primitive laws, valid vector/borrow domains, finite ancestry,
identity/common-root properties and capacity bounds. TLS acquisition, automatic
Drop dispatch and termination are not established by this checkpoint.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-recovery-prophecy-frame-v1/checkpoint-v2.json` | `b6d60ad9077bd5ff8e2f48cbecebf9cc593aacc4b80657cbee7640b08697fda7` |
| `reviews/native-prophecy-frame-root-v1/REVIEW-v1.json` | `ff224f3fd4541e91c1da9abf40a1726b3008b3bd550bf856c30b1cd4e23d0dce` |
| `native-recovery-prophecy-frame-v1/translation-preflight-v1/NATIVE-CALLER-FRAME-INTERPRETATION-PROTOTYPE-v1.json` | `5acb8063c2996ee3e2f89b170a34d26013bb62771bb5d2973569d96f222b3742` |
| `reviews/native-caller-frame-root-v2/REVIEW-v1.json` | `0d178c3abd2d5b692539eefa815c6811b914bcc303e13e074d44e1bdbf136c68` |
## Native child matcher and public entry

The `actual-context-v1/native-ancestor-callback-v1` package connects compound
matching to the native recursive matcher and parent-element traversal. All
runtime branches remain, with premises restricting components to local names
and Child combinators. A Matched result establishes name coverage on the current
element or an element in the abstract `ancestor_of` relation; names after a Child
combinator have a witness in that relation. Both native context wrappers restore
the complete context through the recursive callbacks.

The recursive package passes 353 obligations across thirty models. Its
`public-entry-v1` extension checks `matches_complex_selector`, the matching-mode
accessor and result conversion: 377 obligations across 33 models, including
nineteen for the public entry. Separate Cargo targets reproduce identical models
and all positive proofs. The public entry retains the pseudo-element branch and
excludes its mode through an explicit premise. Its iterator call is specialized
to a checked copy of the identical native `Iterator::next` body; recursive clone
specialization remains inherited from the parent package.

Independent review reproduced both collectors, checked recursive/context
semantics and eight additional elementary adapters, and ran seven physical
source controls for each package. Three compiled public-entry controls each leave
the entry postcondition unproved: unchecked success, discarded matching result
and context mutation. Their Timeout results are sensitivity evidence, not
counterexamples. Review authenticates the producer and fresh proof evidence;
it does not claim a third independent solver run.

The relation `ancestor_of` remains abstract. Earlier prototype wording about
strict ancestry describes its intended DOM interpretation, which is not proved
by parent inclusion and transitivity alone. Valid borrowed iterators, elementary
DOM/name/library laws, non-featureless/non-quirks contexts, nesting conditions,
normal return and disabled logging remain explicit. Native HeaderSlice entry,
concrete ancestor/hash correspondence, Bloom composition, termination and full
compiler/Cargo lookup guarding remain open. Milestone 6 is not complete.

Paths below are relative to `actual-context-v1/native-ancestor-callback-v1`:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-ANCESTOR-CALLBACK-PROTOTYPE-v1.json` | `cdd04152849d03ee6c33c04a534a5234680bfbd662ca160d4b62847005b9bbfc` |
| `reviews/source-review-v1/REVIEW-v1.json` | `319a4fe52201517873e92cb1917a8de57c18adc0ac177e4b1642a1ccd8d62ccb` |
| `public-entry-v1/NATIVE-PUBLIC-ENTRY-PROTOTYPE-v1.json` | `cc6e965897fe7c35d63d2f749b065611f52b456623609832903231c56df5379a` |
| `public-entry-v1/reviews/source-review-v1/REVIEW-v1.json` | `65bf931b335ba26550a36ce2e291a0dfb8827b6ab517eeb830e4c0f953f803a9` |

## Native owner clear and readiness

The `native-owner-clear-v1` package checks the unchanged `StyleBloom::clear`
wrapper through its checked storage helper. Its precondition requires valid
record/hash vectors and either a high-water count above the clear threshold or
an exact small-history counter representation. Nine postconditions establish
empty records/hashes, valid vectors, preserved capacities, zero high-water count,
4096 zero counters and an unchanged atomic borrow guard.

Fresh debug and release builds each add one nine-obligation model to the 126
inherited models. Independent review checks that the inherited models differ
only in source-location filenames and freshly proves the eighteen new goals.
Four compiled controls each leave one intended pre/post obligation unproved;
their Unknown results are not counterexamples. Source and correspondence
controls reject physical changes to the checked wrapper and model comparisons.

The `translation-preflight-v1` package interprets the full native pre/post and
connects them to reusable storage. Seven Lean proofs establish exact pre/post
interpretations, clear readiness after recovery, readiness after clearing and
the next clear precondition. Both the bulk-clear and small-history branches are
covered. Composition retains explicit equality between the previous borrow's
final owner and the next borrow's current owner, plus intrinsic borrow validity.
No storage witness or automatic Drop behavior is assumed into existence.

Independent replay reproduces both generated/proof modules and their compiled
outputs, all seven standard-axiom audits, and 32 controls: ten structural, six
binding, ten generated semantic and six canonical/provenance checks. The binding
checks 33 shared owner symbols, 35 count symbols and seven datatype layouts.
The accepted recovery dependency graph is authenticated rather than rebuilt.

Milestone 4 remains open. The next lifecycle step is preservation of owner
observations and clear readiness through the public push/rebuild wrappers.
TLS allocation/borrow identity, release/reacquisition, automatic Drop dispatch,
unwinding and termination remain outside this conditional normal-return result.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-owner-clear-v1/checkpoint-v1.json` | `c63b65d4822c468fa042c975ee7112bd5e82dca9043e56b5b818b84fa749ada7` |
| `reviews/native-owner-clear-root-v1/REVIEW-v1.json` | `fd217300de385cb7ce49fb0565280ed7542957993f555226556ffb74570ecca0` |
| `native-owner-clear-v1/translation-preflight-v1/NATIVE-OWNER-CLEAR-READINESS-PROTOTYPE-v1.json` | `b59c52f1f8fb93abfb570697558ab75bbb11ad956c6b5ffa6d1ef6b76b0c7132` |
| `reviews/native-owner-clear-readiness-root-v1/REVIEW-v1.json` | `10408dda6d76ada02c4647b95126bec190ac6505c6c4cd0080b2717d9d808bba` |

## Reviewed native owner push and rebuild

The `native-owner-mutations-v1` package checks the unchanged `StyleBloom::push`
and `StyleBloom::rebuild` runtime wrappers. Their contracts expose actual
storage/recovery endpoints, preserve the atomic borrow guard and restore owner
field observations after the temporary storage borrow. Rebuild retains the
erased finite-ancestry witness and the existing capacity/readiness premises.

The complete fifteen-conjunct `Storage::push` postcondition is packaged as a
checked module-local predicate. This preserves private record fields and all
six original preconditions. Four original field-prophecy equalities are also
exported directly for callers. The source audit reconstructs the predicate
from the original postconditions and checks the exact runtime bodies.

Each guarded configuration contains 129 models. Five affected models are
freshly proved: forty debug obligations and thirty-five release obligations.
The other 124 models reuse accepted proofs after checking identical declarations
and bodies, with each relocated source range checked against its Rust fragment.
Changing conjunct packaging changes raw goal counts; those counts do not measure
semantic coverage.

Independent review reproduces the checkpoint and reruns eight physical source
and model controls. Five compiled controls are authenticated against their exact
intended failures. The wrong high-water result causes one storage postcondition
timeout and two propagated caller postcondition timeouts. These are sensitivity
checks, not concrete counterexamples or a new Firefox bug.

Milestone 4 remains open. Native-to-Lean mutation interpretation and clear
readiness composition are next. Drop, TLS acquisition/release, unwinding,
termination and native primitive refinement remain separate obligations.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-owner-mutations-v1/checkpoint-v2.json` | `b3af898965be3ffaaee165062eed3f9bdffe8bd874f29b1563a62267aadff885` |
| `reviews/native-owner-mutations-root-v1/REVIEW-v1.json` | `c4a746d5882e0b978e0da5d46f414981057c64a7b8b2655af6fe57459c23ebe7` |

## Native matcher contract to ancestor rejection

The public child-matcher prototype now has a typed Lean interpretation of its
seven selected predicates, including the complete pre/postconditions. The
translation checks 47 types, 105 symbols and thirteen datatype layouts. The
native or-pattern for local names or child combinators preserves its two arms,
branch order and common body. All context fields remain in the generated model.

Eleven lemmas interpret the contracts, relate native local names and iterator
components to the extracted collector, and derive the ancestor witnesses used
by the collector proof. The resulting theorem connects a successful native
matcher postcondition to collection, packing and Bloom rejection, preserving
the whole final context value. It covers the local-name/child-combinator subset.

The fresh gate builds thirty model/proof modules and checks ten structural,
nine generated semantic and three collector semantic controls. Deliberately
changed shape, name selection, ancestor coverage, context restoration and
success conditions fail in their intended lemmas. Independent source review
reproduces the generated bytes and all ten structural controls. The listed
external Lean lookup trees are authenticated before and after the gate;
their libraries are reused rather than rebuilt.

This is a conditional partial-correctness result. It retains explicit iterator
slice correspondence, HTML/name/hash laws, ancestor hash enumeration and valid
filter history. Sequence and borrow carriers interpret the selected observers;
they do not establish all Why3 library axioms. The final theorem retains the
collector's opaque formatter type axiom alongside standard Lean axioms.

Milestone 6 remains open. Next is composition with native provider history and
ancestor enumeration, followed by the remaining iterator representation and
primitive bindings. The raw `HeaderSlice` ownership boundary is not discharged
by assuming a structural slice contract.

Paths below are relative to the public-entry prototype's
`translation-preflight-v1` directory:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-MATCHER-COLLECTOR-PROTOTYPE-v1.json` | `c6bec2c484bbc6f71674d97c777ee2d38fd08ca39185ad9a5aa4c0d99d36f5c5` |

## Reviewed owner mutation interpretation and clear readiness

The native owner push/rebuild contracts now have a checked Lean interpretation.
Three fresh modules provide nineteen standard-only axiom audits. Their typed
bindings check six shared symbol/layout inventories, the complete storage push
pre/postconditions, and the visible record projection without equating its
private carrier with a public count.

The `Stored` invariant combines vector validity, 4096 counters, record/hash
accounting and high-water history. Native owner push preserves it and the
borrow guard. Native rebuild establishes it, empties the pending sequence and
produces the exact ancestor chain. Both establish clear readiness. The next
clear call retains an explicit final-to-current owner endpoint equality and
the next borrow's intrinsic invariant.

Complete push and rebuild preconditions follow from these invariants together
with explicit ancestry, root, intrinsic and resource premises. In particular,
push does not establish rooted ancestry for an arbitrary element, and rebuild
does not assume an unexplained universally ready temporary stack.

Independent source review and a fresh replay pass all nineteen audits and
fifty controls: ten structural, six binding, twelve generated semantic, four
readiness semantic and eighteen canonical/provenance checks. Changed owner
endpoints, root conditions, pending/hash budgets, high-water observations and
field prophecies fail in the intended lemmas. Listed cached dependencies are
authenticated before and after replay; they are not rebuilt.

Milestone 4 remains open. The next connection is an invariant over owner fields
that survives public normal-return mutations and can be established by actual
allocation/borrow acquisition and consumed by destruction. Guard identity must
follow the allocation across threads. TLS reuse, unwinding, termination and
native primitive refinement remain separate obligations.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-owner-mutations-v1/translation-preflight-v1/NATIVE-OWNER-MUTATIONS-INTERPRETATION-PROTOTYPE-v1.json` | `70a172fdbf9ec4010c007878e0f956ca6ff7124df17c2bfe427662e7522892a8` |
| `reviews/native-owner-readiness-root-v1/REVIEW-v1.json` | `5890bc1b757e18036881ff1ecdd04048a22e693812a355013a40454b8337095c` |

## Subject-local shadow premise and native ancestor membership

The child-matcher prototype now requires absence of a shadow-root parent only
for the subject and its ancestors. The earlier global premise excluded unrelated
shadow trees and could not follow merely from a light-DOM subject. Parent
inclusion and transitivity carry the new condition into recursive matching.
The old globally restricted theorem remains unchanged in its frozen package.

An exact source audit permits only this contract change. All runtime bodies
remain unchanged. A fresh native compile produces 33 models and all 377 proof
obligations pass. Three compiled controls remove the subject condition, ancestor
condition or public entry premise. They leave exactly two, one and one intended
call-precondition obligations unproved. Those solver timeouts are sensitivity
results, not counterexamples. Six source controls reject implementation or
contract drift.

The typed export now includes eight predicates, 47 types, 106 symbols and
thirteen datatype layouts. Its canonical audit preserves the original task.
Lean interprets the revised complete pre/postconditions and derives the same
conditional collector rejection result. A finite inductive parent relation
satisfies the parent laws. The actual native `ancestorsFrom` witness establishes
a rooted list containing the subject followed by its collected ancestors;
every inductive ancestor belongs to that list's ancestor portion.

Five fresh modules pass nineteen axiom audits, twenty-two typed controls and
four ancestry controls. The final rejection theorem retains the existing opaque
formatter type axiom; the other audits use only standard Lean axioms. Bounded
independent source review finds no blocker. All listed Lean lookup roots are
authenticated before and after the gate; cached collector/recovery dependencies
are reused.

Milestone 6 remains open. The parent interpretation still needs its concrete
Gecko observer binding. Native policy/name hashing, iterator representation and
the identity between recovered filter storage and `MatchingContext.bloom_filter`
remain explicit connections. No native completion or whole-selector claim is
made.

Paths below are relative to the public-entry prototype's `subject-ancestry-v1`:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-SUBJECT-ANCESTRY-PROTOTYPE-v1.json` | `b81c6bf3e797d2b8caeb11c8bbf16d888c80c44e3dfb58ec1fc492e5a9f1215c` |
| `reviews/source-review-v1/check-v2/REVIEW-v1.json` | `f422efa314e45b92b1edbb18e57c9df6769b1a7be14463d56dcdb3215ebbd40a` |
| `translation-preflight-v1/SUBJECT-ANCESTRY-INTERPRETATION-PROTOTYPE-v1.json` | `69f535a17e74c6442d445097c1e41dd58da98cdb6e511b4cbcb745bb357d626e` |

## Reviewed direct owner invariant

The lifecycle prototype now states its invariant directly over the owner's
filter, element vector, hash vector and high-water observations. It includes
vector validity, 4096 counters, contribution accounting and insertion/removal
history. Establishing it does not require inventing a temporary `Storage`
reference. An observation lemma transfers it to genuine storage values returned
by the native contracts.

Ten lemmas establish initialization from supplied zero/empty observations,
derive clear readiness, and prove preservation by the exported normal-return
clear, push, rebuild and recover postconditions. Recovery handles all four
native outcomes. This invariant does not include rooted ancestry; matching
retains that separate requirement.

Independent source review and fresh replay pass all ten standard-only axiom
audits and seven semantic controls. Changed initial counters/high-water values,
missing initial invariants and incorrect current/final endpoints fail in their
intended lemmas. Listed parent dependencies are authenticated before and after
replay without rebuilding them.

Milestone 4 remains open. Actual construction must establish the supplied
zero/empty facts, and automatic destruction must consume the maintained
invariant. Preserving an opaque guard value does not by itself prove its
allocation identity. The connection between the borrow counter, filter storage,
acquisition and release still needs refinement, including cross-thread release.
TLS reuse, unwind behavior and termination remain open.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-owner-mutations-v1/lifecycle-observations-v1/OWNER-INVARIANT-PROTOTYPE-v1.json` | `2f01243a17ddd3e4f0fe962fb16bb7afec3615cdde40ee41c98b439011052ed0` |
| `reviews/native-owner-invariant-root-v1/REVIEW-v1.json` | `210bbf9cf7c19034793eea4c30490c50c1740089bc0447fa2228c30a4120769e` |

## Conditional native construction and Drop body

The native lifecycle prototype checks the exact constructor tail after
`BLOOM_KEY.with` supplies an owned guard, plus the exact `self.clear()` Drop
body exposed as a named adapter. The constructor preserves the supplied guard
and establishes empty valid vectors, their inline capacities, zero high-water
state and a zeroed 4096-counter filter. Its input-zero requirement is explicit
in both configurations; the release proof does not rely on `debug_assert!`.

Paired contracts check the actual `SmallVec::default` and `AtomicRefMut::deref`
bodies. The concrete Bloom default uses the explicit specialization of its
one-field derived constructor. Both configurations compile 135 models; 129
inherited bodies are authenticated unchanged. Six new models pass twenty debug
and sixteen release obligations. Four compiled mutations fail their intended
obligations, and six physical controls reject source or contract drift. The
compiled failures are solver sensitivity results, not concrete counterexamples.

Independent review reproduces the checkpoint collector, both native compiles,
all thirty-six new obligations and the six physical controls. Original compiled
mutation evidence is authenticated and reviewed without a second solver replay.
Milestone 4 remains open: supplying the owned zero guard does not verify TLS
acquisition, and checking a named Drop body does not verify automatic destruction.
Allocation identity, the borrow-counter/payload connection, unwinding and
completion remain separate obligations. The next experiment uses explicit
permission tokens and Acquire/Release synchronization to represent that protocol.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-owner-lifecycle-v1/checkpoint-v2.json` | `b8aaa893c95045c78cc40c25497df86bf90a80bb3a78e65d21e3a93f93b39ee9` |
| `reviews/native-owner-lifecycle-root-review-v1/REVIEW-v1.json` | `8cf6045fd287b14553889f597d7813eee4058cd30abf0c39588a1e28b27b002c` |

## Recovery to native matcher composition

The composition now derives rooted ancestry from the complete native recovery
pre/postconditions, then uses the native matcher pre/postconditions to establish
that collection, packing and querying the recovered final filter cannot reject
a successful local-name/Child match. Initial validity/history, primitive and
sequence laws, hash policy and iterator correspondence remain explicit premises.
The query endpoint is the final recovered storage.

Three fresh modules pass three axiom audits and four qualified semantic controls.
Missing initial history or rootedness, the wrong rooted-chain endpoint and a
different matching subject fail their intended lemmas. A direct query-endpoint
mutation reached elaboration or diagnostic resource limits and is not counted.
The final query results retain the existing opaque formatter type axiom.
Independent bounded source review passes, and a surrounding gate authenticates
all listed Lean lookup trees and evidence inputs before and after fresh builds
and controls. Parent dependencies are reused without rebuilding them.

The concrete Gecko source check identifies a required refinement: recovery calls
`traversal_parent`, which follows the flattened tree, while matching calls
`parent_element`, which follows DOM parents. This prototype uses one parent
relation and therefore cannot directly instantiate both Gecko observers when
slotting changes the chain. Absence of shadow-root parents on the matching
ancestry alone does not establish their equality. The next composition must
carry an explicit inclusion of matching ancestry in traversal ancestry.

Milestone 6 remains open. Concrete parent relations, atom/hash correspondence,
iterator ownership, and the identity between the recovered filter and the
matching context still need checked bindings. The source check confirms the
style resolver forwards `StyleBloom::filter()` into the matching context, but
that observation alone does not prove the allocation correspondence.

Paths below are relative to the public-entry prototype:

| Record | SHA-256 |
| --- | --- |
| `subject-ancestry-v1/translation-preflight-v1/native-composition-v1/RECOVERY-MATCHER-PROTOTYPE-v2.json` | `b5401ccb98b226f57aafb7b00f8f57ad062e7b84b2a671cd253d5a551819086d` |
| `provider-bindings-v1/SOURCE-CONNECTIONS-v1.json` | `7611a2ab5fc2fa55409c068c70993af512eb2e29ef46b134d37f2b1a8b5d41d0` |

## Distinct matching and traversal parent relations

The new composition permits different matching and recovery parent functions.
For every matching-parent edge on the subject's matching ancestry, an explicit
premise supplies a nonempty path in traversal ancestry. Induction lifts the
matching ancestor relation through those paths. Rootedness of the recovered
traversal chain then establishes membership for every matched ancestor.

The provider and recovery composition retain the complete native contracts,
initial state premises and final recovered-filter query. They now consume this
edge embedding instead of identifying the two parent functions. An equality
lemma covers callers whose parent functions agree on the relevant ancestry.
A finite example has different subject parents, with an intermediate slot node
in the traversal chain, and proves that all matching ancestors are retained.
This is a relational example, not a proof of Gecko slot assignment.

Four fresh modules pass nine axiom audits and four strict semantic controls.
Missing or reversed embedding, the wrong rooted parent relation and exclusion
of the subject from the embedding domain fail their intended proof sites.
The latter mutation produces errors in both the lifting and equality lemmas;
the gate requires both. The three generic bridge/composition modules pass
independent source review. A surrounding gate authenticates every listed Lean
lookup tree and evidence input before and after fresh builds and controls.
The final query theorems retain the existing formatter type axiom.

Milestone 6 remains open. The next concrete topology obligation must establish
the edge embedding for Gecko's actual caller domain, including slot, shadow and
native-anonymous branches. Atom/hash policy, iterator representation and filter
allocation identity remain separate bindings. The checked relation avoids an
unsupported parent-equality assumption without claiming those bindings are done.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1/parent-relations-v1`:

| Record | SHA-256 |
| --- | --- |
| `PARENT-EMBEDDING-PROTOTYPE-v1.json` | `bbf7cfa95b5d236d151b12dd8d98ec598d56ea1ad93c6c417b93839f12ce881b` |
| `reviews/source-review-v1/REVIEW-v1.json` | `5ae8cd996c83c1884a92981da906c8398860c5d7d8eadcc5f99918daabb95d85` |
## Constructor and Drop contract interpretation

The exact native constructor-tail and named Drop-body contracts now have a
checked typed Lean interpretation. The constructor postcondition establishes
the direct owner invariant, preserves the supplied atomic field and establishes
inline capacities of sixteen element records and sixty-four hashes. The full
Drop-body precondition is definitionally the accepted clear precondition; the
maintained owner invariant supplies it together with the existing intrinsic
premise. The Drop postcondition establishes zero counters and guard preservation.
It does not establish a final vector reuse invariant.

Two fresh modules pass six standard-only axiom audits and thirty-four controls:
seven semantic, fifteen structural/binding and twelve native export checks.
The bindings retain the shared observer, layout and intrinsic closures and keep
private record carriers opaque. Independent bounded source review reproduces
the generator byte-for-byte and the binding audit. Independent capsule collection
reproduces the same digest; that collection authenticates the recorded proof
outputs and dependency closure without rerunning the solver or all Lean builds.
The original gate authenticates listed cached dependencies before and after its
fresh modules and controls.

Milestone 4 remains open. Construction still begins with an acquired zero guard,
and automatic destruction is not implied by a named Drop-body adapter. Native
allocation identity, the stored mutable reference, the atomic borrow counter,
TLS acquisition/release, unwinding and completion remain separate connections.
The permission experiment is evaluating those native primitive boundaries.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-owner-lifecycle-v1/translation-preflight-v1/OWNER-LIFECYCLE-INTERPRETATION-PROTOTYPE-v1.json` | `f785e5f122851981582ae6b865e8dcbe40110cf59ec9b83c583b93fa54b5583b` |
| `native-owner-lifecycle-v1/translation-preflight-v1/reviews/root-source-v1/REVIEW-v1.json` | `da593b37de6f811196985b864dcd6b9341da7e3f834142632fd6abab05da466b` |

## Gecko style-parent observations and caller boundary

A manually transcribed observation model now follows the complete C++
`GetFlattenedTreeParentNode` branch order specialized to `eForStyle`. It derives
the element-parent formula, including document-level native anonymous content,
assigned slots and inactive fallback. Conditional edge retention supplies the
previous matching-to-traversal ancestry embedding. Its cut exclusions and
assigned-slot ancestor paths remain explicit requirements.

Abstract countermodels show why DOM-parent retention cannot be assumed globally.
The unassigned-child and document-level anonymous examples have no shadow-root
DOM parents; inactive fallback explicitly has a shadow boundary in its ancestry.
These are abstract observation assignments, not constructed native DOMs or new
browser bug reproductions.

The ordinary flattened-parent model also distinguishes the computed-style
caller's `IsInFlatTree` check from style traversal. Ordinary connectivity to a
document does not exclude the style-specific anonymous-content cut. The native
loop, its `HasServoData` shortcut and the actual caller domain remain unproved.

Four fresh modules pass fifteen standard-only axiom audits and six strict
semantic controls. Independent bounded source review checks all four modules
against the native branch order. The gate authenticates all listed Lean lookup
roots and evidence inputs before and after fresh builds and controls. The source
map pins the native bodies and their manual correspondence; it is not C++
extraction or verification. The separate Rust fast-path experiment is excluded
from this checkpoint.

Milestone 6 remains open. Native observer meanings, DOM structure and slot-path
invariants, caller eligibility and the Rust fast-path connection still need
bindings. Atom/hash policy, iterator representation and recovered-filter
allocation identity remain separate obligations. The next work connects the
native fast-path body and identifies sufficient conditions at actual callers.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1/gecko-parent-v1`:

| Record | SHA-256 |
| --- | --- |
| `GECKO-PARENT-OBSERVATIONS-v1.json` | `acd9937ac8c6efe050c3f9cc1a64a3c8c1b667dd1e8a1f7e53641634e30bf3b8` |
| `reviews/source-review-v1/REVIEW-v1.json` | `9214bfa16042c2a075e66344dd630453e93fdfbdbc0b7a13265715659570c5e3` |

## Implicit guard cleanup verifier defect

The native permission investigation found a pinned Creusot cleanup defect. A
small program writes one through a zero-guarded mutable reference, exits its
scope and asserts zero. Both proof obligations pass, but ordinary execution
fails the assertion. Independent fresh dependency compilation, solver replay
and identical-source runtime execution reproduce the mismatch. Explicit drop
exposes the missing guard-invariant requirement. See
[the finding](GUARDED-DROP-FINDING.md) for the reproducer, controls and evidence.

Milestone 4 remains open. Implicit `Guarded` cleanup cannot justify the proposed
stored-reference loan route. A bounded native source scan found no direct uses
of the implicated APIs; emitted-model and indirect-library impact remains under
review. The experimental `Guarded<FullBorrow>` protocol needs separate review.
An isolated compiler correction must preserve the failing invariant controls
before this route can be used. No accepted compiler or proof package is changed.

## Native Gecko parent fast-path interpretation

The unchanged Rust `flattened_tree_parent_is_parent` body now has a conditional
proof under stable node and element observer contracts. All twenty obligations
pass. Three compiled controls remove the anonymous-root test, remove the slot
test or change the root observer contract; they leave exactly one, one and two
intended postcondition obligations unproved.

The typed export retains the complete pre/postconditions and fast-path predicate.
Its audit preserves all twelve original roots and the original task's 294
declarations and 639 identities. Three exported definitions use six types,
twenty symbols and three datatype layouts. The generated Lean interpretation
connects the successful native postcondition to the manually transcribed
Gecko style-parent model and derives retention of the supplied element-parent
edge under its structural and root-meaning premises.

The binding keeps the associated Element carrier distinct and relates each
root, slot and shadow observation explicitly. The word carrier, zero, bitwise
operation and mask remain opaque observations, connected through the exact
native-root bit predicate. This does not interpret the full Why3 arithmetic
axioms or establish raw node representation or flag stability.

The guarded replay checks the native positive and three compiled controls, then
builds three fresh Lean modules with four standard-only axiom audits. Three
semantic and four schema controls pass. Independent bounded source review covers
the exact runtime body, typed generator, complete observer binding and proof
statements, and reproduces the export/source audits and targeted rejection
checks. Listed Lean/Why3 lookup roots are authenticated before and after replay.
Rust compilation and all compiler dependencies are not freshly rebuilt by this
gate. The first gate pinned a different Z3 executable; the accepted second gate
pins the actual configured solver.

Milestone 6 remains open. The C++ model is still a manual transcription; native
observer correspondence, the Relaxed flags snapshot, root meaning and caller
eligibility remain explicit. This fast-path result does not discharge slot or
shadow slow paths, all matching ancestry, or filter allocation identity.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1/gecko-parent-v1/rust-fast-path-v1/native-body-v1`:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-FAST-PARENT-INTERPRETATION-v1.json` | `f221cd3dac8b7db3a715cd82b1cbbf27ff16bf045dfd801f9d5607c34ac93003` |

The independent review is relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `reviews/gecko-fast-parent-review-v2/REVIEW-v1.json` | `1136e6100b0917aa2cd698604dc8ccab450a5976f415e8fb473fc4fe031f6c61` |

## Guarded emitted-model impact scan

The independent replay of the bounded Guarded impact scan matches the recorded
report byte for byte: SHA-256
`f11db1fa7e1d395bb923f16554067d63c74349db7aea86d46b05eb7225d3d90a`.
It authenticates 15,746 model paths with 10,397 distinct file hashes from
16 direct native checkpoint manifests, including positive and control copies.
None contains `Guarded`, `NonAtomicInvariant` or `guarded`. The report is
`reviews/guarded-implicit-drop-root-v1/IMPACT-MODEL-COLLECTION.json` under
`artifacts/stylo-bloom-tools/creusot-gate/provider-state/native-storage-pop-concrete`.

This text scan does not prove absence of indirect compiler defects or cover all
accepted artifacts. The separate permission protocol uses `Guarded<FullBorrow>`
and remains subject to further review. Compiler corrections are experimental;
no replacement compiler or native lifecycle acceptance follows from this scan.

## Native Gecko root observer interpretation

The conditional root-observer prototype is frozen at
`NATIVE-ROOT-INTERPRETATION-v1.json`, SHA-256
`de649a8649ab90a61ea4a460241b83ce1c4fc01232d8a6de4f22febabc775977`,
with 15,036 authenticated file entries. Its directory is
`native-body-v1/native-root-v1` under the existing
`gecko-parent-v1/rust-fast-path-v1` experiment.

The fixture copies the Rust `GeckoElement::is_root` and
`GeckoNode::is_in_document` bodies, including the debug assertion and closure.
Fresh compilation produces four models, and all 18 obligations pass under
stable observer contracts and an explicit debug-readiness premise. The C++
`Gecko_IsRootElement` equality is source-authenticated and represented by a
manual generic adapter; this is not a C++ extraction proof.

Four compiled controls remove either early guard, remove debug readiness, or
replace the FFI observer contract with an always-true result. They leave two,
two, one and one intended obligations unproved, respectively; every unrelated
obligation passes. These solver rejections are sensitivity checks, not Firefox
runtime counterexamples.

The typed export retains four actual definitions: debug readiness, the root
result, and exact native pre/post predicates. Appending the two exported
predicates preserves all nine original roots and the selected task's
82 declarations and 155 identities. Two fresh Lean modules pass three
standard-only axiom audits. Four schema controls and three semantic controls
pass; each semantic mutation first compiles its generated module and then
fails at the intended bridge lemma. Independent review reproduces both Lean
modules and the source/export audit without repeating the native solver run.

The new bridge derives the earlier `rootMeaning` premise using explicit
element projection/injectivity, document-root observations, parent/child
owner-document agreement, root flags, document-parent topology, receiver
validity and the checked native root contract. It then composes with the
existing native fast-parent theorem. These native DOM connections remain
premises. Raw pointer validity, flag layout, cache maintenance, bind/unbind
behavior, concurrent mutation, caller eligibility and the manual C++ parent
interpretation remain outside this proof. Milestones 4 and 6 stay open.

The collection report is `COLLECTION-v3.json`, SHA-256
`cb102d454d1ef1d559b336833a3fe1eabd1e9a20606459098e4c74724e56da7a`.
It authenticates recorded native model/raw-goal inventories, checked Lean
sources and resolved imports, and inherited listed lookup roots before and
after collection. It does not repeat compilation or proofs or inventory every
compiler input. The bounded independent review is
`reviews/native-root-review-v1/REVIEW.json`, SHA-256
`9dc5728c0d28d712724132a3448abb45240564d0212f0f899ed3fd591bf88098`.
Existing accepted compiler binaries and earlier capsules are unchanged.

## Restricted guard restoration diagnostic

Independent review now reproduces the restricted permission-protocol evidence
collector byte for byte and regenerates all thirteen transformed COMA models.
The fixed-program gate covers six models and ten bodies, with fifteen physical
integrity controls and four handwritten Lean restoration lemmas. It enforces an
exact reviewed program; it does not admit arbitrary clients or establish a
general compiler correction.

The diagnostic removes the projected future Guarded assumption, weakens the
entry and Ghost contracts to current-state invariants, and checks the outer
current invariant before resolution. It retains the actual projection,
reborrow and permission-call transitions. No stronger entry assumption is
introduced. The original complete guard check before resolution still leaves
two obligations unproved.

A separate variant checks current guard restoration before resolution and the
complete current/final guard relation afterward. Independent local solver
replay proves all 32 obligations. Removing the cell's final-permission ward
guarantee leaves four obligations unproved: the current restoration check,
both post-resolution ward checks, and the outer current guard check. All other
28 obligations pass. These timeouts show sensitivity, not counterexamples.

This is a transformed verification-condition result, not a source-preserved
native proof. The handwritten Lean endpoint model remains separate. Existing
permission, lifetime, Ghost and atomic primitives remain trusted; replacement
and escaped-reference provenance, primitive-cache provenance, native
AtomicRefCell, automatic Drop and TLS are not established. Milestone 4 remains
open. The general Guarded correction is outside this restricted experiment;
the preserved verifier reproducer remains an independent tool limitation.

Paths below are relative to `provider-state/native-storage-pop-concrete`:

| Record | SHA-256 |
| --- | --- |
| `native-owner-lifecycle-v1/native-permission-boundary-v1/protocol-fragment-v1/evidence-v1/RESTRICTED-PROTOCOL-CANDIDATE-v1.json` | `6eaf45306a42b1ea8cba4cee0cfab51b6f04b47bd00c751b6c1d8dfd887e7917` |
| `reviews/restricted-protocol-root-v1/REVIEW-v1.json` | `5f2e1f19b06d442fd6cccdfd9bd42b6a51687d9eefb55a35c65308946d1462f7` |

## Native matching-context constructor interpretation

The copied `MatchingContext::new_internal` and `new_for_visited` bodies now
establish preservation of the supplied optional Bloom filter value and final
mutable selector-cache observation. Their runtime statements are unchanged
apart from qualifying the extracted constructor and callee names. The native
quirks-mode helper is separately copied and proved against its external
contract. All eleven obligations across the three models pass.

Three compiled controls discard the filter, confuse current and final cache
observations, or change the quirks helper. They leave one, two and two intended
obligations unproved, respectively, with every unrelated obligation passing.
The cache control affects both constructor postconditions. These are solver
sensitivity checks, not Firefox runtime failures.

The typed exports retain the full constructor pre/postconditions and preserve
the original verification tasks. A fixed-point layout inventory records each
export's 23 types, 57 functions and fourteen layouts. The generated context
keeps all eighteen fields, including the dynamic callback, associated data and
mutable cache borrow. The bridge to the accepted matcher record preserves the
cache's current value, final value and identity separately.

Four fresh Lean modules pass fourteen axiom-free theorem audits. The gate also
replays six canonical/typed exports and checks ten schema, four binding, two
canonical and eight compiled semantic controls. Independent source review
rebuilds all four modules, reproduces the export audit, and rejects two further
borrow-layout mutations. The complete listed Lean/Why3 lookup inventories are
authenticated before and after the producer gate. Native compilation/proof
records are authenticated; this gate does not rebuild their toolchains.

The resulting observation theorem transports a supplied filter query through
construction into the matcher record. Preservation of the mutable context's
Bloom field between construction and use remains an explicit premise. The
native owner getter, its filter representation binding, caller frames, DOM
stability and allocation identity are separate obligations. Milestones 4 and 6
remain open.

The accepted snapshot collector checks exact relative output paths, including
nested reports. Four physical controls reject missing, altered and unexpected
outputs and a forged report. Its independently reproduced collection is
byte-identical. The initial collector, which excluded every file named
`report.json`, is preserved and superseded.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1/context-filter-v1`:

| Record | SHA-256 |
| --- | --- |
| `NATIVE-CONSTRUCTORS-v1.json` | `8244f0934c91ccb8da12e05d183979587490700ac02898e4d674c79d94cc37d4` |
| `translation-v1/CONTEXT-CONSTRUCTOR-INTERPRETATION-v2.json` | `e12e9014b33858005b80cea9e08659052f4e2397a047af3eccc570af0b71db8e` |
| `reviews/root-constructor-v1/REVIEW-v1.json` | `34db2619f82f601b3271f559ae7cd8fc232e09ea1a90bc102f2c778c1ad2be08` |

## Native filter getter interpretation

The copied `StyleBloom::filter` body establishes that its shared result equals
its owner's current guarded filter value. Native proof records contain three
getter obligations and one shared-guard helper obligation. Controls selecting
the future value or removing the shared-dereference guarantee each leave the
intended getter postcondition unproved. These are solver sensitivity checks.

The selected typed export preserves the full owner intrinsic precondition and
the result intrinsic plus current-value equality postcondition. All four owner
fields and the guard's current value, final value and borrow identity remain
represented. Layout correspondence is checked against the independently
accepted owner-constructor export; this does not jointly interpret the entire
owner invariant dictionary.

Seven fresh Lean modules pass 21 axiom-free theorem audits, including fourteen
inherited constructor audits. The producer gate records eight schema, four
binding, two canonical and seven compiled semantic controls, plus three exact
exporter replays. Four physical controls protect its output inventory.
Independent review authenticates the frozen inputs and listed lookup roots,
reproduces the collector byte for byte, checks the export audit, and rebuilds
all seven modules with isolated imports and warnings treated as errors. Native
compiler/prover records are authenticated rather than rebuilt by this review.

The bridge transports the current owner filter through context construction to
a matcher query under explicit representation, query-alignment and later
context-field preservation premises. Those premises remain open. Storage
identity, allocation identity, automatic cleanup and TLS ownership are not
established. Milestones 4 and 6 remain open; the next work connects the concrete
query implementation and native caller frames.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `filter-getter-v1/NATIVE-GETTER-v1.json` | `c176d2fb04656c74e47369ec63fca5890c22c90a4892bbf4c0ea66cabed00956` |
| `filter-getter-translation-v1/FILTER-GETTER-INTERPRETATION-v1.json` | `68c878c7e3d680e7365855e717bd392677a1cfce009bc506a9f5c752835d7ad5` |
| `reviews/getter-root-v1/REVIEW-v1.json` | `a32efa6c684e5fc07cef966e62eae4c62f20f72e9bce00ab0c8d25d6109126cf` |

## Native filter query and actual selectors storage

The native query path now has a concrete byte-counter contract in both the
copied owner fixture and an isolated fixture using the actual imported
selectors `BloomFilter` and `BloomStorageU8` types. Eight query/index runtime
bodies are checked against source. The actual-type fixture specializes the
storage receiver and qualifies checked free helpers; its dependency fork
changes only the visibility of the storage and counter fields. The copied
verification library changes only its selectors dependency path.

The owner fixture adds six models with 51 proved obligations. All 136 inherited
models remain byte-identical after exact insertion-only source-line and path
relocation. Three compiled controls change conjunction to disjunction, use the
first slot for the second query, or invert the empty-slot test. Each leaves two
intended postcondition obligations unproved, with every unrelated obligation
passing. An initial array-bound timeout is preserved; enabling the existing
bit-vector proof mode resolves it without changing runtime code or premises.

The actual-type fixture freshly compiles its Cargo dependencies and proves all
58 obligations across ten emitted models. Its conjunction-to-disjunction
control produces 59 obligations: two intended query postconditions time out
and the other 57 pass. These controls are solver sensitivity checks, not
browser counterexamples.

Independent review added checks omitted by the initial body audit: all three
constants, all eight full receiver/argument/result signatures, and exact
bijections between compiled models and selected proof roots. Twenty physical
controls exercise those checks. Root review reproduces those controls and the
review collector byte for byte. Native proof records are authenticated rather
than replayed by this review; no complete compiler lookup closure is claimed.

The concrete COMA records expose both the filter storage and its byte array.
Typed Lean interpretation, the external native query contract, packed ancestor
queries, caller frames and allocation identity remain separate obligations.
Milestones 4 and 6 remain open.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `filter-query-v1/NATIVE-QUERY-v1.json` | `4a3f34748f371974a134ced6442f4bba5aec0fd1384dcd1e673d26d1f9a92827` |
| `filter-query-actual-v1/ACTUAL-QUERY-v1.json` | `6d5b985d256f27e4647d3124defd488ca479e6c17a89779215aced07846f3f7c` |
| `filter-query-review-v2/REVIEW-EVIDENCE-v1.json` | `a7feb46e3ab12822bc889130a9f8e84e3915926f87ae3605abea29a61ffc1f39` |
| `reviews/query-review-root-v1/REVIEW-v1.json` | `778eae8aa408c6e387248809d597d41ef244a5bbf76cbd0d6c6fed971492e4c3` |
## Concrete query interpretation and ancestor lookup

The selected full owner and actual-type query contracts now have a typed Lean
interpretation. Concrete filter/storage records preserve the counter-array
carrier and its sequence observation. A shared primitive dictionary gives both
sides the same bitwise operations, width conversions, mask, array view and
sequence lookup. The getter's storage carrier is specialized to that record,
and its current-value postcondition supplies query readiness and alignment.

The producer builds twelve modules with 34 axiom-free audits, including thirteen
new audits. Six canonical/typed exporter replays and nineteen schema, binding,
canonical and semantic controls pass. Four physical controls protect the exact
237-file output inventory. Independent review rebuilds the five new modules
against seven authenticated inherited modules, reproducing their source,
object and diagnostic bytes. Root review reproduces its frozen collector.
This interprets selected contracts under common primitive and intrinsic
dictionaries; it does not interpret the entire native array/invariant library,
identify allocations, or discharge the later mutable context-field frame.

A separate native ancestor-query fixture retains the actual imported
`AncestorHashes` and `BloomFilter` types. The complete `fourth_hash`, `may_match`
and `selector_may_match` runtime bodies are checked against source, with only
receiver/callee qualification and a proof-only loop invariant. The original
array iteration remains, using the previously checked borrowed-array iterator
contract. All 105 obligations across thirteen models pass, including fresh
checks of the ten inherited query models.

Four compiled controls change the zero sentinel, fourth query, fourth-hash shift
or forwarding result. They leave one, two, one and two intended postconditions
unproved, respectively; every unrelated obligation passes. Root source review
reproduces both the ancestor and conditional Rule-helper collectors, and all
six physical ancestor-source controls. Raw native solver evidence is
authenticated by that review; it is not a new solver run.

The Rule helper still has its separately recorded uncontracted-query failure.
Connecting the checked query to that caller is a new experiment. Packed-hash
construction, native selector-borrow readiness, operational loop correspondence,
complete caller semantics and aggregate composition remain open. Milestones 4
and 6 are not complete.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `filter-query-translation-v1/FILTER-QUERY-INTERPRETATION-v1.json` | `56457b0d7397ecbda33000039fc1cef95a9d02b9aac6a735c74b25a4eeb6f9b0` |
| `filter-query-translation-review-v1/REVIEW-EVIDENCE-v1.json` | `55e87424f7863cb3c5ff420c02481fcce2b66178601c624539efe25fc0e2c532` |
| `ancestor-query-v1/ANCESTOR-QUERY-PROTOTYPE-v1.json` | `1823e72f2c4dab9f05b59eee8945f785c9385e4f7cc1e131a9b86500f37841c4` |
| `reviews/ancestor-rule-root-v1/replay-v2/REVIEW-v2.json` | `ce7f4d7102009a75a2a88a5caa4568862e5112f2738d83f37d8811d44dfd1ae0` |

## Conditional native Rule context preservation

The Rule fixture now calls the checked ancestor-query module. Its runtime body
and contracts are unchanged; the integration changes only the query import,
module registration and two dependency paths selecting concrete Bloom storage.
The exact source union and all 53 emitted models are authenticated. All thirteen
caller obligations pass, closing the earlier query-callback readiness failure.

Every inherited matcher model is freshly checked with the concrete storage
layout. The initial run proves 548 of 549 obligations. One context-wrapper
precondition still times out with a larger limit. Independent investigation
finds that a second standard `split_vc` pass proves the unchanged model in 179
obligations. This replaces that model's original 87 obligations: complete
selected coverage is 641 obligations across 53 models, with one proof strategy
per model. Seven models have explicitly empty proof-goal lists.

Restoring the unsupported query call leaves one callback-readiness obligation
unproved. Clearing the context's Bloom field leaves two context-postcondition
obligations unproved. Every other selected caller obligation passes. Six
physical source controls reject changes to the module, import, frame, query,
dependency and source inventory. Independent review reproduces the complete
collector byte for byte and reruns those controls. Commands, proof roots,
control spans and the removed unsupported-query warning are checked exactly.

The subject-loop lowering also has a bounded operational comparison. All 25
executable blocks match after one original goto block is removed; two promoted
constants match exactly. The checker compares all remaining statements, types,
branches and unwind behavior. Its narrow normalization of exclusive iterator
references and an unused shared-reference payload has a manual justification.
Root review reproduces the collector and fifteen rejection controls. This is
not a general MIR or Rust memory-model theorem; valid selector borrowing and
cached compiler/dependency behavior remain premises.

This result establishes complete context preservation under the existing
local-name/child selector domain, selector-access and parent/primitive contracts.
It does not establish the Full bucket shortcut's meaning, actual HeaderSlice
ownership, packed-hash construction or the complete no-false-rejection result.
The next gate connects the actual query argument at caller entry to the
accepted getter/context/query interpretation. The proved return-state frame
cannot alone identify the intermediate query or matcher-call state. Export
those observations with explicit endpoints. Milestones 4 and 6 remain open.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `rule-query-integration-v1/NATIVE-RULE-QUERY-v1.json` | `22a04a061041d7788a2be1e720ed16f1eacdb7089fc87420160630cffca934e0` |
| `rule-query-integration-review-v1/full-review-v1/REVIEW-v1.json` | `b2f53d889e27b1d0c122e4234c7fb7db5c23b25c1fcfa7a609d187b1755190c9` |
| `caller-field-frame-v1/native-wrapper-v1/mir-lowering-v1/MIR-LOWERING-PROTOTYPE-v1.json` | `738af110b179f9be667b10c011f7eb905e3e219242883be26c70a08ea05d00ed` |
| `reviews/mir-root-v1/replay-v1/REVIEW-v1.json` | `e95c8b14c0bcc0eeef3057c5293d1b643c82ada56174c1d5ad586f792a799781` |

## Rule query at entry and concrete word interpretation

The caller's complete contracts and initial query observations now have a typed
Lean interpretation. All Rule fields, eighteen context fields, cache fields and
borrow endpoints are retained. The entry observation reads the current Bloom
field and captures the Rule's actual hashes. The Option result and closure
negation derive acceptance of the generated packed-query predicate. The return
frame is separate and is not used to identify the entry state.

Distinct concrete integer and bit-vector dictionaries agree on masking,
shifting, the first and second Bloom indices and packed fourth-hash construction.
Their standalone checkpoint has 25 theorem audits, seven compiled operation
controls and six metadata controls. The integer library leaves some operations
underconstrained: these are chosen interpretations, not a theorem about every
model of that library. The bounded shift conversion does not rely on unspecified
out-of-range conversion behavior.

The composed entry package freshly checks twenty modules with 95 theorem audits,
including 36 new entry, query, owner and constructor lemmas. Six canonical/typed
exporter executions reproduce the selected exports, and regenerated Lean matches
the pinned source. Eight compiled semantic controls reject wrong operations,
indices, counter observations, packed shifts, query conjunctions and state
endpoints. Only standard `propext` and `Quot.sound` axioms occur. A separate
runner revision rejects resource exhaustion and unrelated compiler diagnostics
as evidence of semantic rejection; five parser controls check that distinction.

Independent review repeats the twenty-module proof and checks the complete
original task/theory prefixes, contract capture and initial COMA call sequence.
Thirteen source/observer controls and five validator controls pass. A supplement
binds the caller's opaque observers to the checked packed helpers by exact
source origins, signatures and layouts. It checks the native mask initializer
with four axiom-free calculations and twelve binding controls, and reproduces
the guarded collector byte for byte. Native solver records and previously built
exporters are authenticated; this is not a new native solver or compiler run.

The result connects the entry query to the getter's current owner filter under
an explicit constructor-to-entry field frame and the Option call's normal-return
postcondition. The call-site interpretation is a bounded manual operational
argument, not a general COMA semantics theorem. Complete array/intrinsic library
interpretation, allocation identity, native selector ownership and actual
collector/packing and recovery composition remain open. The next experiment
connects the selected counter observations to the existing valid-history result,
then derives packed-query acceptance from actual collected ancestor hashes.
Milestones 4 and 6 remain open.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `query-word-interpretation-v1/QUERY-WORD-INTERPRETATION-v1.json` | `c4860c98e472c5ced2580428a7639b2701c15303e4114323c4b02dc008e82caf` |
| `rule-query-entry-v1/QUERY-ENTRY-INTERPRETATION-v2.json` | `d3d7089c7a25f14109505cddb26066206d4f097e3be9feb536447f4a9879ec2c` |
| `rule-query-entry-review-v1/REVIEW-v1.json` | `54dd232d31355590c25f044e8cff6e1ddb55f714ffef607275f0953a667e2c67` |
| `rule-query-entry-review-v1/supplement-v1/REVIEW-SUPPLEMENT-v1.json` | `b81e69c3512bf088b2388d3c16ed9c8679aefcf455b62f2d828e6d8c515a33a0` |


## Stored counters, ancestor collection and entry rejection

A concrete storage interpretation now connects the query's counter observations
to the existing valid-history invariant. Its sequence update laws, constants,
encoded slots and current getter endpoint are proved. The stored raw hash history
is normalized before use by the packed query. Membership of a hash emitted by an
ancestor's provider policy follows from the stored chain and accounting invariant.

The extracted ancestor collector and packing function now compose with this
history and the actual query-entry predicate. Pointwise observation of the three
complete packed words determines masking and reconstruction of the fourth hash;
those results are proved rather than separately assumed. A nonzero raw word can
have zero low bits, so raw-word emptiness and normalized membership stay distinct.

The guarded run rebuilds five modules with 29 audited declarations and checks
five compiled negative controls. They reject shifted reads, shifted updates,
a future getter endpoint, unnormalized history and a future entry context. The
getter control uses a locally opaque encoding definition in both a successful
positive compilation and its failing mutation, avoiding a resource-limit failure
as evidence. Five diagnostic controls reject unrelated compiler failures.
All inputs and complete listed lookup directories are authenticated before and
after execution, and the collector checks 98 output files against exact commands,
source mutations, diagnostics and theorem inventories.

The collector theorem and two final composition theorems retain the inherited
`core.fmt.Formatter` dependency. Other axioms are limited to `propext`,
`Classical.choice` and `Quot.sound`. Native proof records, Aeneas generation and
dependency objects are cached. Independent review checked the collector adapter,
storage composition and guarded runner within their stated scopes; the latest
runner review does not claim a second complete replay.

Remaining premises include the live storage invariant, the collector's hash
membership policy, observation of the Rule's packed hashes, the current-entry
filter relation and the Option call's normal-return postcondition. This chosen
storage interpretation does not prove allocation identity or the complete native
library. The next steps derive the collector policy from a successful native
match and bind the Rule's hashes to the same selector and quirks used to create
it. Public Rule mutation and stylesheet generation still need explicit lifecycle
reasoning. Milestones 4 and 6 remain open.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `packed-query-composition-v1/STORED-COLLECTOR-COMPOSITION-v1.json` | `ffe9c5a9cd97e6cbec5adb5afe93178cfeee75eaba880fbf75be70009e8d690e` |
| `packed-query-composition-review-v1/COLLECTED-PACKING-PROTOTYPE-v1.json` | `1ef9a579434bdc027460632cdcd1d97fed8c2c85a1b1cff4d2a84404fbdc6940` |
| `packed-query-stored-review-v1/REVIEW-v1.json` | `706c7be7620d16d1048e52b9bd37712e9833cd12493b42052a00b6a83b04ca58` |
| `packed-query-gate-review-v1/REVIEW-v1.json` | `8d3ae8adb7ecf884dadeaeef28c2c5c2117f104fba8cad08263417a28aff0245` |


## Successful matching and recovered storage at query entry

The collector's hash-membership premise now follows from the successful native
matcher contract in the local-name/Child domain. The proof transports its
ancestor witnesses through selector slice correspondence and name/provider
alignment, then uses the stored chain and accounting invariant. A second lemma
composes this result with the actual query-entry predicate. Both compile against
the accepted stored-collector objects. Three semantic controls reject an
unsuccessful matcher result, membership of the subject instead of the ancestor,
and the subject's provider instead of the ancestor's provider.

The next composition removes the separately assumed ancestry membership and
final live-history premises. It interprets matching ancestry through
`ParentMatcher.withParentChain`, uses `ParentEmbedding.member` for distinct
matching and traversal parents, and applies the complete recovery outcome to
derive rootedness and live history at the final storage endpoint. The concrete
`EntryStorage` dictionary supplies proved constants and sequence laws.
The final recovered filter is the exact filter required at query entry; the
complete matcher-context return frame is also retained.

A guarded run freshly rebuilds these two composition modules, checks their two
exact axiom audits and runs four semantic controls. Reversed parent embedding,
a rooted chain missing its subject, the old filter at entry and missing initial
history each fail the intended theorem. The gate authenticates all listed inputs
and lookup directories before and after execution and checks 41 output files.
Native proof records, model generation and dependency objects remain cached.
Independent review checks the source, premise transport and gate within this
scope; it does not claim another complete dependency replay.

All four new theorem audits retain the inherited `core.fmt.Formatter` dependency,
with only `propext`, `Classical.choice` and `Quot.sound` otherwise. Initial
validity, history and resource conditions, record/pending contracts, actual
parent-edge embedding, atom/hash policy, selector representation, Rule packing
observation and the current-entry filter relation remain explicit. Independent
matcher and entry dictionaries, selector and quirks identities, and caller
transport are not silently identified. Milestones 4 and 6 remain open.

The next gates bind Rule construction and packing to the same selector, then
instantiate atom identity/hash and concrete parent/caller observations. A proof
under these explicit relations is not yet the complete implementation result.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `matcher-storage-composition-v1/MATCHED-COLLECTOR-PROTOTYPE-v1.json` | `8a53d27fcb7be5ad173ab641174e2c9b865344c12c6516b9c85226b15eb4cf69` |
| `matcher-storage-review-v1/REVIEW-v1.json` | `c229d90dafe9729c9a17bd840139a39ac59713fcc7807d389ac5a625dc82187b` |
| `recovered-entry-composition-v1/RECOVERED-ENTRY-COMPOSITION-v1.json` | `5e1b26a770a8032c05d291677ae70e0c1e12647143a50cde1eac10c76c7b63a0` |
| `recovered-entry-review-v1/REVIEW-v1.json` | `0033cd3732c1dafa4dc29bdd61de99a994547a97c50db2bdc41bb3be8c757896` |


## Native rule construction and atom/provider membership

The native rule-origin checkpoint now covers the unchanged constructor, bucket
setter and hash packing bodies. Its 31 fresh solver obligations pass. The typed
bridge preserves all rule fields and derives packed-word observations from the
native packing input, exact count value and full constructor postcondition.
The bucket setter preserves the selector/hash pair. Public field mutation,
stylesheet generation and the relation to the matching selector remain separate
obligations; this is not a global rule invariant.

The guarded typed run rebuilds six Lean modules with thirteen axiom audits,
replays nine exporter commands, and checks seven semantic, eight malformed
export, six binding and five diagnostic controls. Five physical evidence controls
reject missing, changed or forged outputs. The root independently reconstructs
the collector report and authenticates the frozen package. Native proof records
remain cached for this typed run. The thirteen theorem audits use only standard
Lean axioms; pair-preservation lemmas are axiom-free.

A separate atom/provider composition interprets the unchanged native `policy_E`
definition, retaining the identity/hash fields and atom wrappers. Concrete
sequence operations, nonnegative mapped lengths and exact bounded observations
establish that the local-name hash is in the provider history. A shared coherent
atom hash table then derives matching-name membership. This discharges the
previously supplied membership callback in the recovered-storage/query theorem.
The fixture's independent identity/hash fields do not imply equal hashes from
equal identities alone; its checked countermodel is not a Firefox defect.

The atom composition freshly rebuilds four modules with eight axiom audits.
Eight semantic controls include a typed native-policy mutation that swaps the
first two hashes while preserving the dictionary interface. Nine malformed
export controls, five diagnostic controls and six physical evidence controls
also pass. The gate checks 92 output files and authenticates inputs and complete
listed lookup directories before and after execution. Independent bounded
review reproduces the four-module proof and native hash-swap control.
A separate review reconstructs the revised collector report and independently
replays all six physical evidence controls; it does not repeat the full gate.

The first atom gate remains rejected: its collector did not require exact
validator/diagnostic inventories and imported the parent's diagnostic parser.
The second version loads the intended parser explicitly, pins complete control
records and rejects reindexed duplicate inventories. These corrections do not
change any proof proposition.

Only the final atom/recovery composition retains `core.fmt.Formatter`; the other
atom lemmas use standard Lean axioms or none. Native local-name/hash and matching
identity bindings, selector hashing, coherent atom observations, sequence/list
representation, resource conditions and the prior recovery/query contracts remain
explicit. No local-name native contract was exported. Source observations support
the intended Gecko bindings without proving the C++ atom table.

The next composition connects these two packages and removes the packed-word
observation premise. Actual collector input/count correspondence, the same
selector and quirks at construction and matching, and caller lifecycle remain
the next gates. Milestones 4 and 6 remain open; there are still two confirmed
Firefox bugs.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `rule-origin-native-v1/NATIVE-RULE-ORIGIN-v3.json` | `46b438cec4f4272684b93555423479718a2c8955241c16aa2bc214c77af13ac8` |
| `rule-origin-translation-v1/RULE-ORIGIN-INTERPRETATION-v1.json` | `9b208fe019072e4b9c3f1fe1696c37c98a49c96e35287609f18bed88cbd7c07e` |
| `atom-provider-binding-v1/typed-policy-v1/ATOM-PROVIDER-COMPOSITION-v1.json` | `a0b0f852d38a12b5dd23f92ee97cc22d72206a69fd6705111f791d7c93700c98` |
| `atom-provider-review-v1/REVIEW-v2.json` | `5e504b2601adc03486d0150e4fd837f4fb6ec13713f0ebd9ef4e777f69fb1d10` |
| `atom-provider-review-v1/GATE-REVIEW-v1.json` | `b8fbb2ca27ab2e1c81e5ae943f8511d00b1f35dd94c0701c6014f2de6b220778` |


## Actual ancestor-hash construction and local-name contract

The next composition replaces the explicit collector-output, hash-count,
native-input-word, native packing-postcondition and packed-observation premises
with the actual extracted `AncestorHashes::new` return. Its decomposition proves
that a successful constructor return is the result of the same collector and
packer. Conversion retains all three packed words, and the native `Rule::new`
postcondition connects those words to the stored rule.

The isolated native extraction adds one wrapper calling the unchanged
constructor. The source audit checks exact wrapper/path adaptation, captured
parser and packing source, transparent selected bodies and source spans. Its
replay regenerates normalization and Aeneas output, recompiles three modules with
seven audits, and checks five semantic, seven source, five diagnostic and five
physical evidence controls. Existing ownership/library models remain explicit;
the replay authenticates the cached Rust extraction instead of repeating it.

The local-name bridge exports the complete captured `postcondition_fndef` law
and `postcondition_once_local_name` definition from the unchanged native model.
The complete canonical task and theory match the accepted policy export. The
law is rendered as a proposition supplied by the caller, not a Lean axiom.
Its return postcondition and a shared native-symbol dictionary derive the local
hash equality used by the provider proof. Both atom identity and hash fields are
preserved. This verifies contract transport; the Gecko accessor body and atom
table remain outside the proof.

The combined guarded replay freshly rebuilds eight modules with fifteen exact
axiom audits. Eleven semantic controls cover the accessor, collector/packer,
rule hash association, quirks mode and query result. Eight malformed-export,
six shared-symbol and five diagnostic controls also pass. Seven physical
evidence controls reject duplicate inventories, altered native inputs/commands,
missing proof objects and unexpected files; every copied baseline first passes
the collector. The run checks 135 outputs. The complete listed dependency
lookup is authenticated before and after execution. The four local
accessor lemmas are axiom-free; the final composition retains the existing
`core.fmt.Formatter` abstraction. Independent bounded review reads the complete
composition and reproduces the collector report exactly. It checks the seven
recorded physical controls without repeating the full proof run or transitive
dependency authentication. No semantic blocker was found.

The resulting theorem preserves the matcher context and proves that the
recovered entry query does not reject. It still assumes the observed selector
and matcher slice correspond, the relevant constructor and accessor return
normally, and the earlier DOM, atom coherence, storage, resource and query
contracts hold. Native rule/collector/matcher selector identity and stylesheet
and quirks freshness remain separate obligations. This is not a global invariant
for publicly mutable rule fields.

The next production bridge follows the post-replacement selector through
`AncestorHashes::new`, `Rule::new`, and the `BucketMatches::Unknown` matching
entry. The `Subject` shortcut needs a separate iterator-offset relation. A
normal `Stylist::flush` return alone is insufficient evidence of current hashes:
the rebuild allocation-error path is caught, so the lifecycle obligation must
state successful per-origin rebuild/freshness. No browser defect is claimed from
that observation. Milestones 4 and 6 remain open; there are still two confirmed
Firefox bugs.

Paths below are relative to the public-entry prototype's
`provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `collector-origin-bridge-v1/COLLECTOR-ORIGIN-PROTOTYPE-v1.json` | `c8eaefa8831245c1defa0ff5012a5490781d35246b385ac279c4a3d792dab8da` |
| `native-constructed-recovered-entry-v1/NATIVE-CONSTRUCTED-RECOVERED-v1.json` | `77b95a9aca0fd273e466ec37f134f3398a2466322085a53eb97c3baef0d8115d` |
| `local-name-contract-review-v1/REVIEW-v1.json` | `e6f93c03e3a383520625e6b1e28a4fbccea19a932e957f4188e21cbbdc7754dd` |
| `native-constructed-recovered-entry-review-v1/REVIEW-v1.json` | `a236d770a25418a696eb54052c245cc069f9d17b9b83fbefb0178f4e4dbfcd81` |


## Selected rule and native iterator composition

The next checked composition follows the actual extracted rule construction,
retains all nine returned fields, and uses that rule's selector and packed
hashes in the recovered query. The native iterator's complete postcondition
connects its component view to the same selector and establishes the initial
empty combinator. The Lean bridge derives the previous iterator correspondence
from this postcondition and an explicit same-selector storage observation.
All thirty component variants and their payloads are retained; both component
conversions are inverses, including the `Part` and `Has` slice representations.
Matching semantics remain restricted to the local-name/child domain.

The guarded run regenerates the typed model and freshly checks six modules with
seventeen exact axiom audits. Ten semantic mutations, six malformed typed-input
checks and two well-typed contract mutations pass their rejection checks. The
113-output inventory and all listed dependency lookup trees are authenticated.
Native extraction and solver evidence are cached and authenticated; this run
does not repeat them. The actual native iterator has two successful solver
obligations under its raw-iterator contract. Its two COMA sensitivity controls
leave the intended postcondition unproved; timeouts are not counterexamples.

Independent review found an evidence-integrity limitation in the first auditor:
a reindexed change to a compiled proof object passed an existence-only check.
The fresh proof run itself remained valid. The revised auditor authenticates
a separately pinned original producer report and requires exact bytes for all
six positive and two typed-control proof objects. Eight physical output controls
and a forged-reference control pass. Independent bounded source and collector
reviews accept the correction; they do not claim an independent full proof or
transitive lookup rerun. The failed auditor and its reproducer remain recorded.

The final theorem preserves the matcher context, proves no Bloom rejection and
retains the actual returned selector and iterator identity. The raw iterator
contract, same-selector Arc/HeaderSlice observation, DOM ancestry/stability,
provider and atom coherence, query, library and resource assumptions remain
explicit. No allocation-identity, general rule-field mutation or stylesheet
freshness invariant is claimed.

Ordinary `section > span` uses the `Subject` bucket after selection. A separate
native checkpoint proves its iterator advancement and actual caller obligations
(39 and seventeen respectively). A six-audit Lean bridge transfers ancestor
witnesses from the suffix to the full collector using exact shifted indices;
it needs neither successful subject-name matching nor prior Bloom acceptance.
The native Subject postcondition still needs to establish that suffix
representation before the complete production instance is accepted.

The differential test `local_name_child_has_nonzero_ancestor_contribution`
provides a concrete runtime check using the actual parser, ancestor collector
and matcher. In its two-node mock DOM, `section > span` matches without a filter,
an empty filter rejects, and inserting only the parent-name hash restores the
match. The deterministic test provider returns raw hash `0xfcdd0ccc`, producing
packed words `[0xdd0ccc, 0, 0]`. The targeted optimized test, formatting and lint
checks pass. This is a nonzero runtime witness for the mock provider, not Gecko
atom, Subject-bucket or recovery evidence. A consistent nonzero formal instance
and the Subject coupling are next. Milestones 4 and 6 remain open; the broader
combinator, `:is()`/`:where()` and relative-selector obligations remain in scope.
There are still two confirmed Firefox bugs.

Paths below are relative to the public-entry prototype's `provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `iterator-selected-gate-v1/SELECTED-ITERATOR-COMPOSITION-v1.json` | `3c23bd988ecef6a838011ce41c355d38471a3b0da16988922156e504289894c6` |
| `iterator-selected-review-v1/REVIEW-v1.json` | `46f8bbc02248ecb968873dd25e93d88202bd32bc2af033a60f59568ecad3f61b` |
| `iterator-selected-gate-review-v1/REVIEW-v2.json` | `3ca1313582202a0383a70d461e69f0853b9d66b6bc3f81ec7f04c646a66cf3bb` |
| `rule-subject-callsite-v1/NATIVE-SUBJECT-CALLSITE-PROTOTYPE-v1.json` | `aa43c04571edfc44e29aa0b4d9859b26eaadb756da67194b64df70371462813a` |
| `subject-collector-bridge-v1/SUBJECT-COLLECTOR-PROTOTYPE-v1.json` | `443841fa0f71f035e7e6b351f4894e1a580bdb97ac722db3b3d9ea5a17a705e1` |


## Native Subject contracts and a concrete collector result

The native Subject helper's complete pre/post now supplies the full-selector
prefix and returned-suffix correspondence. The interpretation preserves all
seven precondition and six postcondition conjuncts, the complete context and
borrow records, and all component payloads. Its bounded sequence interpretation
proves the exact `[1..3]` length/index contract. Thirteen theorem audits, six
compiled semantic controls and six schema controls pass. An independent fresh
two-module build reproduces the original proof objects and axiom reports.

A separate three-module composition has four passing audits and five compiled
controls. It combines this helper contract with prospective suffix matching,
recovered ancestor storage, the actual hash constructor and the full rule
constructor postcondition. The rule constructor uses the helper selector's
carrier. The conclusion preserves both context frames and the selector, and
proves no rejection by the recovered filter. Root review freshly rebuilt these
modules and reproduced their proof objects and reports. Neither review reran
the native solver or rebuilt inherited proof dependencies.

The concrete `SectionSpanWitness.constructed` theorem now checks the extracted
collector and constructor for the explicit `[span, Child, section]` selector.
It returns exactly one collected hash, `0xdd0ccc`, and packed words
`[0xdd0ccc, 0, 0]`. The primitive section hash is `0xfcdd0ccc`, matching the Rust
fixture. Twelve audited declarations and four compiled controls pass; changing
the name hash, boundary, collected contribution or packed value breaks the
expected proofs. The package authenticates its accepted parent dependency pins.
Unused primitive operations diverge, but the proved normal return establishes
that this collector execution never calls them. This does not establish
readiness of those operations for a different execution.

The complete instance remains open. The next obligation is successful actual
native suffix matching on the same finite DOM, followed by a concrete recovery
trace from initialized storage and the helper/matcher/query endpoint maps.
Independently chosen successful postconditions do not establish these calls.
A joint interpretation must satisfy the full preconditions with a nonzero
ancestor contribution. The concrete collector result is not a parser-refinement,
Gecko-atom, native matcher or recovery witness. Milestones 4 and 6 and their
broader selector obligations remain open; there are still two confirmed bugs.

Paths below are relative to the public-entry prototype's `provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `subject-contract-translation-v1/SUBJECT-CONTRACT-INTERPRETATION-v1.json` | `5b0474d9bbad62fe1dbc769124778fd60683b07139db32a23ca4324caf1d0556` |
| `subject-recovered-query-v1/SUBJECT-RECOVERED-QUERY-PROTOTYPE-v1.json` | `6ae97965287d73ca4ac30b2544d78bde7577a24a33c67b073f366cb2e778c368` |
| `section-span-witness-v1/SECTION-SPAN-WITNESS-v1.json` | `9bbdb1be7d7d10b198c4a42d57c92938e4a3dbe2c371bf3e0628751d7758f702` |
| `subject-instance-plan-v1/PLAN-v1.json` | `3321856a72b43b322388d62413d6f7ac5a08ccbb66cd9aa3c146349d1effed85` |

The independent root review records are under `artifacts/stylo-bloom-tools`:
`subject-contract-root-review-v1/ROOT-REVIEW-v1.json` has SHA-256
`e7c3f9143eeae7bee2c6820ca02500d787ba38ca08940cb053c16b489e7bbdad`;
`subject-recovered-root-review-v1/ROOT-REVIEW-v1.json` has SHA-256
`49fc175b764606e3bdb091d137d380db24f73fdb43de5d560fa11f26e240adca`.
## Concrete native matching and recovery interpretation

The finite native Subject wrapper now has a bounded checkpoint. It calls the
actual subject helper and suffix matcher for `section > span`; checked converse
contracts carry matching names through their unchanged runtime bodies. All 588
obligations across the 57 emitted models pass. Four compiled controls each leave
one intended obligation unproved while the other six pass. These are sensitivity
checks, not discovered counterexamples.

The same wrapper runs against the concrete two-node mock and production parser.
It returns True for the section/span pair and False for a wrong parent name or a
root target. Source checks distinguish the two runtime-only adaptations from the
checked proof annotations. The root replay reproduces the evidence collector's
report exactly and authenticates all 530 package pins. This does not instantiate
every native logical primitive, prove termination for arbitrary trees, or
rebuild the cached compiler and library dependencies.

A separate concrete recovery interpretation now proves the selected full
recovery precondition and postcondition from initialized storage. Its insertion
trace includes each intermediate borrowed state and all final filter, vector and
count endpoints. A first draft retained only aggregate insertion effects; that
weaker draft was not accepted. The replacement exports both native trace
predicates through Why3's typed AST and proves definitional equivalence with the
specialized interpretation. Five Lean modules pass 44 axiom audits; four recovery
controls, seven trace mutations and four schema controls pass their rejection
checks. The bounded manual formula review covers every trace conjunct. Independent
replay and review of the new generator and query extension remain pending.

The recovered section hash sets two counters to one. The generated packed query
accepts the actual nonzero collector output against this filter and rejects the
empty filter. The option postcondition follows from that query and the caller's
closure and filter invariants. This is a logical contract witness, not an
observation of native recovery execution. The snapshot storage dictionary still
needs a full treatment of native field borrow lifetimes and shared final values
before claiming a joint model of the complete native call sequence.

The next gate connects the concrete Subject, matcher, recovery, constructor and
query interpretations using one selector, DOM and complete context/cache endpoint
mapping. Actual execution evidence and logical contract inhabitation must retain
their separate scopes. Milestones 4 and 6 remain open, as do the broader selector
obligations; the confirmed production bug count remains two.

Paths are relative to `provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `subject-instance-native-v1/NATIVE-FINITE-SUBJECT-EVIDENCE-v1.json` | `378217c812eaa7cf31f4fd59ac4d790308ba3a7fa1df9b4a14a86f5232813131` |
| `section-span-recovery-v1/SECTION-SPAN-RECOVERY-v2.json` | `3d05d6e4cf38ca37e5cf67921ab32dfe0f74135787eb2795fa75a1af1ae74958` |
| `section-span-recovery-review-v1/REVIEW-v1.json` | `00ce405d8092dd2861a1814dffd2a41c62033fa1e7f3a1493738e26c691900a9` |

## Borrowed storage and the concrete Subject composition

The concrete Subject composition now connects the full helper and matcher
contexts, constructor, bucket setter, recovered filter and packed query.
Its eighteen audits and six mutation controls pass. Independent compilation
reproduces its source, object and audit output exactly using cached imports.
The recovery interpretation also received independent replay: all five modules
and 44 audits reproduce exactly. Neither replay rebuilds the entire dependency
chain or reruns all inherited controls.

The selected storage interpretation now represents all four native fields as
borrows, retaining current values, final values and identities. Its filter
invariant checks both endpoints. Full constructor, push and recovery contracts
hold, and the existing composition accepts this dictionary. Five modules pass
45 axiom audits. Six endpoint, identity and early-resolution controls fail at
the intended theorems; a malformed future filter fails its invariant.

The actual insertion provider's typed `advanced` predicate retains all seven
clauses, including both future endpoints. Exact generated equivalence and the
complete insertion trace hold for the same selected sinks. Seven clause-deletion
controls fail the definitional binding; four malformed schemas are rejected.
These check translation completeness, including clauses that are redundant in
this fixed-capacity interpretation. The earlier snapshot sinks fail the future
filter requirement. This is a witness-model limitation, not a new Firefox bug.
Independent source review includes exact regeneration of the typed predicate;
independent replay of this new five-module package remains separate work.

An ordinary Rust fixture also executes the copied native rule constructor,
Subject setter and matching entry with the production parser and hash collector.
The populated filter accepts; empty and wrong-hash filters reject. It directly
inserts the hash and chooses the bucket, so this is not execution of recovery or
proof of bucket classification. A deliberately unjustified Subject bucket shows
why that classification remains a required caller obligation.

The next gate joins native Subject dispatch to the independently derived query
result, preserving one rule generation, selector suffix and current filter.
Then the terminal scoped theorem and generic recovery branch inventory can be
reviewed. Milestones 4 and 6 remain open, including the later selector families.
Complete unsafe-library semantics and allocation-enabled termination remain
explicit extensions of the conditional normal-return result.

Paths are relative to `provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `section-span-composed-v1/SECTION-SPAN-COMPOSED-v1.json` | `964aaff410889b4719f69b9d253b201b355bcf8e97c865aef6343bf246079a0d` |
| `section-span-recovery-review-v1/REVIEW-v2.json` | `2062062d49fa73e0cc91f36c0ece6e20c1ea3a29dde152b12f0202f3fdab6e27` |
| `section-span-storage-borrows-v1/BORROWED-STORAGE-INSTANCE-v1.json` | `031c29d345b1f4d92e2ea4be20a8e3c08cd1f81d6e7da4cff81a6e5681781350` |
| `section-span-storage-borrows-review-v1/REVIEW-v2.json` | `664796dd3324c8927f28e4609b3466b6b99802f5946a0f582568e921c85c5eda` |
| `section-span-rule-runtime-v1/RUNTIME-EVIDENCE-v1.json` | `7641f4c0dd85d7b93fbeadb25ec376ae3625ded839c71271ee930a0200f6cd3f` |
| `milestone-exit-review-v1/ASSESSMENT-v1.json` | `1a7ae4d291fa39bb76e396a6e43a0bd46eead3ef71c88ef649c24f760bfea5c0` |

The independent composition replay is recorded under
`artifacts/stylo-bloom-tools/section-span-composed-root-review-v1/REVIEW-v1.json`,
with SHA-256 `e0d9ce1940b5f01222960629d7397ac82c5c357a42538070a60c268a69dbb729`.

The storage package's v2 acceptance supersedes its v1 reusable collector.
Independent review found loose control inventories and diagnostic checks;
a separate strict audit confirms that all recorded failures were genuine.
The revised collector checks exact mutations, inventories, execution provenance
and semantic diagnostics. Fourteen corrupted-evidence controls are rejected.
The proof sources and 45 audits are unchanged. The v2 capsule is
`section-span-storage-borrows-v1/BORROWED-STORAGE-INSTANCE-v2.json`, SHA-256
`55a53cae6dc84e23e1bf1c748b04ae307e71e85ce8b0867c536df67104cc9b04`.
The independent strict snapshot review is
`section-span-storage-borrows-review-v1/REVIEW-v3.json`, SHA-256
`75aaa31b7c825f9a65d068f439dea5eb4f0fa292889f58a2ebb6ca8b34f72f9a`.
## Selected matching without Bloom filtering and recovered acceptance

The section/span composition now states the first comparison directly:
normal return of the checked native Subject route without a Bloom filter yields
True, and the independently computed query accepts the recovered filter's
nonzero ancestor contribution. The selected rule, selector suffix, subject and
hash generation are shared. The dispatch result does not supply the premise
used to prove query acceptance.

The full storage constructor, rule constructor, Subject setter, recovery and
provider contracts hold in the same selected interpretation. For an arbitrary
final matching context, the native postcondition derives restoration of the
complete entry context. This is a composition of normal-return contracts and a
coherent instance, not a recording of physical recovery calls. Stable finite
DOM and name/hash observations, immutable selector views, library interpretations
and resource assumptions remain explicit. The package README lists them.

The native dispatch extension checks all 57 models and 588 obligations, retaining
the existing full context frame. Its three compiled mutations each leave the
intended postcondition unproved and the other sixteen obligations valid. The
typed interpretation preserves all eighteen context fields, nine rule fields
and cache borrow endpoints. An independent fresh compilation reproduces its ten
Lean audits, source, object and output exactly using cached dependencies.

The terminal module passes thirteen audits with only standard Lean logical
axioms. Five source mutations fail at the expected proof obligations: wrong
recovered filter, unexpected empty filter, swapped entry endpoint, wrong returned
result and false empty-filter acceptance. The acceptance collector checks exact
source mutations, commands, environments, ordered inventories and diagnostics;
sixteen corrupt-report tests are rejected. Independent source review covers all
thirteen statements and proofs. A complete dependency rebuild is not claimed.

A separate Rust fixture now includes the entire production bucket classifier
bodies, including branches outside this selected case. Actual parsing,
classification, rule construction and dispatch accept the populated section/span
case, reject empty and wrong-hash filters, and skip a rule with the wrong subject
bucket key. It also exercises a descendant selector. The fixture directly
inserts the hash and models selected local-name key lookup; full SelectorMap
classification, lookup and cascade are not formally proved. Its descendant
observation does not establish the descendant matching-to-region theorem.

The generic M4 inventory identifies the existing provider-to-push-to-recovery
maps. Recovery consumes the checked aggregate counter, hash, record and historical
high-water clauses; the native insertion trace is additionally retained. Final
aggregate acceptance remains separate from this finite instance. M6 still needs
composed results for descendant combinators, IDs/classes, attributes/namespaces,
`:is()`/`:where()` and relative selectors. There are still two confirmed Firefox
bugs.

Paths are relative to `provider-bindings-v1`:

| Record | SHA-256 |
| --- | --- |
| `native-subject-dispatch-v1/NATIVE-SUBJECT-DISPATCH-v1.json` | `cd67123a0cbad14e4650c60461799d82b144b333aec02b38e1eb3b731023ae72` |
| `native-subject-dispatch-v1/translation-v1/SUBJECT-DISPATCH-INTERPRETATION-v2.json` | `aecb25f3753004f6e9c32caf1dc5e9d1c00f473d0351694d2975c93f0145dead` |
| `section-span-terminal-v1/SECTION-SPAN-TERMINAL-v1.json` | `2617308c8e0a470e8d21ae3c59bb9eecc4320f1a04511dbdc3d5a328e0746d70` |
| `section-span-terminal-review-v1/REVIEW-v1.json` | `111fced16b8d3dbd56c95ce3d9d6863869a24b851b6adc04f7da680b65de6c02` |
| `section-span-bucket-runtime-v1/BUCKET-RUNTIME-v1.json` | `e6092c3d52dc77f05a87aaaa07015a6793d13fe69da489e51e68520ebb9ff2db` |
| `native-provider-recovery-map-v1/INVENTORY-v1.json` | `160eff7fcf4cffe45d14c1d174ff9942a816aea740d3df21d1f59cb4b6d37328` |
