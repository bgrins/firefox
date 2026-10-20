# Base-value metadata change detection and notification

## Result and scope

This component proves a local comparison/decision contract for the proposed `EnsureBaseStyles` repair. It is separate from endpoint-array replacement. Five modules (two unchanged imported definition modules, three new) contain **23 new audited results**: 17 laws and six concrete witnesses. The proof covers arbitrary finite new-entry lists, keys, payloads and primitive payload comparators. It does not assume attr-bit equality or payload-comparator reflexivity.

The repaired per-entry predicate keeps ordinary inequality and adds custom-value metadata comparison guarded by both nonnull pointers. The proof derives:

- The new scan is exactly original payload-change detection OR new-entry custom metadata mismatch.
- Every original payload-change decision remains true; an additional decision occurs exactly when the original scan was false and metadata differs.
- For any selected custom entry actually in the new list, an unchanged scan implies its metadata agrees with the old value under the same key.
- Missing old entries, stored nulls, internally missing custom values, ordinary properties and removed-only old keys have explicit boundaries and witnesses.
- UpdateProperties' modeled call decision is `propertiesChanged OR (targetPresent AND delta)`, taking account of the conditional comparison pointer.
- In an explicitly modeled scheduler, the selected new value's metadata reaches the retained sample after notification; when notification is absent, prior sample coherence plus the unchanged-scan theorem establishes the same metadata result.

The last result does **not** prove Gecko scheduling. It requires actual publication/sample selection and delivery/consumption of the restyle request. The model distinguishes rebuilding base storage from recomputing a retained sample. Its missing-check counterexample publishes the new base but leaves old sampled metadata in both taint directions. A forced tick hides the defect, matching the shape of root's diagnostic without deriving native behavior from that match.

## Meaningful negative controls

The `omit-metadata-check` mutation compiles the complete model plus an executable driver. It then produces four false observations: both metadata-only change flags and both immediate retained-sample taint checks. Six controls stay true: payload changes, ordinary-property filtering, forced resampling, removed-only old keys, null/null and nonnull custom GIV versus missing old value. This is a semantic difference, not a rejected syntax fragment or a proof compile failure.

The original removed-only-key witness is retained deliberately. The repair scans actual new entries and does not claim to detect removals. The observation theorem requires selected-new-entry membership; whole-map equality or arbitrary old-key preservation would be a stronger, unproved claim.

## Source and native boundaries

The source baseline is root's tested `02ffed21...` file, not the earlier audit's differently formatted full-file snapshot. Final candidate is `cee5ea60...`; the exact formatted patch and an explicit transfer from the reviewed draft are retained. The draft source/patch were reconstructed by reversing the observed line wrap and authenticated against the earlier external hashes after the proposal directory advanced; they are not claimed as an original draft receipt. The only formatter change is a line wrap in the pointer conjunction. The original accessor and endpoint fix are already present in this stacked context. No standalone native applicability claim is made here.

Fourteen complete function bindings cover the comparison, base producer, call site, nullable equality, attr accessor, composition context and request forwarding. SOURCE-MAPPING lists every model/native bridge. The bit comparison is source-matched, but bindings do not prove a compiler translation. Actual map enumeration/key identities, comparator representation, successful base providers, pointer lifetimes, target/context/animation/pres-shell readiness, queue coalescing and temporal observers remain admissions. In particular, a call to RequestRestyle is not by itself a proof of updated output.

The parent source review and runtime investigation are separate evidence. The initial root diagnostic reported four failures/four controls passing with successful forced resampling; this proof neither reruns nor independently certifies that browser result. Later paired native evidence must bind its own final source and tests.

## Replay and integrity

`python3 -I -S check.py --output NEW_EXTERNAL_DIRECTORY` authenticates a closed source-only roster, source bindings, exact imports, pinned Lean executable/library, exact theorem inventory/axioms, and the compiled semantic mutation. Use an externally authenticated FREEZE/MANIFEST/checker before execution. Outputs must be fresh, resolved and outside the capsule. The exact per-theorem axiom inventory contains only `propext` and `Quot.sound` (or neither); no proof holes, custom axioms or native_decide.

Canonical and manifest-only relocated replays, integrity negatives and development failures are retained in the sibling replay package. This is a bounded mathematical component with source correspondence evidence. It proves neither the whole animation model, full substitution/URL behavior, nor browser scheduling conformance.
