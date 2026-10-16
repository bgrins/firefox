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

The next priority is connecting the interpreted U8 transitions to each actual
abstract removal edge. Raw encoding, sequential non-underflow from live history,
and the complete native removal contract interpretation now compose under explicit
complete call witnesses. Establishing those witnesses for every actual native
pop step and validating the shared observer interpretation remain open.
The native filter reset now has conditional extracted endpoint correspondence.
The native storage reset path is now checked under its count/high-water and
library premises. Integrating its typed counter interpretation with earlier
storage observers and deriving the native count premise remain open. Linked-pop integration remains useful
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

The old roadmap is retained byte-for-byte because earlier reviewed evidence
pins its contents. Experimental packages and their toolchains remain local
artifacts; this file records their scope and reproduction entry points.
