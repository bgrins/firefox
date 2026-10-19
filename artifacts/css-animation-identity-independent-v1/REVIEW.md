# Independent animation identity review

## Verdict

**ACCEPT the conditional identity/readiness/map/constructor model component.** No substantive defect found in the stated claims. Root owns final acceptance. This does not accept numeric animation values, all caller/provider behavior or the concurrently prepared keyframe-substitution candidate.

## Authentication and fresh replay

Authenticated all externally supplied FREEZE, MANIFEST, checker and REPORT pins before executing/importing code. All 34 inputs match a closed file/directory roster, safe confined paths and unique JSON keys; no symlink/nonregular inputs were admitted. The independent relocation contains only manifest-listed files and the two seals.

Fresh isolated replay compiled all five modules from source in a new external directory. The exact 49-name axiom inventory matched: **26 general lemmas, two concrete-provider contract proofs and 21 concrete kernel examples**. Only standard Lean `propext`, `Quot.sound`, and `Classical.choice` are permitted. All nine integrity controls passed. Commands, exact axiom output, result, guards and additional elaborated type checks are retained under `evidence/`.

I read all five full Lean modules, all 15 complete source bindings, the historical static report, source/scope documents, replay and guard scripts. General theorems have no payload equality assumption; a fresh elaborated type check confirms compose_ready has no equality typeclass, and map/constructor results require decidable equality only on identities.

## Readiness and all composition paths

`Preserves` is an explicit successful-arithmetic premise: matching operand identities imply the same result identity when arithmetic returns Some. It does not assume success, expected payloads, the final composed value or final map coherence. The always-failing and left-result providers are proved to satisfy it, showing both failure and success domains are inhabited. Arbitrary mismatched native arithmetic inputs are not made safe by this theorem.

The outer and inner Options are meaningful. Outer None exposes unavailable native unwrap/expect inputs. Some None represents an ordinary arithmetic failure or no composited replacement, allowing selection to retain the original endpoint. Those outcomes are not conflated.

| Branch | Checked correspondence |
| --- | --- |
| Missing endpoint | Uses underlying value; derived endpoint readiness makes the eventual selection present. |
| Present endpoint, replace | No composited replacement; original endpoint remains ready. |
| Present endpoint, add/accumulate | Underlying presence is required and derived from need; arithmetic can fail, leaving original selection. |
| Iteration inactive or count zero | No last-value requirement. |
| Active iteration | Uses last endpoint, falling back to underlying only when last is absent; guard_last derives presence. |
| Accumulate with composited value | On arithmetic failure, retains that composited value. |
| Accumulate without composited value | Original endpoint readiness is proved before the modeled unwrap; arithmetic failure leaves original endpoint selection. |
| Equal segment keys | Chooses from/to by total-progress sign, with no interpolation. |
| Nonzero segment interpolation | Successful arithmetic preserves identity; failure chooses the appropriate endpoint by the half-progress branch. |

The model's need disjunction matches the retained map wrapper: either endpoint absent, either endpoint mode non-replace, or active accumulation with absent last endpoint. In `step_ready`, the missing-underlying early return is handled first. Passing that branch **derives** `need → underlying.isSome`, which is then used by guard_endpoints and guard_last. This is not an assumed readiness label at the map boundary. Existing map values take precedence over base. Missing required base preserves the entire map; invalid/nonanimatable identities also preserve it.

The lower-level compose_ready theorem appropriately takes this guard as a premise. The direct Servo_ComposeAnimationSegment wrapper lacks the map wrapper's guard and therefore has an external caller readiness contract. No universal safe-direct-call claim is made.

Native source updates both composited endpoints before selecting either final value; the model combines each endpoint's update and selection. Under pure provider functions these have the same value dependencies. No trace-order, effect, callback, timing or exception equivalence is proved.

## Identity and finite-map proof

ActionId constrains admitted segment endpoints, last endpoint and base values to the owning key. It does not constrain rejected actions' unused values. This is a real input/provider premise, not a derivation from native grouping. It is also a sufficient contract, sometimes stronger than necessary: for example an unused base is still constrained for an admitted action. No minimal-premise claim is made.

Lookup identity follows from coherent map entries. Insert removes prior same-key entries and adds the coherent result; coherence and unique keys are proved preserved. The finite-history induction permits repeated update keys and arbitrary payloads, including failure/fallback paths, and starts from a proved empty-map invariant. It does not assume the desired final map is coherent. The list represents an abstract finite map; prepend/filter order is not asserted to equal native HashMap iteration order.

The existing numeric custom-keyframe substitution defect can coexist with this identity theorem: an incorrectly computed payload may still carry its correct property identity. This review does not certify payload substitution or interpolation correctness.

## Separate constructor proof

The constructor loop appends `uncompute(value)` to declarations and inserts the **map key** into a separate membership representation. The two identities are not defined equal. loop_storage derives both fields for arbitrary initial storage. Constructor identity uses map coherence plus the explicit identity-preserving uncompute premise; unique enumeration yields unique declaration IDs. An independently constructed false importance vector has exactly declaration length. Membership agreement is bidirectional, all bits are normal, and mutable=true correctly represents native immutable=false.

Counterexamples show that removing coherence, uncompute preservation or key uniqueness can violate the result. The membership list models set contents; duplicate-free native enumeration and native container semantics remain admissions. No theorem of native map enumeration order, allocation capacity or a mapping into the earlier PublicStorage implementation is claimed.

## Source/provider review and historical binding

Fifteen complete function records are regenerated and checked from frozen full source snapshots. The generated animate template checks longhand tags and writes the original tag on success; custom animate checks names, propagates payload failure and preserves the name. Clone and uncompute preserve tag/name through inspected branches. A missing CustomAnimatedValue payload still has a name and uncomputes to an initial custom declaration; it is not the absent animation-endpoint case. from_declaration physically normalizes logical IDs before computed keyframe identity extraction. These are source arguments conditional on generated layouts and provider implementations, not universal verified translations.

The historical glue.rs hash remains `f850eec636e6740d5582c1dcea66f69f8b50c59f8f576167e2bcab6fb080cf9a`. The capsule deliberately targets those bytes. During this review, root changed Servo_GetComputedKeyframeValues and exposed CustomAnimatedValue::from_computed. A separate read-only observation found 14 selected binding slices unchanged and the remaining from_computed slice changed only from pub(crate) to pub; its function body is identical. Whole glue.rs/value.rs hashes differ and are recorded in `evidence/LIVE-OBSERVATION.json`. This observation does **not** rebind the capsule to the candidate or accept its new provider behavior.

Segment grouping, computed entries, physical-ID conversion, base-cache association and selected/last segment ownership remain explicit source/caller admissions. The static source audit narrows them but does not prove a complete mutable write-set or aliasing invariant.

## Numerical, runtime and validation limits

- Branch results (equal keys, negative total progress, before-half) are arbitrary Boolean parameters; interpolation receives an opaque progress-bits Nat. Identity preservation does not prove floating comparison, NaN behavior, timing/easing, IEEE arithmetic or concrete bit representation.
- Iteration count Nat must correspond to native u64. Nonempty segment arrays, indices and non-NaN upstream grouping offsets remain separate obligations.
- Successful arithmetic identity, cloning, uncompute identity, generated unsafe discriminant/layout correspondence, atoms/name conversion and FFI key association remain admissions. Mismatched longhand tags may panic natively.
- Native HashMap/set/vector/bitvector semantics, normal completion, allocation, aliasing, compiler and standard library are not proved.
- The 21 examples are kernel witnesses, not compiled native semantic mutants or browser evidence. Native executions are zero.

Fresh guards genuinely altered model/tool inputs or closure: module/package shadow, modified executor, empty directory, FIFO, symlink, duplicate key, escaping path, and output inside the capsule. Each rejected before injected exit-88 code execution. The escaping-path mutation is rejected by the closed roster before external dereference; no claim is made that it separately exercises every canonical-path check.

No live native/WPT/Git/build/browser changes were performed by this reviewer. Run `python3 -I -S -B check.py` for independent evidence integrity. Full source replay is `python3 -I -S -B package/check.py --output NEW_EXTERNAL_DIRECTORY`, using the pinned Lean executable. Generated object files are excluded from the seal.
